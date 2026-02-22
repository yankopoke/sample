# Spec: Configuration Management

## Status
Status: Proposed

## Context
Centralized configuration management is crucial for the maintainability of the scraping pipeline. This specification defines the structure of the configuration file and how it should be accessed. The configuration file allows users to change scrape targets, file paths, and behavior without modifying code.

## Requirements

### Requirement: Configuration File Structure
The configuration file must be a valid YAML file with specific sections.

- **GIVEN** a `scraping_config.yaml` file
- **WHEN** it is validated
- **THEN** it must contain a `years` list
- **AND** a `steps` dictionary (boolean flags for each step)
- **AND** an `output_dir` path
- **AND** a `filenames` dictionary defining templates for output files
- **AND** a `urls` dictionary for base URLs.

### Requirement: Default Configuration
The system should have sensible defaults if specific values are missing (where applicable), but essential paths should be explicit.

- **GIVEN** a partial configuration
- **WHEN** loaded
- **THEN** it should rely on hardcoded fallback defaults for things like `wait_time` (e.g., 1 second) or `user_agent` if not provided.

### Requirement: Path Resolution
File paths in the configuration should be handled consistently.

- **GIVEN** relative paths in the configuration (e.g., `./data`)
- **WHEN** utilized by the application
- **THEN** they should be resolved relative to the execution root (typically the project root or the `scrape` directory, decided as: relative to the project root where `run_scraping.py` runs).

### Requirement: Configuration Validation
The configuration loader should warn or fail on invalid configs.

- **GIVEN** a config file with malformed YAML or missing required keys
- **WHEN** loading
- **THEN** the system should raise a clear error message indicating what is wrong (e.g., "Missing required key: output_dir").
