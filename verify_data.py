
import pandas as pd

# --- 設定 ---
# 検証対象の馬名
HORSE_NAME = 'クリノキングボス'
# 元データのファイルパス
INPUT_CSV = r'C:\Users\naga4\Downloads\gemini_sample\database\2023_result.csv'
# 生成されたデータのファイルパス
OUTPUT_CSV = r'C:\Users\naga4\Downloads\gemini_sample\database\2023_result_with_past_data.csv'
# ファイルエンコーディング
ENCODING = 'utf-8-sig'

# --- 処理 ---
try:
    # 1. データの読み込み
    df_input = pd.read_csv(INPUT_CSV, encoding=ENCODING)
    df_output = pd.read_csv(OUTPUT_CSV, encoding=ENCODING)

    # 日付列をdatetime型に変換
    df_input['開催日'] = pd.to_datetime(df_input['開催日'], format='%Y年%m月%d日', errors='coerce')
    df_output['開催日'] = pd.to_datetime(df_output['開催日'], errors='coerce')


    # 2. 対象の馬のデータを抽出
    horse_input_df = df_input[df_input['馬名'] == HORSE_NAME].sort_values('開催日')
    horse_output_df = df_output[df_output['馬名'] == HORSE_NAME].sort_values('開催日')

    # 3. 表示する列を絞り込む
    # 元データから表示する、答え合わせ用の列
    truth_cols = ['開催日', '着順', '斤量', '上り']
    # 生成データから表示する、過去の成績が含まれた列 (比較しやすいように過去2走分まで)
    generated_cols = ['開催日', '着順', '過去1走前_着順', '過去2走前_着順', '過去1走前_斤量', '過去2走前_斤量', '過去1走前_上り', '過去2走前_上り']

    # --- 結果の表示 ---
    # 日付を見やすいように文字列にフォーマット
    horse_input_df['開催日'] = horse_input_df['開催日'].dt.strftime('%Y-%m-%d')
    horse_output_df['開催日'] = horse_output_df['開催日'].dt.strftime('%Y-%m-%d')

    print("--- データ検証：クリノキングボス ---")
    print(f"【1. 元データ：'{HORSE_NAME}'の実際のレース履歴（日付順）】")
    # style.formatで小数点以下の表示を調整
    print(horse_input_df[truth_cols].to_string(index=False))
    print("\n" + "="*80 + "\n")

    print(f"【2. 生成データ：過去の戦績が追加された'{HORSE_NAME}'のデータ】")
    print(horse_output_df[generated_cols].to_string(index=False))
    print("\n" + "="*80 + "\n")

    print("【確認方法】")
    print("表【2】のN行目のレース結果について見ていきます。(N=2,3,4,...)")
    print("・その行の「過去1走前」の各データ（着順, 斤量, 上り など）が、表【1】の「N-1行目」のデータと一致することを確認します。")
    print("・同様に、「過去2走前」のデータが、表【1】の「N-2行目」のデータと一致することを確認します。")
    print("・例えば、表【2】の3行目の「過去1走前_着順」の値は、表【1】の2行目の「着順」の値と一致するはずです。")
    print("この関係が他の行でも成立していれば、処理は成功しています。")

except FileNotFoundError:
    print(f"エラー: ファイルが見つかりません。パスを確認してください。")
except Exception as e:
    print(f"予期せぬエラーが発生しました: {e}")
