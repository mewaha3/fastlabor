import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

# ------------------------------------------------------------------ #
# 1) Load embedding model
# ------------------------------------------------------------------ #
_EMBED_MODEL = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# ------------------------------------------------------------------ #
# 2) Columns for encoding text
# ------------------------------------------------------------------ #
_TEXT_COL_JOBS = [
    "job_type", "job_detail", "salary",
    "province", "district", "subdistrict",
    "job_date", "start_time", "end_time",
]
_TEXT_COL_WORKERS = [
    "job_type", "skills", "start_salary", "range_salary",
    "province", "district", "subdistrict",
    "job_date", "start_time", "end_time",
]

# ------------------------------------------------------------------ #
# 3) Text encoding helper
# ------------------------------------------------------------------ #
def _encode_texts(texts: list[str]) -> np.ndarray:
    return _EMBED_MODEL.encode([str(t) for t in texts], show_progress_bar=False)

# ------------------------------------------------------------------ #
# 4) Encoding DataFrames
# ------------------------------------------------------------------ #
def encode_job_df(jobs_df: pd.DataFrame) -> pd.DataFrame:
    df = jobs_df.copy()
    for col in _TEXT_COL_JOBS:
        df[col] = df.get(col, "").fillna("").astype(str)
    df["__text"] = df[_TEXT_COL_JOBS].apply(lambda row: " ".join(row.values), axis=1)
    df["vec"] = list(_encode_texts(df["__text"].tolist()))
    df.drop(columns="__text", inplace=True)
    if {"job_date","start_time","end_time"}.issubset(df.columns):
        df["job_date"] = pd.to_datetime(df["job_date"], errors="coerce").dt.date
        df["start_dt"] = pd.to_datetime(df["job_date"].astype(str) + " " + df["start_time"], errors="coerce")
        df["end_dt"]   = pd.to_datetime(df["job_date"].astype(str) + " " + df["end_time"],   errors="coerce")
    return df


def encode_worker_df(workers_df: pd.DataFrame) -> pd.DataFrame:
    df = workers_df.copy()
    for col in _TEXT_COL_WORKERS:
        df[col] = df.get(col, "").fillna("").astype(str)
    df["__text"] = df[_TEXT_COL_WORKERS].apply(lambda row: " ".join(row.values), axis=1)
    df["vec"]    = list(_encode_texts(df["__text"].tolist()))
    df.drop(columns="__text", inplace=True)
    if {"job_date","start_time","end_time"}.issubset(df.columns):
        df["job_date"]    = pd.to_datetime(df["job_date"],    errors="coerce").dt.date
        df["avail_start"] = pd.to_datetime(df["job_date"].astype(str) + " " + df["start_time"], errors="coerce")
        df["avail_end"]   = pd.to_datetime(df["job_date"].astype(str) + " " + df["end_time"],   errors="coerce")
    return df

# ------------------------------------------------------------------ #
# 5) Build FAISS index
# ------------------------------------------------------------------ #
def _build_faiss_index(mat: np.ndarray):
    dim = mat.shape[1]
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(mat)
    index.add(mat)
    return index

# ------------------------------------------------------------------ #
# 6) Feature construction
# ------------------------------------------------------------------ #
def _feature_df(worker: pd.Series, jobs_subset: pd.DataFrame) -> tuple:
    sim = jobs_subset["sim"].to_numpy().reshape(-1,1)
    same_type = (jobs_subset["job_type"].str.strip().str.lower().to_numpy() == 
                 str(worker.get("job_type","")).strip().lower()).astype(int).reshape(-1,1)
    loc_vals = jobs_subset[["province","district","subdistrict"]].applymap(lambda x: str(x).strip().lower()).values
    worker_loc = [str(worker.get(c,"")).strip().lower() for c in ["province","district","subdistrict"]]
    loc_match = (loc_vals == worker_loc).all(axis=1).astype(int).reshape(-1,1)

    if "salary" in jobs_subset.columns:
        job_pay = pd.to_numeric(jobs_subset["salary"], errors="coerce").to_numpy().reshape(-1,1)
    else:
        start = pd.to_numeric(jobs_subset.get("start_salary",0), errors="coerce")
        rng   = pd.to_numeric(jobs_subset.get("range_salary",0), errors="coerce")
        job_pay = ((start + rng)/2).to_numpy().reshape(-1,1)
    worker_pay = float(worker.get("exp_wage",0))
    diff_wage = np.abs(job_pay - worker_pay)

    if {"start_dt","end_dt"}.issubset(jobs_subset.columns) and "avail_start" in worker.index:
        overlap = np.minimum(jobs_subset["end_dt"], worker["avail_end"]) - \
                  np.maximum(jobs_subset["start_dt"], worker["avail_start"])
        time_match = (overlap.dt.total_seconds().fillna(0) > 0).astype(int).reshape(-1,1)
    else:
        time_match = np.zeros_like(sim)

    return sim, diff_wage, same_type, time_match, loc_match

# ------------------------------------------------------------------ #
# 7) Recommend function
# ------------------------------------------------------------------ #
def recommend(worker_row: pd.Series,
              jobs_df: pd.DataFrame,
              k: int = 50,
              n: int = 5) -> pd.DataFrame:
    mat = np.vstack(jobs_df["vec"])
    index = _build_faiss_index(mat)
    w_vec = worker_row["vec"].reshape(1, -1)
    faiss.normalize_L2(w_vec)
    sim_scores, idxs = index.search(w_vec, k)
    sim_arr, idxs = sim_scores[0], idxs[0]

    subset = jobs_df.iloc[idxs].copy().reset_index(drop=True)
    subset["sim"] = sim_arr

    sim_arr, diff_arr, type_arr, time_arr, loc_arr = _feature_df(worker_row, subset)
    max_diff = diff_arr.max() if diff_arr.max() > 0 else 1.0
    wage_score = 1 - (diff_arr / max_diff)

    w_type  = 0.8
    w_loc   = 0.1
    w_wage  = 0.05
    w_time  = 0.05

    final = (
        w_type * type_arr.reshape(-1) +
        w_loc  * loc_arr.reshape(-1) +
        w_wage * wage_score.reshape(-1) +
        w_time * time_arr.reshape(-1)
    )

    subset["ai_score"] = final
    return subset.sort_values("ai_score", ascending=False).head(n).reset_index(drop=True)

# ------------------------------------------------------------------ #
# 8) Recommend seekers for employer (strict filter)
# ------------------------------------------------------------------ #
def recommend_seekers(job_row: pd.Series,
                      workers_df: pd.DataFrame,
                      k: int = 50,
                      n: int = 5) -> pd.DataFrame:
    jt = str(job_row.get("job_type","")).strip().lower()
    candidates = workers_df[workers_df["job_type"].str.strip().str.lower() == jt]
    if candidates.empty:
        return pd.DataFrame(columns=workers_df.columns.tolist() + ["ai_score"])
    return recommend(worker_row=job_row, jobs_df=candidates, k=k, n=n)
