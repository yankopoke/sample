
import csv
import time
import random
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs

def scrape_race_list(input_csv: str, config: dict) -> list[str]:
    """
    レース一覧URLのCSVから個別レースURLを取得し、CSVに保存する。
    
    Args:
        input_csv (str): レース一覧URLが記載されたCSVファイルパス
        config (dict): 設定辞書
    
    Returns:
        list[str]: 取得した個別レースURLのリスト
    """
    # 設定の読み込み
    ajax_base_url = config['urls']['race_list_ajax']
    wait_time = config.get('wait_time', 1)
    min_wait = config.get('min_wait')
    max_wait = config.get('max_wait')
    
    user_agent_conf = config.get('user_agent', "Mozilla/5.0")
    output_dir = config['output_dir']
    
    # input_csvからファイル名を推測して出力ファイル名を決定する
    # 例: race_links_2020.csv -> individual_race_urls_2020.csv
    filename = os.path.basename(input_csv)
    year = "unknown"
    if "race_links_" in filename:
        year = filename.replace("race_links_", "").replace(".csv", "")
        output_filename = config['filenames']['individual_urls'].format(year=year)
    else:
        # フォールバック: 入力ファイル名に _individual を付与
        output_filename = filename.replace(".csv", "_individual.csv")

    output_path = os.path.join(output_dir, output_filename)

    # User-Agentの選択
    user_agent = user_agent_conf
    if isinstance(user_agent_conf, list):
        user_agent = random.choice(user_agent_conf)

    headers = {
        "User-Agent": user_agent,
        "X-Requested-With": "XMLHttpRequest"
    }

    # 入力ファイルの読み込み
    try:
        with open(input_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None) # ヘッダーをスキップ
            racelist_urls = [row[0] for row in reader if row]
    except FileNotFoundError:
        print(f"入力ファイルが見つかりません: {input_csv}")
        return []

    all_individual_links = []
    total_urls = len(racelist_urls)
    print(f"{total_urls}個のレース一覧ページから個別レースのURLを取得します。")

    for i, url in enumerate(racelist_urls):
        print(f"- 処理中 ({i+1}/{total_urls}): {url}")
        
        try:
            # URLからkaisai_dateを取得
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            if 'kaisai_date' not in query_params:
                print(f"  スキップ: kaisai_dateが見つかりません: {url}")
                continue
            
            kaisai_date = query_params['kaisai_date'][0]
            
            params = {
                'kaisai_date': kaisai_date
            }
            
            response = requests.get(ajax_base_url, params=params, headers=headers)
            response.raise_for_status()
            response.encoding = 'cp932'
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 正しいリンク形式 (result.html) でリンクを探す
            found_count = 0
            for a_tag in soup.find_all("a", href=lambda href: href and "race/result.html?race_id=" in href):
                if a_tag.get('href'):
                    absolute_url = urljoin("https://race.netkeiba.com/", a_tag['href'])
                    if absolute_url not in all_individual_links:
                        all_individual_links.append(absolute_url)
                        found_count += 1
            
            # print(f"  -> {found_count}件のレースが見つかりました")

        except requests.exceptions.RequestException as e:
            print(f"  エラー: リクエスト中にエラーが発生しました: {e}")
        except Exception as e:
            print(f"  エラー: 予期せぬエラー: {e}")
            
        # 待機
        if min_wait is not None and max_wait is not None:
            try:
                time.sleep(random.uniform(float(min_wait), float(max_wait)))
            except (ValueError, TypeError):
                time.sleep(wait_time)
        else:
            time.sleep(wait_time)

    # 重複を除去してソート
    all_individual_links = sorted(list(set(all_individual_links)))

    # 保存
    if all_individual_links:
        os.makedirs(output_dir, exist_ok=True)
        print(f"\n取得したすべての個別レースURL（{len(all_individual_links)}件）を {output_path} に出力します。")
        
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["url"]) # ヘッダー
                for link in all_individual_links:
                    writer.writerow([link])
            print(f"CSVファイルの出力が完了しました: {output_path}")
        except IOError as e:
            print(f"ファイルへの書き込み中にエラーが発生しました: {e}")
    else:
        print("個別レースのURLは一件も見つかりませんでした。")

    return all_individual_links
