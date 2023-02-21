import pymysql

def connection_db():
    
    conn = pymysql.connect(
        host = 'localhost',
        user = 'root',
        password = '',
        db = 'escalas'
    )
    
    return conn



