from pathlib import Path
import numpy as np
import pandas as pd

# ------------------------------------------------------------------ #
# 1) Encode job DataFrame (pass-through or you can remove vec entirely)
# ------------------------------------------------------------------ #
def encode_job_df(jobs_df: pd.DataFrame) -> pd.DataFrame:
    # ไม่ใช้ embedding ในการ match แบบนี้
    return jobs_df.copy()

# ------------------------------------------------------------------ #
# 2) Encode worker DataFrame (pass-through)
# ------------------------------------------------------------------ #
def encode_worker_df(workers_df: pd.DataFrame) -> pd.DataFrame:
    return workers_df.copy()

# ------------------------------------------------------------------ #
# 3) Recommend based on job_type only
# ------------------------------------------------------------------ #
def recommend(worker_row: pd.Series,
              jobs_df: pd.DataFrame,
              n: int = 5) -> pd.DataFrame:
    """
    คืนรายการงานจาก jobs_df ที่มี job_type ตรงกับ worker_row['job_type'] เป๊ะๆ
    """
    target = str(worker_row.get('job_type', '')).strip()
    # กรอง exact match เท่านั้น
    df_match = jobs_df[jobs_df.get('job_type', '') == target].copy()
    # ถ้าไม่พบเลย คืน DataFrame เปล่า (มีคอลัมน์เดียวกับ jobs_df)
    if df_match.empty:
        return pd.DataFrame(columns=jobs_df.columns)
    # รีเซ็ต index และคืน Top-n
    return df_match.reset_index(drop=True).head(n)

# ------------------------------------------------------------------ #
# 4) Reverse: recommend seekers for a job
# ------------------------------------------------------------------ #
def recommend_seekers(job_row: pd.Series,
                      workers_df: pd.DataFrame,
                      n: int = 5) -> pd.DataFrame:
    """
    คืนรายการผู้สมัครจาก workers_df ที่มี job_type ตรงกับ job_row['job_type'] เป๊ะๆ
    """
    target = str(job_row.get('job_type', '')).strip()
    df_match = workers_df[workers_df.get('job_type', '') == target].copy()
    if df_match.empty:
        return pd.DataFrame(columns=workers_df.columns)
    return df_match.reset_index(drop=True).head(n)
