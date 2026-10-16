# Lab 5: Static Code Analysis — Issues Found and Fixed

**File:** `library_system.py`
**Student:** Tanishk Gowda (PES1UG24AM301)

## Scores

| Tool | Before | After |
|------|--------|-------|
| Pylint | 6.07/10 | 10.00/10 |
| Bandit | 2 issues (1 Medium, 1 Low) | No issues identified |
| Flake8 | 14 issues | 0 issues |

## Issue Table

| # | Issue | Type | Line(s) | Description | Fix Approach |
|---|-------|------|---------|-------------|--------------|
| 1 | Use of `eval()` (Bandit B307, Pylint W0123) | Security (Medium) | 45 | `fine_from_rule` runs `eval()` on a string, so any Python code passed as a rule would be executed. | Replaced `eval` with a small `ast`-based evaluator that only allows numbers, the name `days`, and `+`, `-`, `*`. Anything else raises `ValueError`. |
| 2 | Bare `except: pass` (Bandit B110, Pylint W0702, Flake8 E722) | Security / Bug (Low) | 20–22 | `return_book` swallowed every exception silently, hiding failed returns and real errors. | Catch only `KeyError` and `ValueError` and print a message saying the loan was not found. |
| 3 | Mutable default argument `dates=[]` (Pylint W0102) | Bug | 9 | The same list was shared across every call, so the "loan dates on record" count kept growing across different students (1, 2, 3). | Default changed to `None`; dates are now kept per student in a `loan_dates` dictionary. |
| 4 | `global FINE_PER_DAY` modified in `renewBook` (Pylint W0603) | Bug | 27–30 | Renewing one book for more than 14 days permanently raised the fine rate for every student (fine for 5 days became 15 instead of 10). | `renew_book` no longer changes the constant; it returns the rate for that loan, and `calculate_fine` takes the rate as a parameter. |
| 5 | `global loans` reassigned in `load_records` (Pylint W0603) | Code quality | 35 | Reassigning a global inside a function makes the state hard to follow. | Update the existing dictionary with `loans.clear()` and `loans.update(...)` instead. |
| 6 | `open()` without `with` or encoding (Pylint R1732, W1514) | Code quality | 34, 40 | Files might not close if an error occurs, and the encoding depends on the OS. | Use `with open(file, ..., encoding="utf-8")` and `json.load` / `json.dump`. |
| 7 | Negative fines | Logic bug (not flagged by tools) | 24–25 | `calculate_fine(-3)` returned -9. | Clamp days with `max(days_overdue, 0)`. |
| 8 | Book ID stored as an integer | Logic bug (not flagged by tools) | 57 | `4521` was saved as an int while other IDs were strings. | Convert IDs with `str(book_id)` in `add_book_loan`. |
| 9 | Crash on non-numeric input | Logic bug (not flagged by tools) | 62–63 | Typing `abc` at the prompt raised `ValueError` from `int()`. | Added `read_days()`, which validates input and falls back to 0. |
| 10 | Empty student ID ignored silently | Logic bug (not flagged by tools) | 10–11 | A loan with no student ID was dropped with no message. | Print a message explaining why the loan was not recorded. |
| 11 | Unused `import os` (Pylint W0611, Flake8 F401) | Style | 2 | Imported but never used. | Removed. |
| 12 | Function name `renewBook` (Pylint C0103) | Style | 27 | Not in snake_case. | Renamed to `renew_book`. |
| 13 | Missing docstrings (Pylint C0114, C0116) | Style | 1 and all functions | No module or function docstrings. | Added a module docstring and a docstring for each function. |
| 14 | `%` string formatting and concatenation (Pylint C0209) | Style | 14, 31 | Old-style formatting is harder to read. | Switched to f-strings. |
| 15 | Line too long (Flake8 E501) | Style | 14, 31 | Lines were 90 and 91 characters (limit 79). | Split the f-strings across two lines. |
| 16 | Missing blank lines (Flake8 E302, E305) | Style | 9–68 | Only one blank line between top-level functions. | Two blank lines between all top-level definitions. |
| 17 | `main()` runs on import | Code quality | 68 | Importing the module would run the whole demo. | Wrapped in `if __name__ == "__main__":`. |

## Commits

1. **Bandit fixes:** removed `eval` (issue 1) and the bare `try/except/pass` (issue 2).
2. **Pylint fixes:** issues 3–14, including the logic bugs found by running the program.
3. **Flake8 fixes:** line length, blank lines and the `__main__` guard (issues 15–17).
