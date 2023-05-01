#!/usr/bin/python
import cgi
import sqlite3
import random, string
import html, hashlib
import datetime, time
import gostcrypto
import os, glob

db = sqlite3.connect("main.db") #подключаемся к базе данных

def show_in_browser(text):
    print ("Content-type:text/html; charset=utf-8")
    print()
    content = f"""
        <html lang = "ru">
            <head>
                <title>Ответ сервера</title>
                <meta charset="PyCharm">
                <link rel="stylesheet" href="/css/style_answer.css">
            </head>

            <body>
            <h3 class = "text"> {text} </h3>
            </body> """
    print(content)

class BaseDate(object):
    """Работа с базой данных"""
    def check_db(self, select, fromm, where, value):
        #db = sqlite3.connect("main.db")
        db.row_factory = lambda cursor, row: row[0]
        db_req = f'SELECT {select} FROM {fromm} WHERE {where} == "{value}";' #ищем есть ли в базе
        db_value = db.cursor().execute(db_req).fetchone() #записываем в переменную
        return db_value

    def delete_db(self, fromm, where, value):
        #db = sqlite3.connect("main.db")
        db.row_factory = lambda cursor, row: row[0]
        db_req = f"DELETE FROM {fromm} WHERE {where} == '{value}';"
        db_value = db.cursor().execute(db_req)
        db.commit()

    def add_user(self, login, password, salt, time):
        value = login, password, salt, time
        db.cursor().execute("INSERT INTO users (login, password, salt, time) VALUES (?, ?, ?, ?)", (value)) #кортеж от SQL-инъекций
        db.commit() #сохраняем базу

    def add_message (self, id, recipient, sender, message, time, key):
        value = id, recipient, sender, message, time, key
        db.cursor().execute("INSERT INTO secrets (id, recipient, sender, message, time, key) VALUES (?, ?, ?, ?, ?, ?)", (value))
        db.commit()

class Users(BaseDate):
    def __init__(self, login):
        self.login = login

    def write(self, login, password):
        #self.login = login
        self.salt = ''.join([random.choice(string.ascii_lowercase + string.digits) for i in range(64)]).encode('utf-8')
        self.password = hashlib.sha256(password.encode('utf-8') + self.salt).hexdigest()
        self.time = datetime.datetime.now() + datetime.timedelta(days = 365)        
        self.private_key = ''.join([random.choice(string.ascii_lowercase + string.digits) for i in range(32)]).encode('utf-8')

    #@BaseDate.verification_existence
    def read(self, login):
        if self.check_db('login', 'users', 'login', login) != None:
            #self.login = login
            self.salt = self.check_db('salt', 'users', 'login', login)
            self.password = self.check_db('password', 'users', 'login', login)
            time_del_login_str = self.check_db('time', 'users', 'login', login) #получаем время хранения учетной записи
            self.time =  datetime.datetime.strptime(time_del_login_str, '%Y-%m-%d %H:%M:%S.%f') #преобразуем строку в формат даты и времени
            return True
        else: return False

