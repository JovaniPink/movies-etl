#!/usr/bin/env python3
"""Validate the Movies ETL archive without executing notebook code."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MAX_TRACKED_FILE_BYTES = 50 * 1024 * 1024
NOTEBOOKS = (
    "ETL_clean_kaggle_data.ipynb",
    "ETL_clean_wiki_movies.ipynb",
    "ETL_create_database.ipynb",
    "ETL_function_test.ipynb",
    "wiki_kaggle_etl.ipynb",
)
MOVIE_COLUMNS = (
    "adult",
    "belongs_to_collection",
    "budget",
    "genres",
    "homepage",
    "id",
    "imdb_id",
    "original_language",
    "original_title",
    "overview",
    "popularity",
    "poster_path",
    "production_companies",
    "production_countries",
    "release_date",
    "revenue",
    "runtime",
    "spoken_languages",
    "status",
    "tagline",
    "title",
    "video",
    "vote_average",
    "vote_count",
)
CSV_SCHEMAS = {
    "data/movies-metadata.csv": MOVIE_COLUMNS,
    "data/3405_6663_bundle_archive/keywords.csv": ("id", "keywords"),
    "data/3405_6663_bundle_archive/links.csv": (
        "movieId",
        "imdbId",
        "tmdbId",
    ),
    "data/3405_6663_bundle_archive/links_small.csv": (
        "movieId",
        "imdbId",
        "tmdbId",
    ),
    "data/3405_6663_bundle_archive/movies_metadata.csv": MOVIE_COLUMNS,
    "data/3405_6663_bundle_archive/ratings_small.csv": (
        "userId",
        "movieId",
        "rating",
        "timestamp",
    ),
}
WIKIPEDIA_JSON = ROOT / "data" / "wikipedia-movies.json"
POSTGRES_URL = re.compile(r"postgres(?:ql)?://[^\s\"']+", re.IGNORECASE)


class ValidationError(RuntimeError):
    """Raised when a repository invariant is not satisfied."""


def load_notebook(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValidationError(f"missing notebook: {path.relative_to(ROOT)}")
    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"invalid notebook JSON in {path.name}: {exc}") from exc
    if not isinstance(notebook, dict) or notebook.get("nbformat") != 4:
        raise ValidationError(f"{path.name} is not notebook format 4")
    cells = notebook.get("cells")
    if not isinstance(cells, list) or not cells:
        raise ValidationError(f"{path.name} has no notebook cells")
    return notebook


def validate_database_urls(path: Path, source: str) -> int:
    urls = POSTGRES_URL.findall(source)
    for url in urls:
        if "{db_password}" not in url:
            raise ValidationError(
                f"{path.name} contains a PostgreSQL URL without the db_password template"
            )
        if "@127.0.0.1:5432/movie_data" not in url:
            raise ValidationError(
                f"{path.name} contains a PostgreSQL URL outside the historical local target"
            )
    return len(urls)


def validate_csv(relative_path: str, expected_header: tuple[str, ...]) -> int:
    path = ROOT / relative_path
    if not path.is_file():
        raise ValidationError(f"missing CSV snapshot: {relative_path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        try:
            header = tuple(next(reader))
            next(reader)
        except StopIteration as exc:
            raise ValidationError(f"CSV snapshot has no data rows: {relative_path}") from exc
    if header != expected_header:
        raise ValidationError(f"unexpected CSV schema in {relative_path}: {header!r}")
    return path.stat().st_size


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_file_sizes() -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        size = path.stat().st_size
        if size > MAX_TRACKED_FILE_BYTES:
            raise ValidationError(
                f"{path.relative_to(ROOT)} is {size} bytes; limit is {MAX_TRACKED_FILE_BYTES}"
            )


def main() -> int:
    try:
        validate_file_sizes()
        notebook_results = []
        database_url_count = 0
        for name in NOTEBOOKS:
            path = ROOT / name
            notebook = load_notebook(path)
            cells = notebook["cells"]
            database_url_count += validate_database_urls(
                path, path.read_text(encoding="utf-8")
            )
            notebook_results.append((name, len(cells)))

        csv_sizes = {
            path: validate_csv(path, schema) for path, schema in CSV_SCHEMAS.items()
        }

        try:
            wikipedia_records = json.loads(WIKIPEDIA_JSON.read_text(encoding="utf-8"))
        except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValidationError(f"invalid Wikipedia JSON snapshot: {exc}") from exc
        if not isinstance(wikipedia_records, list) or not wikipedia_records:
            raise ValidationError("Wikipedia JSON snapshot is not a non-empty list")

        metadata_copy = ROOT / "data" / "movies-metadata.csv"
        bundled_metadata = (
            ROOT / "data" / "3405_6663_bundle_archive" / "movies_metadata.csv"
        )
        if sha256(metadata_copy) != sha256(bundled_metadata):
            raise ValidationError("the two historical movie-metadata copies differ")
    except ValidationError as exc:
        print(f"archive validation failed: {exc}", file=sys.stderr)
        return 1

    print("archive validation passed")
    for name, cell_count in notebook_results:
        print(f"- {name}: notebook format 4, {cell_count} cells")
    print(f"- CSV snapshots: {len(csv_sizes)} expected schemas")
    print(f"- Wikipedia records: {len(wikipedia_records)}")
    print(f"- PostgreSQL URL templates: {database_url_count}; literal credentials: 0")
    print("- duplicate movie-metadata snapshots: byte-identical")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
