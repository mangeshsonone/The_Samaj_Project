import os
import subprocess
import boto3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

PG_URL = os.getenv("PG_URL")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_filename = f"db_backup_{timestamp}.sql"

# Dump the PostgreSQL database
dump_command = ["pg_dump", PG_URL, "-f", backup_filename]
subprocess.run(dump_command, check=True)

# Upload to S3
s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

s3_key = f"backups/{backup_filename}"

s3.upload_file(backup_filename, AWS_BUCKET_NAME, s3_key)
print(f"Backup uploaded to S3://{AWS_BUCKET_NAME}/{s3_key}")

# Optional: Delete local file
os.remove(backup_filename)
