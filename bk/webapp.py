
import streamlit as st
import pandas as pd
import glob
import os
import unicodedata
import numpy as np

st.set_page_config(page_title="CSVデータベース検索アプリ", layout="wide")

# --- 関数定義 ---
@st.cache_data
def normalize_text(text):
    if not isinstance(text, str):
        return text
    return unicodedata.normalize('NFKC', text).lower()

@st.cache_data
def load_and_prepare_data(db_dir):
    csv_files = glob.glob(os.path.join(db_dir, '*.csv'))
    if not csv_files:
        return None
    df_list = []
    for file in csv_files:
        try:
            df_list.append(pd.read_csv(file, encoding='utf-8'))
        except UnicodeDecodeError:
            try:
                df_list.append(pd.read_csv(file, encoding='shift-jis'))
            except Exception as e:
                st.error(f"ファイル読み込みエラー: {file} - {e}")
                return None
    if not df_list:
        return None
    df = pd.concat(df_list, ignore_index=True)
    for col in ['着順', '枠番', '馬番', '斤量', '単勝', '人気', '賞金']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    if '距離' in df.columns:
        df['距離'] = pd.to_numeric(df['距離'].astype(str).str.extract(r'(\d+)', expand=False), errors='coerce')
    return df

# --- 初期化 ---
st.title('CSVデータベース検索アプリ')
df_original = load_and_prepare_data('database')

if 'filters' not in st.session_state:
    st.session_state.filters = []
if 'editing_index' not in st.session_state:
    st.session_state.editing_index = None

