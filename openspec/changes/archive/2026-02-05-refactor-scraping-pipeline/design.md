# Design: Refactor Scraping Pipeline

## Context

現在のスクレイピングシステムは3つの独立したスクリプトで構成されており、手動で順次実行する必要があります。この設計では、モジュール化とYAML設定ファイルを導入し、単独実行と一括実行の両方をサポートする柔軟なパイプライン構造に再構成します。

## Architecture Overview

### Directory Structure

```
scrape/
├── config/
│   └── scraping_config.yaml          # 設定ファイル
├── modules/
│   ├── __init__.py
│   ├── calendar_scraper.py           # ステップ1: カレンダースクレイパー
│   ├── race_list_scraper.py          # ステップ2: レース一覧スクレイパー
│   └── race_detail_scraper.py        # ステップ3: レース詳細スクレイパー
├── run_scraping.py                    # 統合実行スクリプト
└── data/                              # 出力データディレクトリ
    ├── race_links_{year}.csv
    ├── individual_race_urls_{year}.csv
    └── race_data_{year}.csv
```

### Component Design

#### 1. Configuration Module (`scraping_config.yaml`)

YAML形式で以下の設定を管理:

```yaml
# 対象年度（リスト形式で複数年対応）
years: [2020, 2021, 2022]

# 出力ディレクトリ
output_dir: "./scrape/data"

# 各ステップの有効/無効
steps:
  calendar: true
  race_list: true
  race_detail: true

# リクエスト間の待機時間（秒）
wait_time: 1

# User-Agent設定
user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"

# ファイル名テンプレート（{year}プレースホルダー使用）
filenames:
  race_links: "race_links_{year}.csv"
  individual_urls: "individual_race_urls_{year}.csv"
  race_data: "race_data_{year}.csv"

# URL設定
urls:
  calendar_base: "https://race.netkeiba.com/top/calendar.html"
  race_list_ajax: "https://race.netkeiba.com/top/race_list_sub.html"
  race_detail_base: "https://db.netkeiba.com/race/"
```

#### 2. Module: `calendar_scraper.py`

**責務**: netkeibaカレンダーからレース一覧ページのURLを取得

**主要関数**:
```python
def scrape_calendar(year: int, config: dict) -> list[str]:
    """
    指定年度の全月からレース一覧URLを取得
    
    Args:
        year: 対象年度
        config: 設定辞書
    
    Returns:
        レース一覧URLのリスト
    """
```

**処理フロー**:
1. 1月〜12月まで順次カレンダーページにアクセス
2. `race_list.html?kaisai_date=`を含むリンクを抽出
3. 重複を除去してソート
4. CSVファイルに出力

**既存コードからの移行**:
- `get_race_links.py`の`get_race_links_from_calendar()`関数を再利用
- ハードコードされた値を設定ファイルから読み込むように変更
- 出力処理を分離して再利用可能に

#### 3. Module: `race_list_scraper.py`

**責務**: レース一覧ページから個別レースURLを取得

**主要関数**:
```python
def scrape_race_list(input_csv: str, config: dict) -> list[str]:
    """
    レース一覧CSVから個別レースURLを取得
    
    Args:
        input_csv: レース一覧URLが記載されたCSVファイルパス
        config: 設定辞書
    
    Returns:
        個別レースURLのリスト
    """
```

**処理フロー**:
1. 入力CSVからレース一覧URLを読み込み
2. 各URLに対してAJAXリクエストを送信
3. `race/result.html?race_id=`を含むリンクを抽出
4. 重複を除去してソート
5. CSVファイルに出力

**既存コードからの移行**:
- `get_individual_race_urls_ajax.py`の`get_individual_urls_via_ajax()`関数を再利用
- ファイル名を設定から取得
- 入力ファイルパスを引数で受け取る

#### 4. Module: `race_detail_scraper.py`

**責務**: 個別レースページから詳細データをスクレイピング

**主要関数**:
```python
def scrape_race_details(input_csv: str, config: dict) -> None:
    """
    個別レースURLからデータをスクレイピング
    
    Args:
        input_csv: 個別レースURLが記載されたCSVファイルパス
        config: 設定辞書
    """
```

**処理フロー**:
1. 入力CSVから個別レースURLを読み込み
2. Seleniumでページにアクセス
3. レース情報、馬情報、過去成績などを抽出
4. データベースまたはCSVに保存

**既存コードからの移行**:
- `scrape_keiba_selenium.py`の既存ロジックを再利用
- ドライバー初期化を関数化
- 設定ファイルから出力先を取得

#### 5. Main Controller: `run_scraping.py`

**責務**: パイプライン全体の制御と実行

**コマンドライン引数**:
```python
--config: 設定ファイルパス（デフォルト: config/scraping_config.yaml）
--step: 実行するステップ（calendar, race_list, race_detail, all）
--years: 対象年度（カンマ区切り、例: 2020,2021）
```

**実行パターン**:

1. **全ステップ実行**:
   ```bash
   python run_scraping.py
   ```
   設定ファイルの`steps`に従って有効なステップを順次実行

