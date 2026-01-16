import boto3
import pandas as pd
import io

from DBinsertion import (
    get_db_connection,
    drop_all_tables,
    create_table_from_df,
    insert_df,
    drop_tables
)

# ---------- S3 CONFIG ----------
BUCKET_NAME = "bhavani-prototype-bucket-12345"

def load_s3_csvs_to_postgres():
    s3 = boto3.client("s3")
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        paginator = s3.get_paginator("list_objects_v2")

        table_names = []
        csv_found = False

        for page in paginator.paginate(Bucket=BUCKET_NAME):
            if "Contents" not in page:
                continue

            for obj in page["Contents"]:
                key = obj["Key"]

                if not key.endswith(".csv"):
                    continue

                csv_found = True
                table_name = key.split("/")[-1].replace(".csv", "")
                table_names.append(table_name)

                print(f"Loading {key} → {table_name}")

                response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
                df = pd.read_csv(io.BytesIO(response["Body"].read()))

                create_table_from_df(df, table_name, cur)
                insert_df(df, table_name, cur)

        # ❌ If no CSV files were found — EXIT EARLY
        if not csv_found:
            return False, "❌ No CSV files found in S3 bucket. Please upload data before syncing."

        # Drop old tables not present in S3
        drop_tables(cur, conn, set(table_names))

        conn.commit()
        return True, "✅ Data loaded successfully"

    except Exception as e:
        conn.rollback()
        return False, f"❌ Error while syncing: {str(e)}"

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    load_s3_csvs_to_postgres()
