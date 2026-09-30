import argparse
import gzip
import logging
import shutil
from pathlib import Path

import boto3

from ingestion.config import AWS_PROFILE, AWS_REGION, S3_BUCKET, S3_PREFIX, STAGED_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def gzip_file(src: Path) -> Path:
    dst = src.with_suffix(".csv.gz")
    with open(src, "rb") as f_in, gzip.open(dst, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    return dst


def upload_month(s3_client, month: str) -> None:
    src = STAGED_DIR / f"loans_{month}.csv"
    if not src.exists():
        raise FileNotFoundError(f"No staged file for {month}: {src}")

    gz = gzip_file(src)
    key = f"{S3_PREFIX}/issue_month={month}/loans_{month}.csv.gz"
    s3_client.upload_file(str(gz), S3_BUCKET, key)  # same key = overwrite, so re-runs are safe
    gz.unlink()
    log.info("Uploaded s3://%s/%s", S3_BUCKET, key)


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload monthly loan files to S3")
    parser.add_argument("--start", help="First month to upload, YYYY-MM (default: earliest)")
    parser.add_argument("--end", help="Last month to upload, YYYY-MM (default: latest)")
    args = parser.parse_args()

    months = sorted(f.stem.removeprefix("loans_") for f in STAGED_DIR.glob("loans_*.csv"))
    if args.start:
        months = [m for m in months if m >= args.start]
    if args.end:
        months = [m for m in months if m <= args.end]
    if not months:
        raise SystemExit("No months matched. Did you run split_by_month first?")

    session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
    s3 = session.client("s3")

    log.info("Uploading %d months: %s to %s", len(months), months[0], months[-1])
    for month in months:
        upload_month(s3, month)
    log.info("Done.")


if __name__ == "__main__":
    main()
