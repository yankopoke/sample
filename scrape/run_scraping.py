
import os
import sys
import argparse
import yaml
from modules import calendar_scraper, race_list_scraper, race_detail_scraper

def load_config(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"設定ファイルが見つかりません: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"設定ファイルの解析エラー: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="netkeiba scraping pipeline")
    parser.add_argument('--config', default='scrape/config/scraping_config.yaml', help='Path to configuration file')
    parser.add_argument('--step', choices=['calendar', 'race_list', 'race_detail', 'all'], default='all', help='Step to execute')
    parser.add_argument('--years', help='Target years (comma-separated, e.g., 2020,2021)')
    
    args = parser.parse_args()
    
    # パス解決（プロジェクトルートからの相対パスを想定）
    config_path = os.path.abspath(args.config)
    config = load_config(config_path)
    
    # 年度のオーバーライド
    if args.years:
        config['years'] = [int(y.strip()) for y in args.years.split(',')]
    
    target_years = config['years']
    output_dir = config['output_dir']
    filenames = config['filenames']
    
    # 実行ステップの決定
    steps_to_run = []
    if args.step == 'all':
        if config['steps']['calendar']: steps_to_run.append('calendar')
        if config['steps']['race_list']: steps_to_run.append('race_list')
        if config['steps']['race_detail']: steps_to_run.append('race_detail')
    else:
        steps_to_run.append(args.step)
        
    print(f"--- Scraping Pipeline Start ---")
    print(f"Target Years: {target_years}")
    print(f"Steps: {steps_to_run}")
    print(f"Config: {config_path}")
    print("-" * 30)
    
    for year in target_years:
        print(f"\n>>> Processing Year: {year} <<<")
        
        # ファイルパスの解決
        race_links_file = os.path.join(output_dir, filenames['race_links'].format(year=year))
        individual_urls_file = os.path.join(output_dir, filenames['individual_urls'].format(year=year))
        
        try:
            # Step 1: Calendar Scraper
            if 'calendar' in steps_to_run:
                print(f"\n[Step 1] Running Calendar Scraper for {year}...")
                calendar_scraper.scrape_calendar(year, config)
                
            # Step 2: Race List Scraper
            if 'race_list' in steps_to_run:
                print(f"\n[Step 2] Running Race List Scraper for {year}...")
                # 入力ファイルの存在確認（単独実行時など）
                if not os.path.exists(race_links_file):
                    if 'calendar' not in steps_to_run:
                        print(f"Error: 必要な入力ファイルが見つかりません: {race_links_file}")
                        print("calendarステップを実行してファイルを生成するか、パスを確認してください。")
                        continue
                    else:
                         # カレンダーステップが失敗してファイルが生成されなかった場合
                         print(f"Error: カレンダーステップ後の入力ファイルが見つかりません: {race_links_file}")
                         continue
                         
                race_list_scraper.scrape_race_list(race_links_file, config)
                
            # Step 3: Race Detail Scraper
            if 'race_detail' in steps_to_run:
                print(f"\n[Step 3] Running Race Detail Scraper for {year}...")
                # 入力ファイルの存在確認
                if not os.path.exists(individual_urls_file):
                     print(f"Error: 必要な入力ファイルが見つかりません: {individual_urls_file}")
                     continue
                     
                race_detail_scraper.scrape_race_details(individual_urls_file, config)
                
        except Exception as e:
            print(f"\n!!! Error processing year {year}: {e}")
            # エラーが発生しても次の年度の処理は続行するポリシーにするか、ここで完全に停止するか
            # ここではその年度の処理を中断し、次の年度へ進む
            continue

    print("\n--- Scraping Pipeline Completed ---")

if __name__ == "__main__":
    # モジュール検索パスを追加（scrapeディレクトリがルートの場合の対策）
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    main()
