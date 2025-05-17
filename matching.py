from pathlib import Path
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

# ------------------------------------------------------------------ #
# 1) Load embedding model
# ------------------------------------------------------------------ #
_EMBED_MODEL = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# ------------------------------------------------------------------ #
# 2) Text encoding (include date/time/location/salary)
# ------------------------------------------------------------------ #
_TEXT_COL_JOBS = [
    "job_type",
    "job_detail",
    "salary",         # เอา salary มารวมในข้อความ
    "province",
    "district",
    "subdistrict",
    "job_date",
    "start_time",
    "end_time",
]
_TEXT_COL_WORKERS = [
    "job_type",
    "skills",
    "start_salary",   # เอาช่วงเงินเดือนมารวมในข้อความ
    "range_salary",
    "province",
    "district",
    "subdistrict",
    "job_date",
    "start_time",
    "end_time",
]

def _encode_texts(texts: list[str]) -> np.ndarray:
    return _EMBED_MODEL.encode(
        [t if isinstance(t, str) else "" for t in texts],
        show_progress_bar=False
    )

def encode_job_df(jobs_df: pd.DataFrame) -> pd.DataFrame:
    df = jobs_df.copy()
    # เติมค่าที่ขาดและแปลงเป็น str
    for col in _TEXT_COL_JOBS:
        df[col] = df.get(col, "").fillna("").astype(str)
    # รวมข้อความทั้งหมดเป็นข้อความเดียวต่อแถว
    df["__text"] = df[_TEXT_COL_JOBS].agg(" ".join, axis=1)
    # สร้าง embedding vector
    df["vec"] = list(_encode_texts(df["__text"].tolist()))
    df.drop(columns="__text", inplace=True)
    # แปลงวัน-เวลาเป็น datetime เพื่อใช้คำนวณเวลาซ้อนทับ
    if {"job_date", "start_time", "end_time"}.issubset(df.columns):
        df["job_date"] = pd.to_datetime(df["job_date"], errors="coerce").dt.date
        df["start_dt"] = pd.to_datetime(
            df["job_date"].astype(str) + " " + df["start_time"], errors="coerce"
        )
        df["end_dt"] = pd.to_datetime(
            df["job_date"].astype(str) + " " + df["end_time"], errors="coerce"
        )
    return df

def encode_worker_df(workers_df: pd.DataFrame) -> pd.DataFrame:
    df = workers_df.copy()
    for col in _TEXT_COL_WORKERS:
        df[col] = df.get(col, "").fillna("").astype(str)
    df["__text"] = df[_TEXT_COL_WORKERS].agg(" ".join, axis=1)
    df["vec"] = list(_encode_texts(df["__text"].tolist()))
    df.drop(columns="__text", inplace=True)
    if {"job_date", "start_time", "end_time"}.issubset(df.columns):
        df["job_date"] = pd.to_datetime(df["job_date"], errors="coerce").dt.date
        df["avail_start"] = pd.to_datetime(
            df["job_date"].astype(str) + " " + df["start_time"], errors="coerce"
        )
        df["avail_end"] = pd.to_datetime(
            df["job_date"].astype(str) + " " + df["end_time"], errors="coerce"
        )
    return df

# ------------------------------------------------------------------ #
# 3) Build FAISS index
# ------------------------------------------------------------------ #
def _build_faiss_index(mat: np.ndarray):
    dim = mat.shape[1]
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(mat)
    index.add(mat)
    return index

# ------------------------------------------------------------------ #
# 4) Feature construction
# ------------------------------------------------------------------ #
def _feature_df(worker: pd.Series, jobs_subset: pd.DataFrame) -> tuple:
    sim       = jobs_subset["sim"].to_numpy().reshape(-1, 1)
    same_type = (jobs_subset["job_type"] == worker.job_type).astype(int).reshape(-1, 1)
    loc_match = (
        (jobs_subset[["province", "district", "subdistrict"]].values
         == worker[["province", "district", "subdistrict"]].values)
        .all(axis=1)
        .astype(int)
        .reshape(-1, 1)
    )

    # จัดการ wage difference
    if "salary" in jobs_subset.columns or (
        "start_salary" in jobs_subset.columns and "range_salary" in jobs_subset.columns
    ):
        if "salary" in jobs_subset.columns:
            job_pay = pd.to_numeric(jobs_subset["salary"], errors="coerce").to_numpy().reshape(-1, 1)
        else:
            job_pay = (
                pd.to_numeric(jobs_subset["start_salary"], errors="coerce")
                + pd.to_numeric(jobs_subset["range_salary"], errors="coerce")
            ).to_numpy().reshape(-1, 1) / 2
        worker_pay = float(worker.get("exp_wage", 0))
        diff_wage  = np.abs(job_pay - worker_pay)
    else:
        diff_wage = np.zeros_like(sim)

    # คำนวณ time overlap
    if {"start_dt", "end_dt"}.issubset(jobs_subset.columns) and "avail_start" in worker.index:
        overlap = np.minimum(jobs_subset["end_dt"], worker["avail_end"]) \
                  - np.maximum(jobs_subset["start_dt"], worker["avail_start"])
        time_match = (overlap.dt.total_seconds().fillna(0) > 0).astype(int).reshape(-1, 1)
    else:
        time_match = np.zeros_like(sim)

    return sim, diff_wage, same_type, time_match, loc_match

# ------------------------------------------------------------------ #
# 5) Recommend function with refined scoring
# ------------------------------------------------------------------ #
def recommend(worker_row: pd.Series,
              jobs_df: pd.DataFrame,
              k: int = 50,
              n: int = 5) -> pd.DataFrame:

    # 1) FAISS search
    mat   = np.vstack(jobs_df["vec"])
    index = _build_faiss_index(mat)
    w_vec = worker_row.vec.reshape(1, -1)
    faiss.normalize_L2(w_vec)
    sim_scores, idxs = index.search(w_vec, k)
    sim_arr, idxs = sim_scores[0], idxs[0]

    subset = jobs_df.iloc[idxs].copy().reset_index(drop=True)
    subset["sim"] = sim_arr

    # 2) Compute features
    sim_arr, diff_arr, type_arr, time_arr, loc_arr = _feature_df(worker_row, subset)

    # 3) Normalize wage difference into [0,1]
    max_diff   = diff_arr.max() if diff_arr.max() > 0 else 1.0
    wage_score = 1 - (diff_arr / max_diff)

    # 4) Weights: include sim
    w_sim  = 0.4  # similarity from embedding
    w_type = 0.2  # job type match
    w_loc  = 0.2  # location match
    w_wage = 0.1  # wage proximity
    w_time = 0.1  # time overlap

    # 5) Final score
    final = (
        w_sim  * sim_arr.reshape(-1)
        + w_type * type_arr.reshape(-1)
        + w_loc  * loc_arr.reshape(-1)
        + w_wage * wage_score.reshape(-1)
        + w_time * time_arr.reshape(-1)
    )

    subset["ai_score"] = final
    subset = subset.sort_values("ai_score", ascending=False)

    return subset.head(n).reset_index(drop=True)

# ------------------------------------------------------------------ #
# 6) Recommend seekers for employer
# ------------------------------------------------------------------ #
def recommend_seekers(job_row: pd.Series,
                      workers_df: pd.DataFrame,
                      k: int = 50,
                      n: int = 5) -> pd.DataFrame:
    # Flip arguments: treat job_row as a "worker" for searching in workers_df
    return recommend(worker_row=job_row, jobs_df=workers_df, k=k, n=n)
