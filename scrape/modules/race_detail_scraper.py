
import os
import time
import random
import csv
import re
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def initialize_driver(user_agent=None):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    if user_agent:
        ua = user_agent
        if isinstance(user_agent, list):
            ua = random.choice(user_agent)
        options.add_argument(f'user-agent={ua}')
    driver = webdriver.Chrome(options=options)
    return driver

def extract_race_id_from_url(url):
    # パターン1: https://db.netkeiba.com/race/202001010101/
    if "/race/" in url and "result.html" not in url:
        parts = url.rstrip('/').split('/')
        if parts:
            return parts[-1]
    
    # パターン2: https://race.netkeiba.com/race/result.html?race_id=202006010101
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    if 'race_id' in qs:
        return qs['race_id'][0]
        
    return ""

def scrape_keiba_page(driver, url, race_id):
    try:
        driver.get(url)
        # ページが完全に読み込まれるまで待機
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'race_table_01'))
        )
        time.sleep(1) # 追加の待機
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    except Exception as e:
        print(f"  Error scraping page {url}: {e}")
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
        
        race_row = {
            "key": key, "開催日": 開催日, "開催場": 開催場, "クラス": クラス,
            "着順": 着順, "枠番": 枠番, "馬番": 馬番, "馬名": 馬名, "性齢": 性齢, "斤量": 斤量, "騎手": 騎手, "タイム": タイム, "着差": 着差, "通過": 通過, "上り": 上り, "単勝": 単勝, "人気": 人気, "馬体重": 馬体重, "賞金": 賞金,
            "芝ダート": shiba_dirt, "距離": kyori, "天候": tenkou, "馬場": baba
        }
        results.append(race_row)
    return results

def scrape_race_details(input_csv: str, config: dict) -> None:
    """
    個別レースURLからデータをスクレイピングし、CSVに保存する。
    
    Args:
        input_csv (str): 個別レースURLが記載されたCSVファイルパス
        config (dict): 設定辞書
    """
    wait_time = config.get('wait_time', 1)
    min_wait = config.get('min_wait')
    max_wait = config.get('max_wait')
    
    user_agent = config.get('user_agent')
    output_dir = config['output_dir']
    base_url = config['urls']['race_detail_base'] # https://db.netkeiba.com/race/
    
    # input_csvからファイル名を推測して出力ファイル名を決定する
    filename = os.path.basename(input_csv)
    if "individual_race_urls_" in filename:
        year = filename.replace("individual_race_urls_", "").replace(".csv", "")
        output_filename = config['filenames']['race_data'].format(year=year)
    elif "_individual" in filename:
        output_filename = filename.replace("_individual.csv", "_data.csv")
    else:
        output_filename = filename.replace(".csv", "_data.csv")

    output_path = os.path.join(output_dir, output_filename)
    
    # 入力ファイルの読み込み
    try:
        with open(input_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None) # ヘッダー
            race_urls = [row[0] for row in reader if row]
    except FileNotFoundError:
        print(f"入力ファイルが見つかりません: {input_csv}")
        return

    # FIXED_HEADER definition
    FIXED_HEADER = [
        "key", "開催日", "開催場", "クラス", "着順", "枠番", "馬番", "馬名", "性齢", "斤量", "騎手", "タイム", "着差", "通過", "上り", "単勝", "人気", "馬体重", "賞金", "芝ダート", "距離", "天候", "馬場"
    ]

    total = len(race_urls)
    print(f"{total}件のレースデータをスクレイピングします。")
    print(f"出力先: {output_path}")

    # ディレクトリ作成
    os.makedirs(output_dir, exist_ok=True)

    driver = None
    try:
        driver = initialize_driver(user_agent)
        
        for idx, url in enumerate(race_urls, 1):
            race_id = extract_race_id_from_url(url)
            if not race_id:
                print(f"- スキップ ({idx}/{total}): race_idが抽出できませんでした: {url}")
                continue
                
            print(f"- 処理中 ({idx}/{total}): {race_id}")
            
            # DB URLを構築してスクレイピング
            target_url = f"{base_url}{race_id}/"
            data = scrape_keiba_page(driver, target_url, race_id)
            
            if data:
                # ヘッダー情報のマージ（予期せぬカラム対応）
                all_keys = set()
                for row in data:
                    all_keys.update(row.keys())
                header = FIXED_HEADER[:]
                for k in all_keys:
                    if k not in header:
                        header.append(k)
                
                # 追記モードで書き込み
                write_header = not os.path.exists(output_path)
                try:
                    with open(output_path, 'a', newline='', encoding='utf-8-sig') as f:
                        writer = csv.DictWriter(f, fieldnames=header)
                        if write_header:
                            writer.writeheader()
                        writer.writerows(data)
                except IOError as e:
                    print(f"  ファイル書き込みエラー: {e}")
            
            # 待機時間の決定
            if min_wait is not None and max_wait is not None:
                try:
                    sleep_time = random.uniform(float(min_wait), float(max_wait))
                except (ValueError, TypeError):
                    sleep_time = float(wait_time)
            else:
                sleep_time = float(wait_time)

            time.sleep(sleep_time) # 待機
            
    except KeyboardInterrupt:
        print("\nスクレイピングが中断されました。")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
    finally:
        if driver:
            driver.quit()
    
    print("スクレイピングプロセスが終了しました。")
