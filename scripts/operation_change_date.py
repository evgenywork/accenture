import mysql.connector
from mysql.connector import errorcode
import dateparser
from config import *

try:

    db_conn = mysql.connector.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        database=DB_NAME,
        port=DB_PORT,
    )
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)

mycursor = db_conn.cursor()

mycursor.execute("SELECT * FROM 03_operation ")

# myresult = mycursor.fetchall()

columns = [col[0] for col in mycursor.description]
rows = [dict(zip(columns, row)) for row in mycursor.fetchall()]

for x in rows:
    date_converted = dateparser.parse(str(x['start_date']))
    # print(date_converted)
    # print(x['start_date'])
    print(x['id'])
    sql = "UPDATE 03_operation SET start_date_new = %s WHERE id = %s"
    val = (date_converted, x['id'])
    mycursor.execute(sql, val)
    db_conn.commit()

db_conn.close()
