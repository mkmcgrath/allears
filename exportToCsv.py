import sqlite3
import csv

conn = sqlite3.connect("wifi_networks.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
tables = [row[0] for row in cursor.fetchall()]


for table in tables:
    with open(f"{table}.csv", "w", newline="") as f:
        writer = csv.writer(f)

        cursor.execute(f"SELECT * FROM {table};")
        rows = cursor.fetchall()

        writer.writerow([desc[0] for desc in cursor.description])

        # write the data
        writer.writerows(rows)

# close connection
conn.close()
