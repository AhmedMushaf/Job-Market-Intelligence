import pandas as pd
import mysql.connector

# LOAD CSV
df = pd.read_csv(
    r"E:\mushaf notes\Data Analytics\Job-Market-Intelligence-project\data\processed\job_details_cleaned.csv"
)

# CONNECT MYSQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mushaf",
    database="job_market"
)

cursor = conn.cursor()

# 1️⃣ DROP TABLE IF EXISTS
cursor.execute("DROP TABLE IF EXISTS jobs")

# 2️⃣ CREATE TABLE AUTOMATICALLY FROM CSV
cols = df.columns

column_defs = []
for col in cols:
    column_defs.append(f"`{col}` TEXT")

create_table_sql = f"""
CREATE TABLE jobs (
{",".join(column_defs)}
)
"""

cursor.execute(create_table_sql)

# 3️⃣ INSERT DATA
col_names = ",".join(f"`{c}`" for c in cols)
placeholders = ",".join(["%s"] * len(cols))

insert_sql = f"INSERT INTO jobs ({col_names}) VALUES ({placeholders})"

data = df.fillna("").values.tolist()

cursor.executemany(insert_sql, data)
conn.commit()

cursor.close()
conn.close()

print("✅ Data inserted into MySQL successfully")
