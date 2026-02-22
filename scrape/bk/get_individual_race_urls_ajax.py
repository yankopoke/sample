"""
AJAXリクエストを直接模倣して、netkeibaの個別レースURLをすべて取得し、CSVに出力する最終版スクリプト。
"""
import csv
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs

def get_individual_urls_via_ajax(racelist_url: str) -> list[str]:
    """
    race_list_sub.htmlへのAJAXコールを模倣し、すべての個別レースURLを取得する。

    Args:
        racelist_url (str): 元のレース一覧ページのURL

    Returns:
        list[str]: 個別レースURLのリスト
    """
    try:
        # URLからkaisai_dateを取得
        parsed_url = urlparse(racelist_url)
        kaisai_date = parse_qs(parsed_url.query)['kaisai_date'][0]
    except (KeyError, IndexError):
        print(f"URLからkaisai_dateの取得に失敗しました: {racelist_url}")
        return []

    # 実際のレースデータを含むAJAXエンドポイントを直接叩く
    ajax_url = "https://race.netkeiba.com/top/race_list_sub.html"
    params = {
        'kaisai_date': kaisai_date
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest" # AJAXリクエストであることを示すヘッダー
    }
    
    individual_links = []
    try:
        response = requests.get(ajax_url, params=params, headers=headers)
        response.raise_for_status()
        response.encoding = 'cp932'
        html_content = response.text

        soup = BeautifulSoup(html_content, "html.parser")
        
        # 正しいリンク形式 (result.html) でリンクを探す
        for a_tag in soup.find_all("a", href=lambda href: href and "race/result.html?race_id=" in href):
            if a_tag.get('href'):
                absolute_url = urljoin("https://race.netkeiba.com/", a_tag['href'])
                if absolute_url not in individual_links:
                    individual_links.append(absolute_url)

    except requests.exceptions.RequestException as e:
        print(f"AJAXリクエスト中にエラーが発生しました ({ajax_url}): {e}")
    
    return individual_links

def main():
    """
    メイン処理
    """
    input_filename = "race_links_2020.csv"
    output_filename = "individual_race_urls_2020.csv"
    
    try:
        with open(input_filename, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader) # ヘッダーをスキップ
            racelist_urls = [row[0] for row in reader]
    except FileNotFoundError:
        print(f"入力ファイルが見つかりません: {input_filename}")
        return

    all_individual_links = []
    total_urls = len(racelist_urls)

    print(f"{total_urls}個のレース一覧ページから個別レースのURLを取得します。")

    for i, url in enumerate(racelist_urls):
        print(f"- 処理中 ({i+1}/{total_urls}): {url}")
        links = get_individual_urls_via_ajax(url)
        if links:
            all_individual_links.extend(links)
        time.sleep(1) # サーバー負荷軽減

    # 重複を除去
    all_individual_links = sorted(list(set(all_individual_links)))

    if all_individual_links:
        print(f"\n取得したすべての個別レースURL（{len(all_individual_links)}件）を {output_filename} に出力します。")
        
        try:
            with open(output_filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["url"]) # ヘッダー
                for link in all_individual_links:
                    writer.writerow([link])
            print(f"CSVファイルの出力が完了しました: {output_filename}")
        except IOError as e:
            print(f"ファイルへの書き込み中にエラーが発生しました: {e}")
    else:
        print("個別レースのURLは一件も見つかりませんでした。")

if __name__ == "__main__":
    main()
