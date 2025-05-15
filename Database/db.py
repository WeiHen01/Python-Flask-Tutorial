import pyodbc 

# MSSQL Database connection configuration
db_config = {
    'server': 'DESKTOP-2713EGT',
    'database': 'FinanceMgmt',
    # 'username': 'sa',
    # 'password': 'YourStrong@Passw0rd',
    'driver': 'SQL Server',
}

def get_db_connection():
    conn_str = (
        f"DRIVER={{{db_config['driver']}}};"
        f"SERVER={db_config['server']};"
        f"DATABASE={db_config['database']};"
        f"Trusted_Connection=yes;"
        # f"UID={db_config['username']};"
        # f"PWD={db_config['password']}"
    )
    return pyodbc.connect(conn_str)

# if in accessing to mssql using Windows Authentication, then no need for user and password
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=DESKTOP-2713EGT;DATABASE=FinanceMgmt;')
if(conn):
    print("db connected")


# # Using a DSN, but providing a password as well
# cursor = conn.cursor()

# testing for query
# cursor.execute('SELECT * FROM dbo.users')
# for row in cursor.fetchall(): 
#     print (row.Username, " , ", row.Email)

# while True:
#     row = cursor.fetchone()
#     if not row:
#         break
#     print('id:', row.Username)
