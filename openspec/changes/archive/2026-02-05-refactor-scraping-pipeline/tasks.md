# Tasks: Refactor Scraping Pipeline

## 1. Environment & Config Setup
- [x] 1.1 Create new directory structure (`scrape/config`, `scrape/modules`, `scrape/bk`) and move existing scripts (`get_race_links.py`, `get_individual_race_urls_ajax.py`, `scrape_keiba_selenium.py`) to `scrape/bk` to preserve them. <!-- id: 1 -->
- [x] 1.2 Create `scrape/modules/__init__.py` to make the directory a Python package. <!-- id: 2 -->
- [x] 1.3 Implement `scrape/config/scraping_config.yaml` with the schema defined in `specs/configuration-management/spec.md`. Include default settings for years 2020-2022. <!-- id: 3 -->

## 2. Calendar Scraper Implementation
- [x] 2.1 Implement `scrape/modules/calendar_scraper.py` by refactoring logic from `bk/get_race_links.py`. <!-- id: 4 -->
- [x] 2.2 Ensure `calendar_scraper.py` reads from the passed configuration (years, output path) instead of hardcoded values. <!-- id: 5 -->
- [x] 2.3 Verify `calendar_scraper.py` correctly outputs `race_links_{year}.csv` to the configured data directory. <!-- id: 6 -->

## 3. Race List Scraper Implementation
- [x] 3.1 Implement `scrape/modules/race_list_scraper.py` by refactoring logic from `bk/get_individual_race_urls_ajax.py`. <!-- id: 7 -->
- [x] 3.2 Ensure `race_list_scraper.py` accepts an input CSV path and configuration dictionary. <!-- id: 8 -->
- [x] 3.3 Verify `race_list_scraper.py` uses the correct AJAX endpoint and headers, and outputs `individual_race_urls_{year}.csv`. <!-- id: 9 -->

## 4. Race Detail Scraper Implementation
- [x] 4.1 Implement `scrape/modules/race_detail_scraper.py` by refactoring logic from `bk/scrape_keiba_selenium.py`. <!-- id: 10 -->
- [x] 4.2 Initialize Selenium WebDriver within the module using configuration for User-Agent and headless mode options. <!-- id: 11 -->
- [x] 4.3 Ensure `race_detail_scraper.py` accepts an input CSV of race URLs and appends data to the existing output format (DB or CSV). <!-- id: 12 -->

## 5. Pipeline Controller Implementation
- [x] 5.1 Implement `scrape/run_scraping.py` using `argparse` to handle arguments (`--step`, `--years`, `--config`). <!-- id: 13 -->
- [x] 5.2 Implement the orchestration logic to load config and sequentially call the scraper modules for each requested year. <!-- id: 14 -->
- [x] 5.3 Add error handling to catch exceptions during steps and prevent cascading failures (e.g., stop year processing if calendar scrape fails). <!-- id: 15 -->

## 6. Verification
- [x] 6.1 Run `python scrape/run_scraping.py --step calendar --years 2020` and verify `race_links_2020.csv` is created. <!-- id: 16 -->
- [x] 6.2 Run `python scrape/run_scraping.py --step race_list --years 2020` and verify `individual_race_urls_2020.csv` is created. <!-- id: 17 -->
- [x] 6.3 Run `python scrape/run_scraping.py --step race_detail --years 2020` (dry run or small subset) to verify Selenium scraping works. <!-- id: 18 -->
