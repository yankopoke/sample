# Spec: Calendar Scraper

## Status
Status: Proposed

## Context
The `calendar_scraper` module is responsible for fetching race list URLs from the netkeiba calendar pages. It replaces the functionality of the existing `get_race_links.py` script, modularizing it to work within the new pipeline architecture. It reads configuration for target years and output paths, executes the scraping logic, and saves the results to a CSV file.

## Requirements

### Requirement: Scrape Calendar Pages
The scraper must iterate through all months of the specified year(s) to find race list pages.

- **GIVEN** a target year is provided (e.g., 2020)
- **WHEN** the scraper is executed
- **THEN** it should iterate from month 1 to 12
- **AND** construct the URL `https://race.netkeiba.com/top/calendar.html?year={year}&month={month}`
- **AND** send an HTTP GET request with a valid User-Agent.

### Requirement: Extract Race List URLs
The scraper must parse the HTML response to find links to race lists.

- **GIVEN** a valid HTML response from the calendar page
- **WHEN** the content is parsed
- **THEN** it should find all `<a>` tags where the `href` attribute contains `race_list.html?kaisai_date=`
- **AND** convert relative URLs to absolute URLs
- **AND** collect these URLs into a list.

### Requirement: Deduplication and Sorting
The scraper must ensure unique URLs and sorted output.

- **GIVEN** a list of extracted URLs from all months
- **WHEN** processing is complete
- **THEN** it should remove any duplicate URLs
- **AND** sort the list of unique URLs.

### Requirement: CSV Output
The scraper must save the results to a CSV file.

- **GIVEN** a list of unique, sorted URLs
- **AND** a configured output directory and filename template
- **WHEN** saving the data
- **THEN** it should create the output directory if it doesn't exist
- **AND** write a CSV file with a header row `url`
- **AND** write each URL on a new line.

### Requirement: Configuration Integration
The scraper must accept configuration parameters.

- **GIVEN** a configuration dictionary
- **WHEN** the module is initialized or a function is called
- **THEN** it should read `wait_time` to sleep between requests
- **AND** use `output_dir` and `filenames` settings for file output.
