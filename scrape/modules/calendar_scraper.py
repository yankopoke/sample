
import os
import csv
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_calendar(year: int, config: dict) -> list[str]:
    """
    指定年度の全月からレース一覧URLを取得し、CSVに保存する。
    
    Args:
        year (int): 対象年度
        config (dict): 設定辞書
    
    Returns:
        list[str]: 取得したレース一覧URLのリスト
    """
    # 設定からの値の取得
    base_url = config['urls']['calendar_base']
    wait_time = config.get('wait_time', 1)
    min_wait = config.get('min_wait')
    max_wait = config.get('max_wait')
    
    user_agent_conf = config.get('user_agent', "Mozilla/5.0")
    output_dir = config['output_dir']
    filename_template = config['filenames']['race_links']
    
    # User-Agentの選択
    user_agent = user_agent_conf
    if isinstance(user_agent_conf, list):
        user_agent = random.choice(user_agent_conf)

    headers = {
        "User-Agent": user_agent
    }

    all_links = []
    print(f"{year}年1月から12月までのレース日程URLを取得します。")

    for month in range(1, 13):
        print(f"- {month}月のリンクを取得中...")
        params = {
            "year": year,
            "month": month
        }
        
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # hrefに "race_list.html?kaisai_date=" を含むaタグを探す
            for a_tag in soup.find_all("a", href=lambda href: href and "race_list.html?kaisai_date=" in href):
                # 相対URLを絶対URLに変換
                absolute_url = urljoin(base_url, a_tag["href"])
                if absolute_url not in all_links:
                    all_links.append(absolute_url)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the page ({year}/{month}): {e}")

        # サーバー負荷軽減のための待機
        if min_wait is not None and max_wait is not None:
            try:
                time.sleep(random.uniform(float(min_wait), float(max_wait)))
            except (ValueError, TypeError):
                time.sleep(wait_time)
        else:
            time.sleep(wait_time)

    # 重複を除去してソート
    all_links = sorted(list(set(all_links)))

    # 保存処理
    if all_links:
        # 出力ディレクトリの作成
        os.makedirs(output_dir, exist_ok=True)
        
        # ファイル名の生成
        filename = filename_template.format(year=year)
        output_path = os.path.join(output_dir, filename)
        
        print(f"\n取得したすべてのリンクを {output_path} に出力します。")
        
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["url"]) # ヘッダー
                for link in all_links:
                    writer.writerow([link])
            print(f"CSVファイルの出力が完了しました: {output_path}")
        except IOError as e:
            print(f"ファイルへの書き込み中にエラーが発生しました: {e}")
    else:
        print(f"{year}年のURLの取得に失敗したか、対象のレース日程がありませんでした。")

    return all_links

if __name__ == "__main__":
    # テスト実行用（ダミー設定）
    config = {
        'urls': {'calendar_base': "https://race.netkeiba.com/top/calendar.html"},
        'wait_time': 1,
        'user_agent': "Mozilla/5.0",
        'output_dir': "./test_data",
        'filenames': {'race_links': "test_race_links_{year}.csv"}
    }
    scrape_calendar(2020, config)
