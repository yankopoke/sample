# Proposal: Refactor Scraping Pipeline

## Problem Statement

現在のスクレイピングプログラムは以下の課題があります:

1. **分散した実行フロー**: 3つの独立したスクリプトを順番に実行する必要があり、手動での管理が必要
2. **ハードコードされた設定**: 年度、ファイル名、URLなどがスクリプト内に直接記述されている
3. **柔軟性の欠如**: 特定のステップだけを実行したい場合でも、スクリプト全体を修正する必要がある
4. **保守性の低さ**: 設定変更のたびにコードを編集する必要がある

### 現在の構成

```
get_race_links.py
  ↓ race_links_YYYY.csv
get_individual_race_urls_ajax.py
  ↓ individual_race_urls_YYYY.csv
scrape_keiba_selenium.py
  ↓ データベース/CSV出力
```

## Proposed Solution

スクレイピングパイプラインを以下のように再構成します:

### 1. モジュール化されたコンポーネント設計

各スクレイピングステップを独立したモジュールとして実装:
- `calendar_scraper.py`: カレンダーからレース一覧URLを取得
- `race_list_scraper.py`: レース一覧から個別レースURLを取得
- `race_detail_scraper.py`: 個別レースの詳細データを取得

### 2. 統合パイプライン実行スクリプト

`run_scraping.py`: 設定ファイルに基づいて、単独または一括実行を制御
- 全ステップを順次実行
- 特定のステップのみを実行
- 複数年度の一括処理

### 3. 設定ファイル (YAML/JSON)

`scraping_config.yaml`:
```yaml
# 対象年度
years: [2020, 2021, 2022]

# 出力ディレクトリ
output_dir: "./scrape/data"

# 各ステップの有効/無効
steps:
  calendar: true
  race_list: true
  race_detail: true

# 待機時間（秒）
wait_time: 1

# ファイル名テンプレート
filenames:
  race_links: "race_links_{year}.csv"
  individual_urls: "individual_race_urls_{year}.csv"
  race_data: "race_data_{year}.csv"
```

### 4. 実行例

```bash
# 全ステップを実行
python run_scraping.py

# 特定のステップのみ実行
python run_scraping.py --step calendar
python run_scraping.py --step race_list
python run_scraping.py --step race_detail

# 特定の年度のみ
python run_scraping.py --years 2023

# 設定ファイルを指定
python run_scraping.py --config custom_config.yaml
```

## Impact

### Modified Capabilities

- **`scrape/get_race_links.py`**: モジュール化され、`calendar_scraper.py`として再実装
- **`scrape/get_individual_race_urls_ajax.py`**: モジュール化され、`race_list_scraper.py`として再実装
- **`scrape/scrape_keiba_selenium.py`**: モジュール化され、`race_detail_scraper.py`として再実装

### New Capabilities

- **`scrape/run_scraping.py`**: パイプライン全体を制御する統合スクリプト
- **`scrape/scraping_config.yaml`**: 保守性の高い設定ファイル
- **`scrape/modules/`**: 各スクレイピング機能を含むモジュールディレクトリ

### Benefits

1. **柔軟な実行**: 必要なステップだけを選択的に実行可能
2. **保守性向上**: 設定変更時にコードを触る必要がない
3. **再利用性**: 各モジュールが独立しており、他のプロジェクトでも利用可能
4. **拡張性**: 新しいスクレイピングステップの追加が容易

## Non-Goals

- エラーハンドリングの強化（既存の基本的なエラー処理は維持）
- ログ機能の追加
- データベーススキーマの変更
- スクレイピングロジックの大幅な変更
