import pandas as pd

# ------------------------------------------------------------------ #
# 1) Encode job DataFrame (pass-through)
# ------------------------------------------------------------------ #
def encode_job_df(jobs_df: pd.DataFrame) -> pd.DataFrame:
    """
    ไม่เปลี่ยนแปลง DataFrame งาน: คืนสำเนาแบบไม่แก้ไข
    """
    return jobs_df.copy()

# ------------------------------------------------------------------ #
# 2) Encode worker DataFrame (pass-through)
# ------------------------------------------------------------------ #
def encode_worker_df(workers_df: pd.DataFrame) -> pd.DataFrame:
    """
    ไม่เปลี่ยนแปลง DataFrame ผู้สมัคร: คืนสำเนาแบบไม่แก้ไข
    """
    return workers_df.copy()

# ------------------------------------------------------------------ #
# 3) Recommend based on exact job_type match only
# ------------------------------------------------------------------ #
def recommend(worker_row: pd.Series,
              jobs_df: pd.DataFrame,
              n: int = 5) -> pd.DataFrame:
    """
    คืน rows จาก jobs_df ที่มี job_type ตรงกับ worker_row['job_type'] เป๊ะๆ (ภาษาไทย)
    และตั้ง ai_score = 1.0 ให้ทุกแถว
    """
    target = str(worker_row.get('job_type', '')).strip()
    # กรอง exact match เท่านั้น
    df_match = jobs_df[jobs_df.get('job_type', '') == target].copy()
    if df_match.empty:
        # ไม่มีตรงกันเลย: คืน DataFrame ว่างพร้อมคอลัมน์ ai_score
        return pd.DataFrame(columns=list(jobs_df.columns) + ['ai_score'])
    # กำหนด ai_score = 1.0
    df_match['ai_score'] = 1.0
    # รีเซ็ต index และคืน Top-n
    return df_match.reset_index(drop=True).head(n)

# ------------------------------------------------------------------ #
# 4) Reverse: recommend seekers for a job
# ------------------------------------------------------------------ #
def recommend_seekers(job_row: pd.Series,
                      workers_df: pd.DataFrame,
                      n: int = 5) -> pd.DataFrame:
    """
    คืน rows จาก workers_df ที่มี job_type ตรงกับ job_row['job_type'] เป๊ะๆ (ภาษาไทย)
    และตั้ง ai_score = 1.0 ให้ทุกแถว
    """
    target = str(job_row.get('job_type', '')).strip()
    df_match = workers_df[workers_df.get('job_type', '') == target].copy()
    if df_match.empty:
        return pd.DataFrame(columns=list(workers_df.columns) + ['ai_score'])
    df_match['ai_score'] = 1.0
    return df_match.reset_index(drop=True).head(n)
