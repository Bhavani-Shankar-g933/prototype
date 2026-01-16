import psycopg2
from psycopg2.extras import execute_batch

# ---------- DB CONNECTION ----------

def get_db_connection():
    # conn = psycopg2.connect(
    # host="localhost",         #hostname
    # port="5432",              #port number
    # database="prototype_db",  #database name
    # user="odoo",              #username
    # password="odoo"           #password
    #     )
    
    conn = psycopg2.connect(
            dbname="prototype",
            user="postgres",
            password="prototype",
            host="database-1.cbgggcuu6bc0.ap-south-1.rds.amazonaws.com",
            port="5432"
        )

    conn.autocommit = True
    return conn


# ---------- DATA TYPE MAPPING ----------

def pandas_to_postgres_dtype(dtype):
    if "int" in str(dtype):
        return "INTEGER"
    if "float" in str(dtype):
        return "FLOAT"
    if "bool" in str(dtype):
        return "BOOLEAN"
    if "datetime" in str(dtype):
        return "TIMESTAMP"
    return "TEXT"


# ---------- DROP ALL TABLES ----------

def drop_all_tables(cur):
    cur.execute("""
            DO $$
            DECLARE
                r RECORD;
            BEGIN
                FOR r IN (
                    SELECT schemaname, tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                )
                LOOP
                    EXECUTE format(
                        'DROP TABLE IF EXISTS %I.%I CASCADE',
                        r.schemaname,
                        r.tablename
                    );
                END LOOP;
            END $$;
            """)


# ---------- CREATE TABLE FROM DF ----------

def create_table_from_df(df, table_name, cur):
    columns = []
    for col, dtype in df.dtypes.items():
        pg_type = pandas_to_postgres_dtype(dtype)
        columns.append(f'"{col}" {pg_type}')

    sql = f"""
    CREATE TABLE IF NOT EXISTS "{table_name}" (
        {', '.join(columns)}
    );
    """
    cur.execute(sql)


# ---------- INSERT DATA ----------

def insert_df(df, table_name, cur):
    # ✅ Remove old data first
    cur.execute(f'TRUNCATE TABLE "{table_name}";')

    cols = ', '.join([f'"{c}"' for c in df.columns])
    placeholders = ', '.join(['%s'] * len(df.columns))

    sql = f"""
        INSERT INTO "{table_name}" ({cols})
        VALUES ({placeholders})
    """

    data = [tuple(row) for row in df.itertuples(index=False)]
    execute_batch(cur, sql, data, page_size=1000)



def drop_tables(cur, conn, table_names):
    cur.execute("""
    SELECT tablename
    FROM pg_tables
    WHERE schemaname = 'public';
    """)
    print("It is going in drop tables")
    db_tables = {row[0] for row in cur.fetchall()}
    tables_to_drop = db_tables - table_names
    for table_name in tables_to_drop:
        try:
            cur.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;')
            conn.commit()
            print(f"✅ Table '{table_name}' dropped successfully")

        except Exception as e:
            conn.rollback()
            print(f"❌ Failed to drop table '{table_name}': {e}")

