
import pandas as pd
import os

# --- 設定 ---
# 入力ファイルパス
input_path = r"C:\Users\naga4\Downloads\gemini_sample\database\2023_result.csv"
# 出力ファイルパス
output_path = r"C:\Users\naga4\Downloads\gemini_sample\database\2023_result_with_past_data.csv"
# 文字コード
encoding = "utf-8-sig"

# 過去何走分まで取得するか
PAST_RACE_COUNT = 5
# 過去の成績として追加したい特徴量のリスト
# 注: CSVファイルに存在する列名を指定してください
features_to_shift = [
    "開催場", "開催回", "クラス", "クラス特徴", "着順", "枠番", "馬番", 
    "性", "年齢", "斤量", "騎手", "タイム", "着差", "通過", "上り", 
    "単勝", "人気", "馬体重", "賞金", "芝ダート", "距離", "天候", "馬場"
]

# --- 処理 ---
try:
    print(f"'{os.path.basename(input_path)}' を読み込んでいます...")
    df = pd.read_csv(input_path, encoding=encoding)
    print("読み込み完了。")

    # --- 前処理 ---
    # 日付列をdatetime型に変換
    if '開催日' in df.columns:
        df['開催日'] = pd.to_datetime(df['開催日'], format='%Y年%m月%d日', errors='coerce')
    else:
        raise ValueError("列 '開催日' が見つかりません。")

    # 着順列を数値に変換（'除外', '中止'などはNaNになる）
    if '着順' in df.columns:
        df['着順'] = pd.to_numeric(df['着順'], errors='coerce')
    
    # 処理対象の特徴量が存在するか確認
    valid_features = [f for f in features_to_shift if f in df.columns]
    if not valid_features:
        raise ValueError(f"処理対象の特徴量 {features_to_shift} が一つも見つかりません。")
    print(f"処理対象の特徴量: {valid_features}")

    # --- メイン処理 ---
    print("過去のレース成績を追加しています...")
    # 馬名と日付でソート（shift処理のために必須）
    df_sorted = df.sort_values(by=['馬名', '開催日'])

    for i in range(1, PAST_RACE_COUNT + 1):
        for feature in valid_features:
            new_col_name = f'過去{i}走前_{feature}'
            # 馬ごとにグループ化し、shift(i)でi走前のデータを取得
            df_sorted[new_col_name] = df_sorted.groupby('馬名')[feature].shift(i)

    # --- 保存 ---
    print(f"処理結果を '{os.path.basename(output_path)}' に保存しています...")
    # Excelで文字化けしないように'utf-8-sig'エンコーディングで保存
    df_sorted.to_csv(output_path, index=False, encoding='utf-8-sig')
    print("すべての処理が完了しました。")

except FileNotFoundError:
    print(f"エラー: ファイルが見つかりません。パスを確認してください: {input_path}")
except ValueError as e:
    print(f"エラー: {e}")
except Exception as e:
    print(f"予期せぬエラーが発生しました: {e}")
