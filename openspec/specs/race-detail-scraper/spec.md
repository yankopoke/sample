# Spec: Race Detail Scraper

## Status
Status: Proposed

## Context
The `race_detail_scraper` module is responsible for scraping detailed race data from individual race pages. It replaces `scrape_keiba_selenium.py`. This module will be designed to work with the new configuration system and can be invoked as part of the pipeline or independently. It uses Selenium to handle dynamic content if necessary, though the primary focus is on robust data extraction from the new pipeline's inputs.

## Requirements

### Requirement: Process Input CSV
The scraper must read individual race URLs from an input CSV file.

- **GIVEN** an input CSV file path containing a list of race URLs
- **WHEN** the scraper is started
- **THEN** it should read the file
- **AND** ignore the header row
- **AND** extract the URLs from the first column.

### Requirement: Initialize Browser Driver
The scraper must manage the Selenium WebDriver instance.

- **GIVEN** the scraper needs to access web pages
- **WHEN** initialization occurs
- **THEN** it should launch a headless Chrome browser (or configured browser)
- **AND** set appropriate options (like `headless`, `disable-gpu`, user-agent)
- **AND** ensure the driver is properly closed when scraping is complete or if an error occurs.

### Requirement: Scrape Race Details
The scraper must extract specific data points from each race page.

- **GIVEN** a race page URL
- **WHEN** the page is loaded
- **THEN** it should extract race information (race name, distance, weather, track condition)
- **AND** extract horse information for every horse in the race (rank, frame, horse number, horse name, jockey, time, odds, etc.)
- **AND** extract payoff/dividend information if available.
- **AND** handle cases where data might be missing gracefully.

### Requirement: Output Data
The scraper must save the extracted data.

- **GIVEN** extracted data from a race
- **WHEN** processing is complete for a race
- **THEN** it should append the data to a result file (CSV or Database as per existing logic, but configured via the new settings)
- **AND** ensure data integrity (correct columns, encoding).
- **Note**: For this refactor, we will maintain the existing CSV/DB output format to ensure backward compatibility with downstream tools, but the output path will be configurable.

### Requirement: Robustness and configuration
The scraper must respect configuration for timing and reliability.

- **GIVEN** a list of URLs to process
- **WHEN** iterating through them
- **THEN** it should sleep for `wait_time` between requests
- **AND** log progress to stdout (e.g., "Processing 1/100...")
- **AND** catch and report errors for individual pages without crashing the entire batch process.
