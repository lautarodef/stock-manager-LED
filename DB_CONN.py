import mysql.connector
conexion= mysql.connector.connect(
    host="localhost", 
    user="root",
    password="47074020",
    database="control_stock",
)


cursor=conexion.cursor()
sql=("SELECT * FROM productos")
cursor.execute(sql)
xd=cursor.fetchall()

