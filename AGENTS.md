# Antigravity Development Rules — NSE/BSE Pump-and-Dump Early Detector

**Purpose:** These rules are mandatory engineering standards for every feature, module, API, data pipeline, machine-learning component, test, and UI screen generated or modified by Antigravity in this repository.

---

## 1. Core Engineering Principles
1. Build modular, reusable, maintainable, and production-minded code.
2. Prefer dynamic and data-driven implementations over static or hardcoded logic.
3. Follow DRY (Don't Repeat Yourself). Do not duplicate logic, validations, constants, transformations, or UI components.
4. Follow Single Responsibility Principle: each function, class, and module should have one clear purpose.
5. Keep implementation simple. Do not introduce unnecessary abstractions, frameworks, dependencies, or design patterns.
6. Make changes consistent with the existing project architecture and conventions.
7. Do not generate placeholder implementations, fake data, mock success responses, or unfinished TODOs in production paths unless explicitly requested.
8. Never claim a feature works until it has been executed and verified.

## 2. Function and Class Size
1. **Target:** Each function should contain no more than 30 lines of executable code.
2. Keep functions focused and easy to test. Extract cohesive helper functions when a function grows beyond 30 lines.
3. Do not split code artificially into tiny functions that make the flow harder to understand. Each helper must have a meaningful responsibility.
4. Keep class responsibilities narrow. Avoid large "manager", "utility", or "god" classes.
5. Use clear names that describe intent and behaviour.
6. Add type hints to function parameters and return values.
7. Add docstrings to public functions, classes, API endpoints, and complex logic.

> **Line-count interpretation:** Count executable statements, excluding blank lines, comments, and docstrings. If a function must exceed 30 executable lines for a well-justified reason, explain why in the implementation notes and keep it as small as practical.

## 3. Dynamic, Configurable, Data-Driven Code
1. Do not hardcode file paths, stock symbols, dates, thresholds, API URLs, credentials, model parameters, or environment-specific settings.
2. Put configurable values in environment variables, validated configuration files, or database records as appropriate.
3. Provide sensible defaults, but make important thresholds and settings configurable.
4. Discover datasets recursively from configured dataset directories. Do not assume a fixed number of folders or files.
5. Support new NSE/BSE dataset folders and supported files without requiring code changes for every new folder.
6. Use schema detection or explicit, configurable column mappings to handle variations in source column names.
7. Validate file type, required columns, date formats, numeric values, and data quality before processing.
8. Make ingestion idempotent: re-running a dataset import should not create duplicate records.
9. Handle missing, malformed, empty, duplicate, and partially corrupted files safely. Log clear reasons and continue with other valid files where appropriate.
10. Do not silently guess ambiguous columns or data meanings. Report the ambiguity and require a mapping or configuration.

## 4. Reusability and DRY
1. Before creating a new function or component, search the repository for existing functionality that can be reused.
2. Keep shared logic in appropriate modules, such as configuration, logging, validation, data access, feature engineering, and common UI components.
3. Do not copy-paste similar logic across NSE, BSE, or other dataset sources. Use source adapters or configurable mappings.
4. Centralize constants and shared schemas. Avoid scattering the same values throughout the codebase.
5. Reuse API clients, database sessions, validators, chart components, and error-handling utilities.
6. Avoid circular imports and unclear dependencies between modules.

## 5. Project Architecture
Keep responsibilities separated:
- **Data ingestion:** discover, read, validate, normalize, and import datasets.
- **Data processing:** clean data, handle missing values, deduplicate, and standardize records.
- **Feature engineering:** calculate price, volume, volatility, rolling-window, and other approved features.
- **ML models:** train, load, version, and run anomaly-detection models.
- **Detection/scoring:** combine model outputs and configured rules transparently.
- **Backend/API:** expose validated services through FastAPI.
- **Database:** own models, migrations, repositories, and transactions.
- **Frontend:** display API-backed data and reusable components.
- **Tests:** verify individual units, integrations, data quality, and end-to-end workflows.

Do not place the entire application in one file. Do not mix database queries, ML logic, business rules, and HTTP response formatting in the same function.

## 6. Python and FastAPI Standards
1. Use Python type hints and Pydantic schemas for request and response validation.
2. Keep route handlers thin. Put business logic in service modules.
3. Use dependency injection for database sessions and shared services.
4. Use parameterized database queries or a safe ORM. Never build SQL by concatenating untrusted input.
5. Handle errors with appropriate exception types and consistent API error responses.
6. Use async endpoints only when the operations and libraries support asynchronous execution.
7. Do not block the event loop with long-running ML training or heavy file processing. Use background workers or suitable job execution.
8. Validate upload size, file extension, content, and access permissions.
9. Keep secrets out of source code and logs.
10. Add database migrations for schema changes; do not rely on manually editing production tables.

## 7. Dataset Ingestion and Processing Rules
1. Recursively scan configured dataset directories, including nested folders.
2. Initially support only explicitly implemented formats (for example CSV and XLSX); add PDF parsing only through a dedicated, tested extraction pipeline.
3. Use source-specific adapters where NSE, BSE, and SEBI files have different structures.
4. Preserve source filename, source type, import timestamp, and relevant provenance metadata.
5. Normalize column names and data types into a documented internal schema.
6. Store raw source files separately from cleaned/normalized data when appropriate.
7. Record import status, rejected rows, validation errors, and processing summaries.
8. Never treat every PDF or spreadsheet as stock OHLCV data. Identify its document/data type before selecting a parser.
9. Do not overwrite raw input files.
10. Make processing repeatable and auditable.

## 8. Machine-Learning and Research Integrity
1. Establish a simple baseline before introducing complex models.
2. Keep training, validation, and test data separated chronologically to avoid time-series leakage.
3. Fit preprocessing steps only on training data; apply the fitted transformations to later periods.
4. Do not use future information when generating historical predictions or backtests.
5. Handle class imbalance and rare manipulation events explicitly.
6. Treat SEBI enforcement cases as weak labels unless the event dates and affected securities are verified.
7. Do not label an unusual price/volume movement as proven manipulation. Use terms such as anomaly, suspicious pattern, or surveillance alert.
8. Store model version, training period, feature set, configuration, and evaluation metrics with each model.
9. Make anomaly scores and thresholds explainable and configurable.
10. Evaluate false positives, precision, recall, and detection delay where labels permit. State limitations when reliable labels are unavailable.
11. Never fabricate model accuracy, evaluation results, or historical detections.
12. Keep training code separate from inference code.

## 9. Database and Data Integrity
1. Use consistent naming conventions and explicit constraints.
2. Add indexes based on actual query patterns, especially for symbol and trading date.
3. Use unique constraints or idempotency keys to prevent duplicate imports.
4. Use transactions for multi-step writes.
5. Store timestamps consistently and document the timezone used for market dates.
6. Use migrations for all schema changes.
7. Avoid loading the entire historical dataset into memory when chunked or incremental processing is practical.

## 10. Frontend Standards
1. Build reusable React components; do not duplicate page layouts or chart logic.
2. Keep API calls in a dedicated service/client layer rather than scattering fetch logic across components.
3. Use environment variables for backend URLs and environment-specific settings.
4. Render real API data. Do not hardcode stock lists, alert counts, charts, or model results as if they were live.
5. Include loading, empty, error, and success states.
6. Validate user inputs and show useful messages.
7. Make tables, filters, charts, and alert details reusable and configurable.
8. Ensure charts clearly identify the symbol, exchange, date range, price units, and volume units.
9. Do not imply that an alert is a confirmed case of manipulation.

## 11. Security and Configuration
1. Never commit API keys, passwords, tokens, private certificates, or database credentials.
2. Provide a `.env.example` containing placeholder variable names only.
3. Validate configuration at application startup and fail clearly when required settings are missing.
4. Use least-privilege database and service credentials.
5. Restrict file uploads to approved directories and prevent path traversal.
6. Do not expose stack traces, secrets, or internal paths in public API responses.
7. Keep dependencies minimal and review their purpose before adding them.

## 12. Logging and Observability
1. Use Python's logging framework or the project's established structured logger.
2. Do not use scattered `print()` statements for application logging.
3. Include useful context such as dataset filename, source, symbol, date range, job ID, and model version where applicable.
4. Never log credentials or sensitive tokens.
5. Log failures with enough detail to debug them, without hiding the original exception.
6. Track ingestion counts, rejected rows, processing duration, model version, and detection summaries.

## 13. Testing and Verification
For each feature:
1. Add unit tests for business logic and edge cases.
2. Add integration tests for database, API, and ingestion workflows where relevant.
3. Test empty files, invalid schemas, missing values, duplicate records, and unexpected folder structures.
4. Test that adding a new supported dataset file does not require changing application code.
5. Test chronological splits and leakage-sensitive ML workflows.
6. Run formatting, linting, type checks, and relevant tests after changes.
7. Do not weaken or delete tests merely to make a build pass.
8. Report the exact commands executed and whether they passed.
9. If a test cannot be run, state why; do not claim it passed.

## 14. Antigravity Workflow — Mandatory Before and After Coding
### Before implementation:
1. Inspect the repository structure and existing code.
2. Read the README, configuration, dependencies, and relevant modules.
3. Identify reusable code and existing conventions.
4. Write a short implementation plan listing files to create or modify.
5. Identify data assumptions, risks, and required configuration.
6. Ask for clarification only when an essential requirement is genuinely ambiguous. Do not invent business requirements.

### During implementation:
1. Work in small, logically complete steps.
2. Modify only files needed for the task.
3. Preserve existing working functionality and backward compatibility unless a change is explicitly required.
4. Follow the 30-line function target, modularity, DRY, and dynamic-configuration rules.
5. Do not replace real functionality with placeholders or hardcoded demo data.
6. Keep dependencies and architecture consistent across modules.

### After implementation:
1. Review the diff for duplication, hardcoding, oversized functions, dead code, and security issues.
2. Run relevant tests and checks.
3. Fix regressions introduced by the change.
4. Update documentation, configuration examples, and tests.
5. Provide a concise report: files changed, functionality implemented, configuration required, commands run, test results, and known limitations.

## 15. Definition of Done
A task is complete only when:
- The implementation follows the architecture and coding standards in this document.
- Functions meet the 30-line target or have a documented exception.
- No unnecessary duplication or environment-specific hardcoding remains.
- Inputs and outputs are validated.
- Errors are handled and logged appropriately.
- Relevant tests have been added and executed, or execution limitations are disclosed.
- Documentation and configuration examples are updated.
- The feature uses real data and real integrations where required.
- Limitations and assumptions are clearly reported.

---

## Instruction to Antigravity
Treat this file as the repository-wide engineering rulebook. Read it before starting any task. Follow it for all generated and modified code, not just new files. If a user request conflicts with these standards, explain the conflict and ask for direction when it materially affects correctness, security, or maintainability. Never silently ignore these rules.
