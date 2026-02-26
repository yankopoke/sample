## ADDED Requirements

### Requirement: Identification of horse pedigree fields
The system SHALL analyze the horse detail pages (e.g., https://db.netkeiba.com/horse/) to extract pedigree information.

#### Scenario: Map pedigree data
- **WHEN** analyzing the "Pedigree" (血統) table on a horse detail page
- **THEN** the system MUST extract unique horse IDs for the Sire, Dam, and Dam's Sire.