2. **特定ステップのみ**:
   ```bash
   python run_scraping.py --step calendar
   python run_scraping.py --step race_list
   python run_scraping.py --step race_detail
   ```

3. **特定年度のみ**:
   ```bash
   python run_scraping.py --years 2023
   ```

4. **カスタム設定ファイル**:
   ```bash
   python run_scraping.py --config custom_config.yaml
   ```

**処理フロー**:
```python
1. 設定ファイルを読み込み
2. コマンドライン引数をパース
3. 対象年度を決定（引数 > 設定ファイル）
4. 実行するステップを決定
5. 各ステップを順次実行:
   - calendar: calendar_scraper.scrape_calendar()
   - race_list: race_list_scraper.scrape_race_list()
   - race_detail: race_detail_scraper.scrape_race_details()
6. 完了メッセージを表示
```

## Data Flow

```
[設定ファイル]
    ↓
[run_scraping.py] ← コマンドライン引数
    ↓
┌───────────────────────────────────┐
│ Step 1: calendar_scraper          │
│ Input: 年度                        │
│ Output: race_links_{year}.csv     │
└───────────────────────────────────┘
    ↓
┌───────────────────────────────────┐
│ Step 2: race_list_scraper         │
│ Input: race_links_{year}.csv      │
│ Output: individual_urls_{year}.csv│
└───────────────────────────────────┘
    ↓
┌───────────────────────────────────┐
│ Step 3: race_detail_scraper       │
│ Input: individual_urls_{year}.csv │
│ Output: DB/CSV                    │
└───────────────────────────────────┘
```

## Technical Decisions

### 1. Configuration Format: YAML

**選択理由**:
- 人間が読みやすく編集しやすい
- コメントのサポート
- ネストした構造を直感的に表現可能
- Pythonの`pyyaml`ライブラリで簡単に扱える

**代替案**:
- JSON: コメント不可、やや冗長
- TOML: Pythonでの標準サポートが弱い

### 2. Module Organization

**選択理由**:
- 各ステップを独立したモジュールに分離
- 単体テストが容易
- 他のプロジェクトでの再利用が可能
- 責務が明確

**構造**:
```
modules/
├── __init__.py              # モジュール初期化
├── calendar_scraper.py      # 独立したスクレイパー
├── race_list_scraper.py     # 独立したスクレイパー
└── race_detail_scraper.py   # 独立したスクレイパー
```

### 3. Backward Compatibility

**既存スクリプトの扱い**:
- 既存の3つのスクリプトは`bk/`ディレクトリに移動（バックアップ）
- 新しいモジュールは既存のロジックを最大限再利用
- データフォーマットは変更しない（CSV構造は維持）

### 4. Error Handling Strategy

**方針**:
- 既存の基本的なエラー処理を維持
- `try-except`で例外をキャッチし、エラーメッセージを表示
- ログ機能は追加しない（要件通り）
- 各ステップでエラーが発生しても、次のステップに影響しないよう独立性を保つ

### 5. Command-Line Interface

**ライブラリ**: `argparse`（Python標準ライブラリ）

**選択理由**:
- 追加の依存関係不要
- 十分な機能性
- ヘルプメッセージの自動生成

## Implementation Strategy

### Phase 1: Configuration & Structure
1. `config/scraping_config.yaml`を作成
2. `modules/`ディレクトリを作成
3. 既存スクリプトを`bk/`に移動

### Phase 2: Module Migration
1. `calendar_scraper.py`を実装
2. `race_list_scraper.py`を実装
3. `race_detail_scraper.py`を実装

### Phase 3: Controller Implementation
1. `run_scraping.py`を実装
2. 設定読み込み機能
3. コマンドライン引数パース
4. ステップ実行ロジック

### Phase 4: Testing & Validation
1. 各モジュールを単独で実行テスト
2. パイプライン全体の実行テスト
3. 既存データとの整合性確認

## Dependencies

**既存の依存関係を維持**:
- `requests`: HTTP リクエスト
- `beautifulsoup4`: HTML パース
- `selenium`: ブラウザ自動化
- `csv`: CSV ファイル操作（標準ライブラリ）

**新規追加**:
- `pyyaml`: YAML設定ファイルの読み込み

## Risks / Trade-offs

### Risks

1. **YAML依存の追加**: 新しい依存関係が追加されるが、軽量で広く使われているため低リスク
2. **既存スクリプトの動作変更**: モジュール化により動作が変わる可能性があるが、ロジックは再利用するため最小限

### Trade-offs

1. **初期実装コスト vs 長期保守性**: 初期の実装工数は増えるが、長期的な保守性が大幅に向上
2. **シンプルさ vs 柔軟性**: 単一スクリプトよりも複雑になるが、柔軟性と再利用性が向上

### Mitigation

- 既存のロジックを最大限再利用してリスクを低減
- 段階的な実装とテストで問題を早期発見
- 既存スクリプトをバックアップとして保持
