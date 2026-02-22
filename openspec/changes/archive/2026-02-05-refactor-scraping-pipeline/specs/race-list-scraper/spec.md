# Spec: Race List Scraper

## Status
Status: Proposed

## Context
The `race_list_scraper` module is responsible for fetching individual race URLs given a list of race meeting (kaisai) URLs. It replaces `get_individual_race_urls_ajax.py`, refactoring it into a reusable module. It iterates through the provided list of race meeting URLs, mimics an AJAX request to netkeiba to retrieve the race list for that meeting, scrapes the individual race links, and extracts them to a CSV file.

## Requirements

### Requirement: Process Input CSV
The scraper must read race meeting URLs from an input CSV file.

- **GIVEN** an input CSV file path containing a list of URLs
- **WHEN** the scraper is executed
- **THEN** it should read the file
- **AND** ignore the header row
- **AND** extract the URLs from the first column.

### Requirement: Fetch Race Lists via AJAX
The scraper must retrieve race lists using the site's AJAX endpoint to ensure all data is loaded.

- **GIVEN** a race meeting URL (e.g., `.../race_list.html?kaisai_date=202001050601`)
- **WHEN** processing the URL
- **THEN** it should extract the `kaisai_date` query parameter
- **AND** construct a request to `https://race.netkeiba.com/top/race_list_sub.html` with `kaisai_date`
- **AND** include the `X-Requested-With: XMLHttpRequest` header
- **AND** use the configured `cp932` encoding for the response.

### Requirement: Extract Individual Race URLs
The scraper must parse the AJAX response to find links to specific races.

- **GIVEN** a successful response from the AJAX endpoint
- **WHEN** parsing the HTML content
- **THEN** it should find 12 URLs (typically) matching the pattern `race/result.html?race_id=`
- **AND** convert them to absolute URLs (base: `https://race.netkeiba.com/`)
- **AND** add them to the collection of found links.

### Requirement: CSV Output
The scraper must save the accumulated individual race URLs to a file.

- **GIVEN** a list of found individual race URLs
- **WHY** meaningful analysis requires unique race IDs
- **THEN** it should remove duplicates
- **AND** sort the URLs
- **AND** write them to the specified output CSV file with a header row `url`.

### Requirement: Error Handling and Rate Limiting
The scraper must handle errors gracefully and respect server load.

- **GIVEN** a network error or parsing error occurs
- **THEN** it should print an error message and continue to the next URL
- **AND** it should sleep for a configured `wait_time` between requests to avoid overwhelming the server.
