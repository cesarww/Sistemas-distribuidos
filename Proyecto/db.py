import mysql.connector

def userValidation(): 
  username = str(input("Enter your username: "))
  password = str(input("Enter your password: "))

  mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="CesarPadilla_1",
    database="sistemas_dis"
  )

  mycursor = mydb.cursor()

  sql_query = "SELECT * FROM users"

  mycursor.execute(sql_query)

  result = mycursor.fetchall()

  for x in result:
    if x[1] == username and x[2] == password:
      return True
    else:
      return False

  mydb.close()