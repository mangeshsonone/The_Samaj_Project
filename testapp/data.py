"C:\Users\ankii\Downloads\db (1) (1).sqlite3"
import sqlite3

# Replace 'path/to/your.db' with the actual file path
conn = sqlite3.connect("C:\Users\ankii\Downloads\db (1) (1).sqlite3")
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Query a specific table (replace 'your_table_name' with a table name)
cursor.execute("SELECT * FROM your_table_name;")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()