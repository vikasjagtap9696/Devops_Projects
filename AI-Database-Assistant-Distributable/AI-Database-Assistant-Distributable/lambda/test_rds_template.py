# Safe local RDS connection test template.
# Never commit real passwords or access keys.

import os
import pymysql

connection = pymysql.connect(
    host=os.environ['DB_HOST'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    database=os.environ.get('DB_NAME', 'company_db'),
    port=int(os.environ.get('DB_PORT', '3306')),
)

print('RDS connection successful!')

cursor = connection.cursor()
cursor.execute('SELECT DATABASE();')
print('Database:', cursor.fetchone()[0])

cursor.execute('''
    SELECT TABLE_NAME
    FROM information_schema.TABLES
    WHERE TABLE_SCHEMA = %s
    ORDER BY TABLE_NAME;
''', (os.environ.get('DB_NAME', 'company_db'),))

print('Tables:')
for row in cursor.fetchall():
    print('-', row[0])

cursor.close()
connection.close()
