# Spec: Pipeline Controller

## Status
Status: Proposed

## Context
The `pipeline_controller` (implemented as `run_scraping.py`) is the entry point for the new scraping system. It orchestrates the execution of the three scraper modules based on command-line arguments and a configuration file. It provides a unified interface for running the entire scraping process or specific parts of it.

## Requirements

### Requirement: Command Line Interface
The controller must accept command-line arguments to control execution.

- **GIVEN** the script is run from the terminal
- **WHEN** arguments are parsed
- **THEN** it should support `--config` to specify a custom config file path (defaulting to `scrape/config/scraping_config.yaml`)
- **AND** support `--step` to specify which steps to run (`calendar`, `race_list`, `race_detail`, or `all`)
- **AND** support `--years` to override the target years (comma-separated).

### Requirement: Load Configuration
The controller must load and merge configuration settings.

- **GIVEN** a configuration file exists
- **WHEN** the script starts
- **THEN** it should load the YAML configuration
- **AND** override the `years` setting if the `--years` argument was provided
- **AND** validate that essential settings (like `output_dir`) are present.

### Requirement: Orchestration Logic
The controller must execute the correct modules in the correct order.

- **GIVEN** the configured steps and years
- **WHEN** execution begins
- **THEN** it should iterate through each specified year
- **AND** for each year, execute the enabled steps in order:
    1. **Calendar Step**: Call `calendar_scraper` module.
    2. **Race List Step**: Call `race_list_scraper` module, passing the output from the previous step as input if available/applicable.
    3. **Race Detail Step**: Call `race_detail_scraper` module, passing the output from the previous step.
- **AND** print clear headers/separators in the output between steps and years.

### Requirement: Error Handling
The controller must manage errors during the pipeline execution.

- **GIVEN** an error occurs in one of the steps
- **WHEN** it is caught
- **THEN** it should print a descriptive error message
- **AND** default behavior should be to stop execution for that year/step to prevent cascading errors (e.g., trying to scrape details when the list generation failed), or follow a configured `stop_on_error` policy. (For this refactor, stopping on major step failure is appropriate).
