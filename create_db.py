import MySQLdb

def create_database():
    try:
        # Connect to MySQL server
        db = MySQLdb.connect(host="localhost", user="root", passwd="root")
        cursor = db.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS agros;")
        print("Successfully created database 'agros' or it already exists.")
        
        db.close()
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    create_database()