class Messages(BaseDate):      
    def encryption(self, message, key):
        obj = gostcrypto.gostcipher.new('kuznechik', key.encode('utf-8'), gostcrypto.gostcipher.MODE_ECB, pad_mode=gostcrypto.gostcipher.PAD_MODE_1)
        encrypted_text = obj.encrypt(message) #шифруем приватный ключ кузнечиком
        return encrypted_text
    
    def decryption(self, message, key):
        obj = gostcrypto.gostcipher.new('kuznechik', key.encode('utf-8'), gostcrypto.gostcipher.MODE_ECB, pad_mode=gostcrypto.gostcipher.PAD_MODE_1)
        decryption_text = obj.decrypt(message).decode('utf-8')
        return decryption_text

    def write(self, sender, resipient, message):
        self.id = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(16)])
        self.sender = sender
        self.resipient = resipient
        self.message = message
        self.time = datetime.datetime.now() + datetime.timedelta(days = 7)
        self.key = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(32)])
        return self.id

    #@BaseDate.verification_existence
    def read(self, id):
        if self.check_db('id', 'secrets', 'id', id) != None:
            self.id = id
            self.sender = self.check_db('sender', 'secrets', 'id', id)
            self.resipient = self.check_db('recipient', 'secrets', 'id', id)
            self.message = self.check_db('message', 'secrets', 'id', id)
            time_del_message_str = self.check_db('time', 'secrets', 'id', id)
            self.time = datetime.datetime.strptime(time_del_message_str, '%Y-%m-%d %H:%M:%S.%f')
            self.key = self.check_db('key', 'secrets', 'id', id)
            return True
        else: return False

    def write_file(self, secret_file, key, id):
        if secret_file.filename:   
            fn = os.path.basename(secret_file.filename)           
            with open ('files/' + id + '_' + fn, 'wb') as new_file:            
                open_text = secret_file.file.read()
                encription_text = self.encryption(open_text, key)
                new_file.write(encription_text)

    def read_file(self, id, key):
        file_name = glob.glob(f'files/{id}*')[0]
        with open(file_name, 'rb') as old_file:
            encryption_text = old_file.read()
        open_text = self.decryption(encryption_text, key)           

        file_name_new = file_name[23:] # получаем имя файла 
       
        print('Content-type: application/octet-stream') #отдаем пользователю
        print(f'Content-Disposition: attachment; filename="{file_name_new}"')
        print()
        print(f'{open_text}')         
        os.remove(file_name) #удаляем файл
        
        return file_name_new
    
    def write_message(self, secret_message, key, id):
        encription_text = self.encryption(secret_message, key)
        with open ('messages/' + id + '.txt', 'wb') as new_file:
            new_file.write(encription_text)

    def read_message(self, id, key):
        with open ('messages/' + id + '.txt', 'rb') as old_file:
            encryption_text = old_file.read()
            open_text = self.decryption(encryption_text, key)
        os.remove('messages/' + id + '.txt') #удаляем
        return open_text

def registration(login, password):
    user = Users(login)
    if user.check_db('login', 'users', 'login', user.login) == None:
        user.write(user.login, password)
        user.add_user(user.login, user.password, user.salt, user.time)
        response = 'Вы зарегистрированы'
    else: response = 'Пользователь с таким логином уже зарегистрирвоан, придумайте другой'
    del user
    show_in_browser(response)
    return response

def send_message(login_sender, password_sender, login_recipient, secret, type_message):
    sender = Users(login_sender)
    sender_read = sender.read(login_sender)
    resipient = Users(login_recipient)
    resipient_read = resipient.read(login_recipient)

    #проверяем отправителя
    if sender_read == False: 
        response = 'Вы ввели несуществующий логин или время действия вашей учетной записи истекло'
        show_in_browser(response)
        return response
    elif datetime.datetime.now() > sender.time:
        sender.delete_db('users', 'login', sender.login)
        response = 'Вы ввели несуществующий логин или время действия вашей учетной записи истекло'
        show_in_browser(response)
        return response
    elif sender.password != hashlib.sha256(password_sender.encode('utf-8') + sender.salt).hexdigest():
        response = 'Вы ввели неправильный пароль'
        show_in_browser(response)
        return response
    # #проверяем получателя
    elif resipient_read == False: 
        response = 'Вы ввели несуществующий логин получателя или время действия его учетной записи истекло'
        show_in_browser(response)
        return response
    elif datetime.datetime.now() > sender.time:
        resipient.delete_db('users', 'login', resipient.login)
        response = 'Вы ввели несуществующий логин получателя или время действия его учетной записи истекло'
        show_in_browser(response)
        return response
    else:
        message = Messages()

        if type_message == 'text':            
            #encrypted_message = message.encryption (secret.encode('utf-8'),  message.key) #шифруем сообщение                
            message.write(login_sender, login_recipient, 'text')
            message.write_message(secret.encode('utf-8'), message.key, message.id)
            message.add_message(message.id, message.resipient, message.sender, message.message, message.time, message.key)
            response = f"Для пользователя {resipient.login} сформерован идентификатор: {message.id}"
            show_in_browser(response)

            values = dict() #создаем словарь
            values['response'] = response
            values['message_id'] = message.id
            return values
            
        elif type_message == 'file':                
            message.write(login_sender, login_recipient, 'file')
            message.write_file(secret, message.key, message.id)           

            message.add_message(message.id, message.resipient, message.sender, message.message, message.time, message.key)
            response = f"Для пользователя {resipient.login} сформерован идентификатор: {message.id}"
            show_in_browser(response)

            values = dict() #создаем словарь
            values['response'] = response
            values['message_id'] = message.id
            return values
    
