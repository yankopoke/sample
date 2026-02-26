## ADDED Requirements

### Requirement: Categorization of new data fields for ML
The system SHALL categorize each newly identified data field into feature types (numerical, categorical, time-series).

#### Scenario: Categorize pedigree data
- **WHEN** a new field "Sire" is identified
- **THEN** the system MUST categorize it as a categorical feature for embedding or one-hot encoding.

### Requirement: Definition of feature importance hypothesis
The system SHALL define a hypothesis for how each new feature is expected to improve the prediction of race outcomes.

#### Scenario: Hypothesize impact of lap times
- **WHEN** including "last 3-furlong pace" as a feature
- **THEN** the system MUST describe how it helps distinguish late-stage burst capability from overall speed.
