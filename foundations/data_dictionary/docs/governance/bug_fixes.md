# Data Dictionary Bug Fix Log

## 2026-03-02 - Silver key uniqueness note correction
- Area: Silver dictionary generation (`silver__*.md` and `silver__*.yml` artifacts)
- Issue:
  - The generated `Data Quality Notes` line stated that the recommended primary key had zero duplicates, even for tables where the selected key candidate was not unique.
- Root cause:
  - The generator used a static success sentence instead of checking the duplicate count for the final selected key candidate.
- Fix:
  - Added conditional logic to evaluate duplicates for the chosen key and write either:
    - success (`zero duplicates`), or
    - provisional warning (`found <n> duplicate rows`).
- Impact:
  - Silver dictionary files now accurately reflect key uniqueness status in the current snapshot.
- Verification:
  - Confirmed on `silver__bea_regional_line_codes.md` (now reports duplicate rows for `line_code`).
  - Confirmed on `silver__age_base.md` (still reports zero duplicates for selected key).
