# utils/split.py

def split_data_for_out_of_sample(df, split_ratio=0.8):
    """
    تقسیم داده‌ها به in-sample و out-of-sample
    """
    if df is None or df.empty:
        return None, None
    split_index = int(len(df) * split_ratio)
    df_in_sample = df.iloc[:split_index].copy()
    df_out_sample = df.iloc[split_index:].copy()
    return df_in_sample, df_out_sample