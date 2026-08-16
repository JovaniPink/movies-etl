# Repository guidance

## Purpose

This repository is a historical notebook and data archive. It is not a current
ETL service, reproducible Python package, or authoritative movie database.

## Canonical command

```sh
python3 scripts/check_repository.py
```

The validator uses only the Python standard library. It must never execute a
notebook, contact a source, or connect to PostgreSQL.

## Working rules

- Preserve the notebooks and saved outputs as historical evidence unless a task
  explicitly authorizes artifact migration.
- Never run database-writing cells against a database that has not been created
  specifically for disposable local testing.
- Keep credentials out of notebooks, outputs, configuration, logs, and Git.
- Do not restore the literal loopback-database credential retained in earlier
  Git history; use an untracked local value only for disposable testing.
- Treat all committed datasets as unverified third-party snapshots with
  incomplete rights and lineage evidence.
- Do not add live source calls to tests or CI.
- Stage explicit files, preserve unrelated data, and run the canonical command
  before opening or updating a pull request.
