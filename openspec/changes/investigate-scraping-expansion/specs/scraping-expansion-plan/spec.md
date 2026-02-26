## ADDED Requirements

### Requirement: Design of extended scraping logic
The system SHALL define the logic for navigating from race results to horse/jockey detail pages without triggering bot detection.

#### Scenario: Sequential scraping with delays
- **WHEN** the scraper finishes a race result page
- **THEN** it SHALL visit linked horse detail pages with a randomized delay between 1-3 seconds.

### Requirement: Update to data storage schema
The system SHALL define the updated CSV/DB schema to accommodate the new fields.

#### Scenario: Add pedigree columns
- **WHEN** the plan is finalized
- **THEN** it MUST include a mapping of `sire_id`, `dam_id`, and `dams_sire_id` to the race result row.
