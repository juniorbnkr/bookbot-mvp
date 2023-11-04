
from sqlalchemy import create_engine  
from sqlalchemy import text
import os

class Event():

    def __init__(self,event) -> None:
        self.event = event
        self.db_name = os.getenv('db_name')
        self.db_user = os.getenv('db_user')
        self.db_pass = os.getenv('db_pass')
        self.type = self.get_type(self)
        return None
    
    def check_event(self):
        return None
    
    def save_event(self):
        sqlEngine       = create_engine(f'mysql+pymysql://{self.db_user}:@{self.db_name}/bot_mvp?password={self.db_pass}', pool_recycle=3600, future=True)
        dbConnection    = sqlEngine.connect()
        dbConnection.execute(text(f'INSERT INTO bot_mvp.events_received (event) VALUES ("{self.event}");'))
        dbConnection.commit()
        return None
    
    def get_type(self) -> str:
        if 'sent' in self.event:
            return 'sent'
        if 'read' in self.event:
            return 'read'
        if "'type': 'text'" in self.event:
            return 'receive'
        return self.type
