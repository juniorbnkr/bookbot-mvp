import json,requests,os,time
from sqlalchemy import create_engine  
from sqlalchemy import text
import pandas as pd
import templates_messages

class Messages():

    def __init__(self,number,name,received_msg,wamid='') -> None:
        self.perm_token = os.getenv('perm_token')
        self.db_name = os.getenv('db_name')
        self.db_user = os.getenv('db_user')
        self.db_pass = os.getenv('db_pass')
        self.number = number
        self.name = name
        self.received_msg = received_msg
        self.template = ''
        self.msg_to_send = ''
        self.wamid = wamid
        self.sqlEngine = create_engine(f'mysql+pymysql://{self.db_user}:@{self.db_name}/bot_mvp?password={self.db_pass}', pool_recycle=3600, future=True)
        self.dbConnection = self.sqlEngine.connect()
        self.msgs_logs = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml WHERE phone_number = {self.number} \
                                ORDER BY created_at DESC;"),self.dbConnection)
        self.book_selected = self.get_book_selected()
        self.author_chosed = self.get_author_selected()
        self.book_available = ['Memórias Póstumas de Bras Cubas','Vidas Secas']
        self.log_itens = {
            "phone_number": self.number,
            "chap": None,
            "template": self.template,
            "block": None,
            "wamid": self.wamid,
            "book": self.book_selected,
            "author": self.author_chosed,
        }
        self.msgs = self.set_msgs()
        return None 
    
    def get_book_selected(self):
        df = self.msgs_logs[(self.msgs_logs['book'].notnull()) & (self.msgs_logs['book']!='')].tail(1)
        if not df.empty:
            print('book: ',df['book'].values[0])
            book_selected = df['book'].values[0]
            return book_selected

        print('no book selected')
        return None
    
    def get_author_name(self,author_code=False):
        if not author_code:
            author_code = self.get_author_selected()
        if author_code == '1':
            return 'Machado de Assis'
        if author_code == '2':
            return 'Graciliano Ramos'

        return None
    
    def get_author_selected(self):
        df = self.msgs_logs[(self.msgs_logs['author'].notnull()) & (self.msgs_logs['author']!='')].tail(1)
        if not df.empty:
            print('author: ',df['author'].values[0])
            author_selected = df['author'].values[0]
            return author_selected

        print('no author selected')
        return None
    
    def get_book_name(self,msg):
        if msg == '1':
            return 'Memórias Póstumas de Brás Cubas'
        if msg == '2':
            return 'Vidas Secas'

        return None

    def set_msgs(self):
        return templates_messages.set_msgs(self)

    def check_block(self):
        msgs = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml WHERE phone_number = {self.number} \
                                AND block = 1 ORDER BY created_at DESC;"),self.dbConnection)

        if not msgs.empty:
            print('bloqueado XXXXXX')
            return True
        print('not blocked')
        return False
    
    def unblock(self):
        self.dbConnection.execute(text(f'UPDATE bot_mvp.msg_log SET block = 0 WHERE phone_number = {self.number};'))
        self.dbConnection.commit()
        return None
    
    def send_msg(self):
        self.msg_to_send = self.next_msg()
        print(self.msg_to_send)
        url = "https://graph.facebook.com/v17.0/116826464720753/messages/"
        
        if isinstance(self.msg_to_send,list):
            response = []
            for msg in self.msg_to_send:
                payload = json.dumps({
                "messaging_product": "whatsapp",
                "to": self.number,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": msg
                }
                })
                headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '+self.perm_token

                }
                response.append(requests.request("POST", url, headers=headers, data=payload))
        else:
            payload = json.dumps({
            "messaging_product": "whatsapp",
            "to": self.number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": self.msg_to_send
            }
            })
            headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+self.perm_token

            }
            response = requests.request("POST", url, headers=headers, data=payload)
   
        return response

    def send_template(self):
        
        url = "https://graph.facebook.com/v17.0/116826464720753/messages/"

        payload = json.dumps({
        "messaging_product": "whatsapp",
        "to": self.number,
        "type": "template",
        "template": {
            "name": self.template,
            "language" : {"code":"pt_BR"}
        }
        })
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+self.perm_token

        }

        response = requests.request("POST", url, headers=headers, data=payload)
        # response = httpx.post(url, data=payload, headers=headers)
        # print(response.text)
        return response
    
    def check_in_progress_book(self):
        df = pd.read_sql(text(f"""SELECT * FROM bot_mvp.msg_log ml \
                        WHERE phone_number = {self.number} 
                        AND book = {self.received_msg} ORDER BY created_at DESC
                        ;"""),self.dbConnection)
        return int(df['chap'].max())    
        df = self.msgs_logs[(self.msgs_logs['book'] == self.received_msg)]
        return int(df['chap'].max())

    def get_last_chap(self,book):
        df = self.msgs_logs[(self.msgs_logs['book'] == book) & (self.msgs_logs['chap'].notnull())].tail(1)

        last_cap = df['max_chap'].values[0] 
        return last_cap

    def get_chap_content(self, book, chap):
        print(f'book: {book}, chap: {chap}')
        if str(book) == '1':
            table = 'memoriasBras'
        elif str(book) == '2':
            table = 'vidasSecas'
        df = pd.read_sql(text(f"SELECT content FROM bot_mvp.{table} ml \
                        WHERE cap = {chap} and status = 'ACTIVE' \
                        AND content NOT LIKE '<%' ORDER BY line asc;"),self.dbConnection)
        content = ""
        for index, row in df.iterrows():
            content = content + row['content'] + '\n'
        return content

    def next_msg(self):
        msgs = self.msgs_logs
        if msgs.empty:
            self.log_itens['template'] = 'author_chosen'
            self.add_log()
            return [self.msgs['welcome'],self.msgs['author_chosen']]
        
        if msgs['template'].iloc[1] == 'author_chosen':
            if self.received_msg in ['1','2'] :
                self.log_itens['template'] = 'book_chosen'
                self.log_itens['author'] = self.received_msg
                self.add_log()
                self.author_chosed = self.get_author_name(self.received_msg)
                self.msgs = self.set_msgs()
                return self.msgs['author_chosed']
            self.log_itens['template'] = 'author_chosen'
            self.log_itens['author'] = None
            self.add_log()
            return [self.msgs['wrong_author_chosed'], self.msgs['author_chosen']]
        
        if msgs['template'].iloc[1] == 'book_chosen':
            if self.received_msg in ['1'] :
                self.book_chosed = self.received_msg
                self.book_selected = self.get_book_name(self.received_msg)
                self.msgs = self.set_msgs()
                self.log_itens['template'] = 'book'
                self.log_itens['book'] = self.book_chosed
                self.log_itens['chap'] = 0
                if not msgs[msgs['book']==int(self.received_msg)].empty:
                    if self.check_in_progress_book() > 0:
                        self.msgs = self.set_msgs()
                        self.log_itens['template'] = 'continue_choose'
                        self.log_itens['book'] = self.book_chosed
                        self.log_itens['chap'] = None
                        self.add_log()
                        return [self.msgs['book_chosed'],self.msgs['start_or_continue']]
                
                self.add_log()
                return [self.msgs['book_chosed'],self.get_chap_content(self.received_msg,0),self.msgs['next']]
            
            if self.received_msg == '0':
                self.log_itens['template'] = 'author_chosen'
                self.add_log()
                return self.msgs['author_chosen']
            
            self.log_itens['template'] = 'book_chosen'
            self.log_itens['book'] = None
            self.add_log()
            return [self.msgs['wrong_book_chosed'], self.msgs['author_chosed']]

        if msgs['template'].iloc[1] == 'continue_choose':
            if self.received_msg == '1':
                next_chap = self.get_last_chap(self.book_selected) + 1
                self.log_itens['template'] = 'book'
                self.log_itens['book'] = self.book_selected
                self.log_itens['chap'] = next_chap
                print(self.log_itens)
                self.add_log()
                return [self.get_chap_content(self.book_selected,
                                              next_chap),
                        self.msgs['next']]
            
            if self.received_msg == '2':
                self.log_itens['template'] = 'book'
                self.log_itens['chap'] = 0
                self.log_itens['book'] = self.book_selected
                print(self.log_itens)
                self.add_log()
                return [self.get_chap_content(self.book_selected,0),self.msgs['next']]
            
            self.log_itens['template'] = 'continue_choose'
            self.add_log()
            return [self.msgs['invalid'], self.msgs['author_chosed']]

        if msgs['template'].iloc[1] == 'book':
            if self.book_selected not in [1,2]:
                self.log_itens['template'] = 'author_chosen'
                self.add_log()
                return self.msgs['author_chosen']
            
            if self.received_msg not in ['1','2'] :
                self.log_itens['template'] = 'book'
                self.add_log()
                return [self.msgs['invalid'],self.msgs['next']]

            if self.received_msg == '1':
                content = self.get_chap_content(str(self.book_selected), int(msgs['chap'].iloc[-1]) + 1)
                self.log_itens['chap'] = int(msgs['chap'].iloc[-1]) + 1
                self.log_itens['template'] = 'book'
                self.add_log()
                return [content, self.msgs['next']]

            if self.received_msg == '2':
                self.log_itens['template'] = 'author_chosen'
                self.add_log()
                return [self.msgs['author_chosen']]

        return None

    def add_log(self,
                chap=None,
                template=None,
                ):
        
        

        if self.log_itens['chap'] is None and self.log_itens['template'] is None:
            raise Exception('One of chap or template is required')
        chap = int(self.log_itens['chap']) if self.log_itens['chap'] is not None else 'NULL'
        template = self.log_itens['template'] if self.log_itens['template'] is not None else 'NULL'
        book = self.log_itens['book'] if self.log_itens['book'] is not None else 'NULL'
        author = self.log_itens['author'] if self.log_itens['author'] is not None else 'NULL'
        self.dbConnection.execute(text(f"""INSERT INTO bot_mvp.msg_log (phone_number,template, chap,block,wamid,author,book) 
        VALUES ({self.number}, '{template}',{chap},1,'{self.wamid}','{author}', {book});"""))
        self.dbConnection.commit()
        return None
    
    def check_repeat_msg(self):
        print('checkig repeat msg')
        sqlEngine       = create_engine(f'mysql+pymysql://{self.db_user}:@{self.db_name}/bot_mvp?password={self.db_pass}', pool_recycle=3600, future=True)
        dbConnection    = sqlEngine.connect()
        df = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml \
                        WHERE phone_number = {self.number} AND wamid = '{self.wamid}';"),dbConnection)
        if df.empty:
            print('new wamid, not repeated')
            return False
        else:
            print('repeated wamid')
            return True

