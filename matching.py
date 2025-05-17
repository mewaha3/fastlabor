from pathlib import Path
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

# ------------------------------------------------------------------ #
# 1) Load embedding model (supports multiple languages, including Thai)
# ------------------------------------------------------------------ #
_EMBED_MODEL = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")

# ------------------------------------------------------------------ #
# 2) Define text columns to embed
# ------------------------------------------------------------------ #
_TEXT_COL_JOBS    = [
    "job_type", "job_detail", "required_skill",
    "province", "district", "subdistrict",
    "start_salary", "range_salary"
]

_TEXT_COL_WORKERS = [
    "job_history", "skills",
    "province", "district", "subdistrict",
    "expected_salary"
]

# ------------------------------------------------------------------ #
# 3) Utility: build FAISS index
# ------------------------------------------------------------------ #
def _build_faiss_index(mat: np.ndarray) -> faiss.IndexFlatIP:
    faiss.normalize_L2(mat)
    dim = mat.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(mat)
    return index

# ------------------------------------------------------------------ #
# 4) Embed text sequence
# ------------------------------------------------------------------ #
def _embed_text(texts: list[str]) -> np.ndarray:
    return _EMBED_MODEL.encode(texts)

# ------------------------------------------------------------------ #
# 5) Encode job DataFrame: add 'vec' column
# ------------------------------------------------------------------ #
def encode_job_df(jobs_df: pd.DataFrame) -> pd.DataFrame:
    df = jobs_df.copy()
    # Concatenate text columns into a single string per row
    texts = df[_TEXT_COL_JOBS].astype(str).agg(" ".join, axis=1).tolist()
    embeddings = _embed_text(texts)
    df['vec'] = list(embeddings)
    return df

# ------------------------------------------------------------------ #
# 6) Encode worker DataFrame: add 'vec' column
# ------------------------------------------------------------------ #
def encode_worker_df(workers_df: pd.DataFrame) -> pd.DataFrame:
    df = workers_df.copy()
    texts = df[_TEXT_COL_WORKERS].astype(str).agg(" ".join, axis=1).tolist()
    embeddings = _embed_text(texts)
    df['vec'] = list(embeddings)
    return df

# ------------------------------------------------------------------ #
# 7) Feature extraction between a worker and jobs
# ------------------------------------------------------------------ #
def _feature_df(worker_row: pd.Series, subset: pd.DataFrame):
    # diff_arr: absolute salary difference
    diff_arr = np.abs(subset['start_salary'] - worker_row['expected_salary'])
    # type_arr: exact job_type match
    type_arr = (subset['job_type'] == worker_row['job_type']).astype(float)
    # time_arr: placeholder for time overlap ratio
    time_arr = np.ones(len(subset))
    # loc_arr: location match score
    loc_arr = (
        (subset['province'] == worker_row['province']).astype(float) +
        (subset['district'] == worker_row['district']).astype(float) / 2
    )
    return diff_arr.values, type_arr.values, time_arr, loc_arr.values

# ------------------------------------------------------------------ #
# 8) Main recommendation: worker -> jobs
# ------------------------------------------------------------------ #
def recommend(worker_row: pd.Series,
              jobs_df: pd.DataFrame,
              k: int = 50,
              n: int = 5) -> pd.DataFrame:
    # Pre-filter to same job_type
    df_search = jobs_df[jobs_df['job_type'] == worker_row['job_type']]
    if df_search.empty:
        df_search = jobs_df.copy()

    # Build FAISS index
    mat = np.vstack(df_search['vec'])
    index = _build_faiss_index(mat)
    w_vec = worker_row['vec'].reshape(1, -1)
    faiss.normalize_L2(w_vec)

    # Search top-k
    sim_scores, idxs = index.search(w_vec, k)
    subset = df_search.iloc[idxs[0]].copy()
    subset['sim'] = sim_scores[0]

    # Filter by similarity threshold
    threshold = 0.3
    subset = subset[subset['sim'] >= threshold]

    # Extract features
    diff_arr, type_arr, time_arr, loc_arr = _feature_df(worker_row, subset)

    # Normalize wage difference score
    max_diff = diff_arr.max() if diff_arr.max() > 0 else 1.0
    wage_score = 1 - (diff_arr / max_diff)

    # Feature weights
    w_type  = 0.7
    w_loc   = 0.2
    w_wage  = 0.05
    w_time  = 0.05

    final_score = (
        w_type * type_arr +
        w_loc  * loc_arr +
        w_wage * wage_score +
        w_time * time_arr
    )

    subset['ai_score'] = final_score
    result = subset.sort_values('ai_score', ascending=False).head(n).reset_index(drop=True)
    return result

# ------------------------------------------------------------------ #
# 9) Reverse recommendation: job -> workers
# ------------------------------------------------------------------ #
def recommend_seekers(job_row: pd.Series,
                      workers_df: pd.DataFrame,
                      k: int = 50,
                      n: int = 5) -> pd.DataFrame:
    # Use recommend by swapping roles
    return recommend(worker_row=job_row, jobs_df=workers_df, k=k, n=n)
