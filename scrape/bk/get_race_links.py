
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_race_links_from_calendar(year: int, month: int) -> list[str]:
    """
    netkeibaの開催日程カレンダーからレース日程のURLを取得する。

    Args:
        year (int): 年
        month (int): 月

    Returns:
        list[str]: レース日程のURLのリスト
    """
    base_url = "https://race.netkeiba.com/top/calendar.html"
    params = {
        "year": year,
        "month": month
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    
    race_links = []
    # hrefに "race_list.html?kaisai_date=" を含むaタグを探す
    for a_tag in soup.find_all("a", href=lambda href: href and "race_list.html?kaisai_date=" in href):
        # 相対URLを絶対URLに変換
        absolute_url = urljoin(base_url, a_tag["href"])
        if absolute_url not in race_links:
            race_links.append(absolute_url)

    return race_links

import csv
import time

# ... (rest of the function definition remains the same)

if __name__ == "__main__":
    target_year = 2020
    all_links = []

    print(f"{target_year}年1月から12月までのレース日程URLを取得します。")

    for month in range(1, 13):
        print(f"- {month}月のリンクを取得中...")
        links = get_race_links_from_calendar(target_year, month)
        if links:
            all_links.extend(links)
        # サーバーに負荷をかけすぎないよう、リクエスト間に待機時間を設ける
        time.sleep(1)

    # 重複を除去
    all_links = sorted(list(set(all_links)))

    if all_links:
        output_filename = f"race_links_{target_year}.csv"
        print(f"\n取得したすべてのリンクを {output_filename} に出力します。")
        
        try:
            with open(output_filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["url"]) # ヘッダーを書き込む
                for link in all_links:
                    writer.writerow([link])
            print(f"CSVファイルの出力が完了しました: {output_filename}")
        except IOError as e:
            print(f"ファイルへの書き込み中にエラーが発生しました: {e}")

    else:
        print("URLの取得に失敗したか、対象のレース日程がありませんでした。")