# --- メイン処理 ---
if df_original is not None:
    columns = df_original.columns.tolist()
    st.sidebar.header('検索条件')

    # --- 編集モードUI ---
    if st.session_state.editing_index is not None:
        st.sidebar.subheader("条件の編集")
        idx = st.session_state.editing_index
        f = st.session_state.filters[idx]
        col = f['column']
        st.sidebar.selectbox('カラムを選択', [col], index=0, disabled=True)
        column_is_numeric = pd.api.types.is_numeric_dtype(df_original[col])
        if column_is_numeric:
            type_mapping_display = {'range': '範囲指定', 'exact': '完全一致'}
            type_index = ["範囲指定", "完全一致"].index(type_mapping_display[f['type']])
            edit_search_type = st.sidebar.radio("検索方法", ["範囲指定", "完全一致"], index=type_index)
            if edit_search_type == "範囲指定":
                min_val = st.sidebar.number_input('最小値', value=f.get('min', np.nan), format="%f")
                max_val = st.sidebar.number_input('最大値', value=f.get('max', np.nan), format="%f")
            else:
                exact_val = st.sidebar.number_input(f'{col}の値', value=f.get('value', np.nan), format="%f")
        else:
            search_value = st.sidebar.text_input('検索値を入力', value=f.get('value', ""))
        col1, col2 = st.sidebar.columns(2)
        if col1.button("条件を更新", type="primary"):
            new_filter = {'column': col}
            if column_is_numeric:
                if edit_search_type == "範囲指定":
                    new_filter['type'] = 'range'
                    new_filter['min'] = min_val
                    new_filter['max'] = max_val
                else:
                    new_filter['type'] = 'exact'
                    new_filter['value'] = exact_val
            else:
                new_filter['type'] = 'text'
                new_filter['value'] = search_value
            st.session_state.filters[idx] = new_filter
            st.session_state.editing_index = None
            st.rerun()
        if col2.button("キャンセル"):
            st.session_state.editing_index = None
            st.rerun()
    # --- 追加モードUI ---
    else:
        st.sidebar.subheader("新しい条件の追加")
        selected_column = st.sidebar.selectbox('カラムを選択', columns, key="add_col_select")
        column_is_numeric = pd.api.types.is_numeric_dtype(df_original[selected_column])
        if column_is_numeric:
            search_type = st.sidebar.radio("検索方法", ["範囲指定", "完全一致"], key=f"add_{selected_column}_type")
            if search_type == "範囲指定":
                min_val = st.sidebar.number_input('最小値', value=np.nan, format="%f", key="add_range_min")
                max_val = st.sidebar.number_input('最大値', value=np.nan, format="%f", key="add_range_max")
                if st.sidebar.button('条件を追加', key='add_range_btn'):
                    st.session_state.filters.append({'column': selected_column, 'type': 'range', 'min': min_val, 'max': max_val})
                    st.rerun()
            else:
                exact_val = st.sidebar.number_input(f"{selected_column}の値", value=np.nan, format="%f", key="add_exact_val")
                if st.sidebar.button('条件を追加', key='add_exact_btn'):
                    if not pd.isna(exact_val):
                        st.session_state.filters.append({'column': selected_column, 'type': 'exact', 'value': exact_val})
                        st.rerun()
                    else:
                        st.sidebar.warning('値を入力してください。')
        else:
            search_value = st.sidebar.text_input('検索値を入力', key="add_text_val")
            if st.sidebar.button('条件を追加', key='add_text_btn'):
                if search_value:
                    st.session_state.filters.append({'column': selected_column, 'type': 'text', 'value': search_value})
                    st.rerun()
                else:
                    st.sidebar.warning('検索値を入力してください。')

    # --- 適用中フィルターの表示 ---
    st.sidebar.subheader('適用中の条件')
    if not st.session_state.filters:
        st.sidebar.write('条件はありません')
    else:
        for i, f in enumerate(st.session_state.filters):
            col1, col2, col3 = st.sidebar.columns([0.7, 0.15, 0.15])
            f_type = f['type']
            if f_type == 'range': label = f'{f["column"]}: {f.get("min", "N/A")} ~ {f.get("max", "N/A")}'
            elif f_type == 'exact': label = f'{f["column"]} = {f["value"]}'
            else: label = f'{f["column"]} contains "{f["value"]}"'
            col1.write(label)
            if col2.button('✏️', key=f'edit_{i}'):
                st.session_state.editing_index = i
                st.rerun()
            if col3.button('❌', key=f'del_{i}'):
                st.session_state.filters.pop(i)
                st.session_state.editing_index = None
                st.rerun()

    if st.sidebar.button('全条件をリセット'):
        st.session_state.filters = []
        st.session_state.editing_index = None
        st.rerun()

    # --- データ表示 ---
    df_filtered = df_original.copy()
    if st.session_state.filters:
        for f in st.session_state.filters:
            col, f_type = f['column'], f['type']
            try:
                if f_type == 'range':
                    if not pd.isna(f.get('min')):
                        df_filtered = df_filtered[df_filtered[col] >= f['min']]
                    if not pd.isna(f.get('max')):
                        df_filtered = df_filtered[df_filtered[col] <= f['max']]
                elif f_type == 'exact':
                    if not pd.isna(f.get('value')):
                        df_filtered = df_filtered[df_filtered[col] == f['value']]
                elif f_type == 'text':
                    normalized_val = normalize_text(f['value'])
                    search_series = df_filtered[col].astype(str).apply(normalize_text)
                    df_filtered = df_filtered[search_series.str.contains(normalized_val, na=False)]
            except Exception as e:
                st.error(f"フィルター適用中にエラーが発生しました: {e}")

    st.subheader("分析結果")
    total_bet = len(df_filtered) * 100
    df_wins = df_filtered[df_filtered['着順'] == 1]
    total_payout = (df_wins['単勝'] * 100).sum()
    recovery_rate = total_payout / total_bet if total_bet > 0 else 0
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("回収率", f"{recovery_rate:.1%}")
    col2.metric("投資合計", f"{int(total_bet):,}円")
    col3.metric("払戻合計", f"{int(total_payout):,}円")
    col4.metric("表示件数", f"{len(df_filtered)}件")
    st.dataframe(df_filtered)

    # --- 回収率ランキング機能 ---
    st.divider()
    st.header("回収率ランキング")
    c1, c2, c3, c4 = st.columns(4)
    string_columns = df_original.select_dtypes(include=['object']).columns.tolist()
    group_col = c1.selectbox("集計対象カラム", string_columns, key="rank_group_col")
    filter_col = c2.selectbox("絞り込み条件カラム", ["なし"] + string_columns, key="rank_filter_col")
    filter_val = None
    if filter_col != "なし":
        unique_vals = df_original[filter_col].dropna().unique()
        filter_val = c3.selectbox(f'{filter_col}の値', unique_vals, key="rank_filter_val")
    min_races = c4.number_input("最低レース数", min_value=1, value=10, key="rank_min_races")

    if st.button("ランキングを計算", type="primary"):
        with st.spinner("計算中..."):
            target_df = df_original.copy()
            if filter_col != "なし" and filter_val is not None:
                target_df = target_df[target_df[filter_col] == filter_val]
            grouped = target_df.groupby(group_col)
            results = []
            for name, group in grouped:
                race_count = len(group)
                if race_count >= min_races:
                    total_bet = race_count * 100
                    df_wins = group[group['着順'] == 1]
                    total_payout = (df_wins['単勝'] * 100).sum()
                    recovery_rate = total_payout / total_bet if total_bet > 0 else 0
                    results.append({
                        group_col: name,
                        "回収率": recovery_rate,
                        "レース数": race_count,
                        "勝利数": len(df_wins),
                        "投資合計": total_bet,
                        "払戻合計": total_payout,
                    })
            if results:
                ranked_df = pd.DataFrame(results)
                ranked_df = ranked_df.sort_values("回収率", ascending=False).reset_index(drop=True)
                st.dataframe(ranked_df.style.format({"回収率": "{:.1%}", "投資合計": "{:,}円", "払戻合計": "{:,}円"}))
            else:
                st.warning("表示できるデータがありません。最低レース数などを調整してください。")

else:
    st.error("データベースディレクトリにCSVファイルが見つかりません。")
