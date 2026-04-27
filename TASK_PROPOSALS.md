# Task Proposals from Codebase Review

## 1) Typo Fix Task

**Issue found:** In `CONTRIBUTING.md`, the example URL starts with `hhttps://` (double `h`), which is a typo and breaks the link.

**Proposed task:**
- Correct `hhttps://` to `https://` in the example link.
- Quickly validate all Markdown links in `CONTRIBUTING.md` after the fix.

**Why this matters:** Broken example links confuse contributors and reduce trust in the contribution guide.

---

## 2) Bug Fix Task

**Issue found:** `requirements.txt` pins `pywin32==307` without an environment marker. This package is Windows-only and can break `pip install -r requirements.txt` on Linux/macOS.

**Proposed task:**
- Change `pywin32==307` to `pywin32==307; platform_system == "Windows"`.
- Verify dependency resolution on Linux with `pip install -r requirements.txt` (or `pip install -r requirements.txt --dry-run` where supported).

**Why this matters:** Contributors using non-Windows environments can fail immediately during setup.

---

## 3) Documentation Discrepancy Task

**Issue found:** In the "Adding a New Prompt Engineering Technique" section of `CONTRIBUTING.md`, the example references `basic_prompt_construction.ipynb`, but the repository’s naming convention uses hyphenated filenames (e.g., `basic-prompt-structures.ipynb`). The example filename is inconsistent with actual repo naming and can mislead contributors.

**Proposed task:**
- Update the example to use an existing or convention-consistent notebook path.
- Add one sentence explicitly documenting the expected filename style (e.g., lowercase kebab-case).

**Why this matters:** Clear, accurate examples reduce onboarding errors and PR churn.

---

## 4) Test Improvement Task

**Issue found:** There is no automated check ensuring that notebook links in `README.md` remain valid as files are renamed or moved.

**Proposed task:**
- Add a lightweight test script (e.g., `tests/test_readme_links.py`) that:
  - Extracts local notebook paths referenced in README links,
  - Verifies each file exists,
  - Fails CI if a path is missing.
- Optionally add a second assertion ensuring the documented notebook count matches actual referenced notebooks.

**Why this matters:** Prevents silent documentation drift and catches broken links before merge.
