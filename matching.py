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
# 2) Text encoding (include date/time/location)
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
# 5) Feature extraction between a worker and jobs
# ------------------------------------------------------------------ #
def _feature_df(worker_row: pd.Series, subset: pd.DataFrame):
    # Compute feature arrays: sim_arr is computed in recommend()
    # diff_arr: absolute salary difference
    diff_arr = np.abs(subset['start_salary'] - worker_row['expected_salary'])
    # type_arr: exact job_type match (1 or 0)
    type_arr = (subset['job_type'] == worker_row['job_type']).astype(float)
    # time_arr: time overlap ratio
    # dummy for demonstration: always 1.0
    time_arr = np.ones(len(subset))
    # loc_arr: location match ratio between province/district
    loc_arr = (
        (subset['province'] == worker_row['province']).astype(float) +
        (subset['district'] == worker_row['district']).astype(float) / 2
    )
    return None, diff_arr.values, type_arr.values, time_arr, loc_arr.values

# ------------------------------------------------------------------ #
# 6) Main recommendation: worker -> jobs
# ------------------------------------------------------------------ #
def recommend(worker_row: pd.Series,
              jobs_df: pd.DataFrame,
              k: int = 50,
              n: int = 5) -> pd.DataFrame:
    # 1) Pre-filter to only same job_type
    df_search = jobs_df[jobs_df['job_type'] == worker_row['job_type']]
    if df_search.empty:
        df_search = jobs_df.copy()

    # 2) Build FAISS index on filtered set
    mat   = np.vstack(df_search['vec'])
    index = _build_faiss_index(mat)
    w_vec = worker_row.vec.reshape(1, -1)
    faiss.normalize_L2(w_vec)

    # 3) Search top-k
    sim_scores, idxs = index.search(w_vec, k)
    sim_arr, idxs = sim_scores[0], idxs[0]
    subset = df_search.iloc[idxs].copy()
    subset['sim'] = sim_arr

    # 4) Apply similarity threshold
    subset = subset[subset['sim'] >= 0.3]

    # 5) Extract other features
    _, diff_arr, type_arr, time_arr, loc_arr = _feature_df(worker_row, subset)

    # 6) Normalize wage difference
    max_diff = diff_arr.max() if diff_arr.max() > 0 else 1.0
    wage_score = 1 - (diff_arr / max_diff)

    # 7) Feature weighting
    w_type  = 0.7  # High importance on job_type match
    w_loc   = 0.2  # Location match
    w_wage  = 0.05 # Wage match
    w_time  = 0.05 # Time match

    final = (
        w_type * type_arr +
        w_loc  * loc_arr +
        w_wage * wage_score +
        w_time * time_arr
    ).reshape(-1)

    subset['ai_score'] = final
    subset = subset.sort_values('ai_score', ascending=False)

    return subset.head(n).reset_index(drop=True)

# ------------------------------------------------------------------ #
# 7) Reverse: Recommend workers for a job
# ------------------------------------------------------------------ #
def recommend_seekers(job_row: pd.Series,
                      workers_df: pd.DataFrame,
                      k: int = 50,
                      n: int = 5) -> pd.DataFrame:
    return recommend(worker_row=job_row, jobs_df=workers_df, k=k, n=n)
