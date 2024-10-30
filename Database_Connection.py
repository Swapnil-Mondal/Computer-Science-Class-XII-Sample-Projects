def con():
    import mysql.connector
    mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="06122007",
            database="project_dbms"
        )
    return mydb
if __name__=="__main__":
    con()
