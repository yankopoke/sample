import os
import requests
from bs4 import BeautifulSoup
import csv
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

#ブラウザを偽装するためのUser-Agentリスト
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 OPR/85.0.4341.72",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 OPR/85.0.4341.72",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Vivaldi/5.3.2679.55",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Vivaldi/5.3.2679.55",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Brave/1.40.107",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Brave/1.40.107",
]

BASE_URL = "https://db.netkeiba.com/race/"

def initialize_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'user-agent={random.choice(USER_AGENTS)}')
    driver = webdriver.Chrome(options=options)
    return driver

def get_horse_links_from_race(driver, race_url):
    driver.get(race_url)
    time.sleep(random.uniform(2, 4)) # ページの読み込みを待つ
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', class_='race_table_01')
    horse_links = []
    if table:
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 4:
                a = cols[3].find('a')
                if a and a.has_attr('href'):
                    horse_links.append('https://db.netkeiba.com' + a['href'])
    return horse_links

def scrape_keiba(driver, url, race_id):
    try:
        driver.get(url)
        # ページが完全に読み込まれるまで待機（例: race_table_01クラスのテーブルが出現するまで）
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'race_table_01'))
        )
        time.sleep(random.uniform(2, 4)) # 追加の待機時間
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

    key = race_id
    # --- 開催情報抽出 ---
    race_info_box = soup.select_one('.data_intro')
    if race_info_box:
        info_text = race_info_box.get_text(strip=True, separator=' ')
        m = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日)\s+(\d+回\S+?\d+日目)\s+(.+)', info_text)
        if m:
            開催日 = m.group(1)
            開催場 = m.group(2)
            クラス = m.group(3)
        else:
            info_parts = info_text.split(' ', 2)
            開催日 = info_parts[0] if len(info_parts) > 0 else ''
            開催場 = info_parts[1] if len(info_parts) > 1 else ''
            クラス = info_parts[2] if len(info_parts) > 2 else ''
    else:
        開催日 = 開催場 = クラス = ''

    shiba_dirt = ''
    kyori = ''
    tenkou = ''
    baba = ''
    if race_info_box:
        info_text = race_info_box.get_text("\n", strip=True)
        m_course = re.search(r'(芝|ダ)[^\d]*(\d{3,4}m)', info_text)
        if m_course:
            shiba_dirt = m_course.group(1)
            kyori = m_course.group(2)
        m_tenkou = re.search(r'天候\s*:\s*([\u4e00-\u9fa5ぁ-んァ-ヶa-zA-Z0-9]{1})', info_text)
        if m_tenkou:
            tenkou = m_tenkou.group(1)
        m_baba = re.search(r'(芝|ダート)\s*:\s*(良|稍重|重|不良)', info_text)
        if m_baba:
            baba = m_baba.group(2)

    table = soup.find('table', class_='race_table_01')
    if table is None:
        return []
    rows = table.find_all('tr')[1:]

    results = []
    for row in rows:
        cols = row.find_all(['td', 'th'])
        if len(cols) < 15:
            continue
        着順 = cols[0].text.strip()
        枠番 = cols[1].text.strip()
        馬番 = cols[2].text.strip()
        馬名 = cols[3].text.strip()
        性齢 = cols[4].text.strip()
        斤量 = cols[5].text.strip()
        騎手 = cols[6].text.strip()
        タイム = cols[7].text.strip()
        着差 = cols[8].text.strip()
        通過 = cols[10].text.strip()
        上り = cols[11].text.strip()
        単勝 = cols[12].text.strip()
        人気 = cols[13].text.strip()
        馬体重 = cols[14].text.strip()
        賞金 = cols[-1].text.strip()
        # 馬詳細ページURL
        horse_url = None
        if len(cols) >= 4:
            a = cols[3].find('a')
            if a and a.has_attr('href'):
                horse_url = 'https://db.netkeiba.com' + a['href']
        race_row = {
            "key": key, "開催日": 開催日, "開催場": 開催場, "クラス": クラス,
            "着順": 着順, "枠番": 枠番, "馬番": 馬番, "馬名": 馬名, "性齢": 性齢, "斤量": 斤量, "騎手": 騎手, "タイム": タイム, "着差": 着差, "通過": 通過, "上り": 上り, "単勝": 単勝, "人気": 人気, "馬体重": 馬体重, "賞金": 賞金,
            "芝ダート": shiba_dirt, "距離": kyori, "天候": tenkou, "馬場": baba
        }
        results.append(race_row)
    return results

def save_csv(data, filename):
    all_keys = []
    for row in data:
        for key in row.keys():
            if key not in all_keys:
                all_keys.append(key)
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(all_keys)
        for row in data:
            writer.writerow([row.get(key, '') for key in all_keys])

if __name__ == "__main__":
    race_id_list = []
    # race_id_list_all.txt が gemini_sample ディレクトリ直下にあると仮定
    race_id_list_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "race_id_list_all.txt")
    if not os.path.exists(race_id_list_path):
        print(f"Error: {race_id_list_path} not found. Please create this file with race IDs.")
        sys.exit(1)

    with open(race_id_list_path, "r", encoding="utf-8") as f:
        race_id_list = [line.strip() for line in f]

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "2022_result_selenium.csv")

    FIXED_HEADER = [
        "key", "開催日", "開催場", "クラス", "着順", "枠番", "馬番", "馬名", "性齢", "斤量", "騎手", "タイム", "着差", "通過", "上り", "単勝", "人気", "馬体重", "賞金", "芝ダート", "距離", "天候", "馬場"
    ]
    total = len(race_id_list)
    last_key = None

    driver = None # driverを初期化
    try:
        driver = initialize_driver() # driverをここで初期化
        for idx, race_id in enumerate(race_id_list, 1):
            url = BASE_URL + race_id + "/"
            data = scrape_keiba(driver, url, race_id) # driverを渡す
            if data:
                all_keys = set()
                for row in data:
                    all_keys.update(row.keys())
                header = FIXED_HEADER[:]
                for k in all_keys:
                    if k not in header:
                        header.append(k)
                write_header = not os.path.exists(output_file)
                with open(output_file, 'a', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=header)
                    if write_header:
                        writer.writeheader()
                    writer.writerows(data)
                print(f"{idx}/{total} ({(idx/total)*100:.2f}%) 完了: {race_id}")
                last_key = race_id
            time.sleep(random.uniform(3, 7)) # 各リクエスト間の待機時間を長くする
    except KeyboardInterrupt:
        print("\nスクレイピングが中断されました。最後に完了した key:", last_key)
        sys.exit(0)
    finally:
        if driver:
            driver.quit() # 処理終了時にdriverを閉じる
    print(f"全レースの処理が完了しました（随時CSV追記）: {output_file}")
