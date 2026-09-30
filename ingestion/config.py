import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# AWS
AWS_PROFILE = os.getenv("AWS_PROFILE", "loan-pipeline")
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
S3_BUCKET = os.environ["S3_BUCKET"]  # fail loudly if missing
S3_PREFIX = "raw/loans"

# Local paths
DATA_DIR = PROJECT_ROOT / "data"
SOURCE_FILE = DATA_DIR / "accepted_2007_to_2018Q4.csv.gz"
STAGED_DIR = DATA_DIR / "staged" / "loans"

# Source contract: the columns this pipeline ingests
COLUMNS = [
    # Loan identity and terms
    "id", "issue_d", "loan_amnt", "funded_amnt", "term", "int_rate",
    "installment", "grade", "sub_grade", "purpose", "application_type",
    # Borrower profile
    "emp_length", "home_ownership", "annual_inc", "verification_status",
    "addr_state", "dti",
    # Credit history
    "fico_range_low", "fico_range_high", "delinq_2yrs", "open_acc",
    "pub_rec", "revol_bal", "revol_util", "total_acc",
    # Performance and outcome
    "loan_status", "out_prncp", "total_pymnt", "total_rec_prncp",
    "recoveries", "last_pymnt_d",
]
