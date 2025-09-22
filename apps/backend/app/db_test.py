import psycopg2

conn = psycopg2.connect(
    host="35.232.214.10",
    port=5432,
    dbname="postgres",
    user="postgres",
    password="council0929"
)
cur = conn.cursor()
cur.execute("SELECT * FROM tb_meta_info;")
rows = cur.fetchall()
for row in rows:
    print(row)
cur.close()
conn.close()
