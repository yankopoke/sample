import pandas as pd
import glob
import os
import unicodedata

def normalize_text(text):
    """
    文字列を正規化する（半角・小文字に統一）
    """
    if not isinstance(text, str):
        return text
    return unicodedata.normalize('NFKC', text).lower()

def load_database(db_dir):
    """
    指定されたディレクトリ内のすべてのCSVファイルを読み込み、
    1つのPandas DataFrameに結合する。
    """
    csv_files = glob.glob(os.path.join(db_dir, '*.csv'))
    if not csv_files:
        print(f"ディレクトリ '{db_dir}' にCSVファイルが見つかりません。")
        return None
    
    df_list = []
    for file in csv_files:
        try:
            df_list.append(pd.read_csv(file, encoding='utf-8'))
        except UnicodeDecodeError:
            try:
                df_list.append(pd.read_csv(file, encoding='shift-jis'))
            except Exception as e:
                print(f"ファイルの読み込みに失敗しました: {file} - {e}")

    if not df_list:
        return None

    return pd.concat(df_list, ignore_index=True)

def search_interactive(df):
    """
    対話的にデータを検索する。
    """
    original_df = df.copy()
    current_df = df.copy()

    while True:
        print("\n------------------------------------")
        print(f"現在のデータ件数: {len(current_df)}件")
        if len(current_df) < len(original_df):
            print(f"（フィルター適用中）")
        
        print("\n--- 操作を選択してください ---")
        print("[1] 検索条件を追加")
        print("[2] 検索をリセット")
        print("[3] 終了")
        
        choice = normalize_text(input("番号を入力: ").strip())

        if choice == '1':
            print("\n--- カラム一覧 ---")
            print(original_df.columns.tolist())
            column = input("検索したいカラム名を入力してください: ").strip()

            if column not in original_df.columns:
                print("エラー: 存在しないカラム名です。")
                continue

            value = normalize_text(input(f"カラム '{column}' で検索したい値を入力してください: "))

            try:
                if pd.api.types.is_numeric_dtype(original_df[column].dtype):
                    # 数値型の場合 (完全一致)
                    current_df = current_df[current_df[column] == pd.to_numeric(value)]
                else:
                    # 文字列型の場合 (正規化した上で部分一致)
                    search_series = current_df[column].astype(str).apply(normalize_text)
                    current_df = current_df[search_series.str.contains(value, na=False)]
                
                print(f"\n--- 検索結果 ({len(current_df)}件) ---")
                print(current_df.head())

            except Exception as e:
                print(f"検索中にエラーが発生しました: {e}")

        elif choice == '2':
            current_df = original_df.copy()
            print("\n検索条件をリセットしました。")

        elif choice == '3':
            print("アプリケーションを終了します。")
            break
        
        else:
            print("エラー: [1], [2], [3] のいずれかを入力してください。")

def main():
    """
    メイン関数
    """
    db_dir = 'database'
    df = load_database(db_dir)

    if df is not None:
        print("データベースの読み込みが完了しました。")
        search_interactive(df)

if __name__ == '__main__':
    main()