def open_message(login, password, id):
    resipient = Users(login)
    resipient_read = resipient.read(login)
    message = Messages()
    message_read = message.read(id)

    #проверяем получателя
    if resipient_read == False: 
        response = 'Вы ввели несуществующий логин или время действия вашей учетной записи истекло'
        show_in_browser(response)
        return response
    elif datetime.datetime.now() > resipient.time:
        resipient.delete_db('users', 'login', resipient.login)
        response = 'Вы ввели несуществующий логин или время действия вашей учетной записи истекло'
        show_in_browser(response)
        return response
    elif resipient.password != hashlib.sha256(password.encode('utf-8') + resipient.salt).hexdigest():
        response = 'Вы ввели неправильный пароль'
        show_in_browser(response)
        return response
    #проверяем сообщение
    elif message_read == False: 
        response = 'Сообщения с таким идентификатором не существует или его срок хранения истек'
        show_in_browser(response)
        return response
    elif datetime.datetime.now() > message.time:
        message.delete_db('secrets', 'id', message.id)
        response = 'Сообщения с таким идентификатором не существует или его срок хранения истек'
        show_in_browser(response)
        return response
    elif resipient.login != message.resipient: 
        response = 'Сообщение предназначено другому пользователю'
        show_in_browser(response)
        return response
    else:
        try:
            if message.message == 'text':
                text = message.read_message(message.id, message.key)
                response = f"Пользователь {message.sender} отправил Вам сообщение: {text}"
                message.delete_db('secrets', 'id', message.id) #удаляем запись о сообщении
                show_in_browser(response)

                values = dict() #создаем словарь
                values['response'] = response
                values['message'] = text
                return values
            elif message.message == 'file':                       
                file_name = message.read_file(id, message.key)            
                message.delete_db('secrets', 'id', message.id) #удаляем запись о сообщении
                response = f"Пользователь {message.sender} отправил Вам файл."            
                values = dict()
                values['sender'] = message.sender
                values['path'] = file_name 
                return values         
        except IndexError: 
            message.delete_db('secrets', 'id', message.id)
            show_in_browser('Кажется, сообщение где-то потерялось, попросите отпаравить его повторно')

    
def main():    
    form = cgi.FieldStorage() #получаем данные из форм

    send_button = form.getfirst("send") #кнопки
    open_button = form.getfirst("open")
    registration_button = form.getfirst("registration")

    if send_button != "send":      
        login_sender = html.escape(form.getfirst("login_sender")) 
        password_sender = html.escape(form.getfirst("password_sender"))
        login_recipient = html.escape(form.getfirst("login_recipient"))
       
        if form.getfirst("secret") == '':
            f = form["secret_file"]   
            send_message(login_sender, password_sender, login_recipient, f, 'file')
        else:
            secret = html.escape(form.getfirst("secret"))         
            send_message(login_sender, password_sender, login_recipient, secret, 'text')       

    elif open_button != "open": 
        login = form.getfirst("login") 
        password = form.getfirst("password")
        id = form.getfirst("key")
        open_message(login, password, id)

    elif registration_button != "registration": 
        login_new = html.escape(form.getfirst("login_new")) # html.escape - экранируем от XXS-атак через форму ввода
        password_new = html.escape(form.getfirst("password1")) 
        registration(login_new, password_new)

if __name__ == "__main__":
    main()

    

#rsa.pkcs1.decryptionError
