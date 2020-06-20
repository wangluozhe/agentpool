import settings
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class DBClient():

    def __new__(cls, *args, **kwargs):
        db_start = settings.DB_START
        db_host = settings.DB_HOST
        db_port = settings.DB_PORT
        db_password = settings.DB_PASSWORD
        db_database = settings.DB_DATABASE
        if db_start == 'RedisClient':
            db = getattr(__import__('redisclient'),'RedisClient')(host=db_host,port=db_port,password=db_password,database=db_database)
        else:
            db_username = settings.DB_USERNAME
            db = getattr(__import__('redisclient'),'RedisClient')(host=db_host,port=db_port,username=db_username,password=db_password,database=db_database)
        return db