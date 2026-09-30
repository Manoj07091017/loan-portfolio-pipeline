import logging
import shutil

import pandas as pd

from ingestion.config import COLUMNS, SOURCE_FILE, STAGED_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

CHUNK_SIZE = 200_000


def main() -> None:
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(f"Source file not found: {SOURCE_FILE}")

    # Start clean so re-running never duplicates rows
    if STAGED_DIR.exists():
        shutil.rmtree(STAGED_DIR)
    STAGED_DIR.mkdir(parents=True)

    rows_written = 0
    rows_dropped = 0

    # dtype=str: keep the raw layer untyped; typing happens later in dbt staging
    reader = pd.read_csv(SOURCE_FILE, usecols=COLUMNS, dtype=str, chunksize=CHUNK_SIZE)

    for i, chunk in enumerate(reader, start=1):
        issue_month = pd.to_datetime(chunk["issue_d"], format="%b-%Y", errors="coerce")
        valid = issue_month.notna()

        rows_dropped += int((~valid).sum())
        chunk = chunk[valid].copy()
        chunk["issue_month"] = issue_month[valid].dt.strftime("%Y-%m")

        for month, group in chunk.groupby("issue_month"):
            out_file = STAGED_DIR / f"loans_{month}.csv"
            group.drop(columns="issue_month").to_csv(
                out_file, mode="a", header=not out_file.exists(), index=False
            )

        rows_written += len(chunk)
        log.info("Chunk %d done: %s rows written so far", i, f"{rows_written:,}")

    months = len(list(STAGED_DIR.glob("loans_*.csv")))
    log.info("Finished: %s rows across %d months, %d rows dropped (no valid issue date)",
             f"{rows_written:,}", months, rows_dropped)


if __name__ == "__main__":
    main()
