import psycopg2
import pandas as pd


# Establish a connection to the PostgreSQL database
# conn = psycopg2.connect(
#     host="localhost",         #hostname
#     port="5432",              #port number
#     database="prototype_db",  #database name
#     user="odoo",              #username
#     password="odoo"           #password
# )

conn = psycopg2.connect(
            dbname="prototype",
            user="postgres",
            password="prototype",
            host="database-1.cbgggcuu6bc0.ap-south-1.rds.amazonaws.com",
            port="5432"
        )


conn.autocommit = True
# Create a cursor object
cursor = conn.cursor()


# Fetch data from the database
def fetch_data(query):
    # Execute the query
    cursor.execute(query)
    # Get column names and data
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return pd.DataFrame(rows, columns=columns)


# Preprocess the dataframe
def preprocess_df(df):
    numeric_cols = [
        "SeniorCitizen",
        "Tenure",
        "MonthlyCharges",
        "TotalCharges"
    ]
    # Convert columns to numeric
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill missing values if any
    df = df.fillna(0)
    return df

# Get list of table names in the public schema
def table_names():
    #fetch table names
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    return  [table[0] for table in tables] if tables else []