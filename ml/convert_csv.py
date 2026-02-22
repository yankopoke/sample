import pandas as pd
import os
import re
import argparse

# Define constants
RACECOURSES = ["札幌", "函館", "福島", "新潟", "東京", "中山", "中京", "京都", "阪神", "小倉"]

# Define the target column order
TARGET_COLUMN_ORDER = [
    "key", "開催日", "開催場", "開催回", "クラス", "クラス特徴", "着順", "枠番", "馬番",
    "馬名", "性", "年齢", "斤量", "騎手", "タイム", "着差", "通過", "上り", "単勝",
    "人気", "馬体重", "賞金", "芝ダート", "距離", "天候", "馬場"
]

def split_venue(venue_str):
    """Splits the venue string into venue and event number."""
    for course in RACECOURSES:
        if course in venue_str:
            return course, venue_str.replace(course, "").strip()
    return "", venue_str.strip()

def split_class(class_str):
    """Splits the class string into class and class feature."""
    if pd.isna(class_str):
        return "", ""
    parts = re.split(r'\s+', class_str, 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return parts[0], ""

def main():
    """
    Reads a CSV file from a command-line argument, processes its columns,
    and saves the result to a new CSV file named 'result_after.csv'
    in the same directory as the script.
    """
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(
        description="CSVファイルを処理し、スクリプトと同じディレクトリに 'result_after.csv' として保存します。"
    )
    parser.add_argument("input_file", help="入力元のCSVファイルパス。")
    args = parser.parse_args()

    # Define output file path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_filepath = os.path.join(script_dir, 'result_after.csv')

    if not os.path.exists(args.input_file):
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}")
        return

    print(f"'{args.input_file}' を読み込んでいます...")
    # Read the CSV file
    df = pd.read_csv(args.input_file, encoding='utf-8')

    print("データを処理しています...")
    # --- Column Transformations ---

    # Split 性齢 into 性 and 年齢
    df['性'] = df['性齢'].str[0]
    df['年齢'] = df['性齢'].str[1:]

    # Split 開催場 into 開催場 and 開催回
    venue_split = df['開催場'].apply(split_venue)
    df['開催場_temp'] = venue_split.str[0]
    df['開催回'] = venue_split.str[1]
    df['開催場'] = df['開催場_temp']


    # Split クラス into クラス and クラス特徴
    class_split = df['クラス'].apply(split_class)
    df['クラス_temp'] = class_split.str[0]
    df['クラス特徴'] = class_split.str[1]
    df['クラス'] = df['クラス_temp']

    # Reorder and select the final columns
    final_df = pd.DataFrame()
    for col in TARGET_COLUMN_ORDER:
        if col in df.columns:
            final_df[col] = df[col]
        else:
            final_df[col] = None

    # No need to create output directory as it's the script's directory

    print(f"処理完了。新しいファイルを作成しています: '{output_filepath}'")
    # Write to a new CSV file with UTF-8 with BOM encoding
    final_df.to_csv(output_filepath, index=False, encoding='utf-8-sig')

    print("正常に変換が完了しました。")

if __name__ == '__main__':
    main()
