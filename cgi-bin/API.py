import cgi
import sqlite3
import random, string
import html, hashlib
import datetime, time
import rsa, gostcrypto

db = sqlite3.connect("Users.db") #подключаемся к базе данных

def show_in_browser(text):
    print ("Content-type:text/html; charset=PyCharm")
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
        db = sqlite3.connect("Users.db")
        db.row_factory = lambda cursor, row: row[0]
        db_req = f'SELECT {select} FROM {fromm} WHERE {where} == "{value}";' #ищем есть ли в базе
        db_value = db.cursor().execute(db_req).fetchone() #записываем в переменную
        return db_value

    def verification_existence(func):
        def wrapper(self, arg):
            if self.__class__.__name__ == 'Users':
                if self.check_db('login', 'users', 'login', arg) != None:
                    func(self, arg)
                    return True
                else: return False
            elif self.__class__.__name__ == 'Messages':
                if self.check_db('key', 'secrets', 'key', arg) != None:
                    func(self, arg)
                    return True
                else: return False
        return wrapper

    def delete_db(self, fromm, where, value):
        db = sqlite3.connect("Users.db")
        db.row_factory = lambda cursor, row: row[0]
        db_req = f"DELETE FROM {fromm} WHERE {where} == '{value}';"
        db_value = db.cursor().execute(db_req)
        db.commit()

    def add_user(self, login, password, salt, time, public_key, private_key):
        value = login, password, salt, time, public_key, private_key
        db.cursor().execute("INSERT INTO users (login, password, salt, time, public, private) VALUES (?, ?, ?, ?, ?, ?)", (value)) #кортеж от SQL-инъекций
        db.commit() #сохраняем базу

    def add_message (self, id, recipient, sender, message, time):
        value = id, recipient, sender, message, time
        db.cursor().execute("INSERT INTO secrets (key, recipient, sender, message, time) VALUES (?, ?, ?, ?, ?)", (value))
        db.commit()

class Users(BaseDate):
    """Описание пользователя"""
    # password = None
    # time = None
    # salt = None
    # public_key = None
    # private_key = None

    def __init__(self, login):
        self.login = login

    def rsa(self, password):
        key = password.rjust(32, '0').encode('utf-8') #добавляем к паролю символы до нужной длинный
        (public_key, private_key) = rsa.newkeys(2048) #формирование ключей для rsa
        pub_k = public_key.save_pkcs1()
        pr_k = private_key.save_pkcs1()

        obj = gostcrypto.gostcipher.new('kuznechik', key, gostcrypto.gostcipher.MODE_ECB, pad_mode=gostcrypto.gostcipher.PAD_MODE_1)
        encrypted_private_key = obj.encrypt(pr_k) #шифруем приватный ключ кузнечиком

        keys = dict() #создаем словарь
        keys['public'] = pub_k
        keys['private'] = encrypted_private_key
        return keys

    def write(self, login, password):
        self.salt = ''.join([random.choice(string.ascii_lowercase + string.digits) for i in range(64)]).encode('utf-8')
        self.password = hashlib.sha256(password.encode('utf-8') + self.salt).hexdigest()
        self.time = datetime.datetime.now() + datetime.timedelta(days = 365)
        keys = self.rsa(password)
        self.public_key = keys['public']
        self.private_key = keys['private']

    @BaseDate.verification_existence
    def read(self, login):
        self.salt = self.check_db('salt', 'users', 'login', login)
        self.password = self.check_db('password', 'users', 'login', login)
        time_del_login_str = self.check_db('time', 'users', 'login', login) #получаем время хранения учетной записи
        self.time =  datetime.datetime.strptime(time_del_login_str, '%Y-%m-%d %H:%M:%S.%f') #преобразуем строку в формат даты и времени
        self.public_key = self.check_db('public', 'users', 'login', login)
        self.private_key = self.check_db('private', 'users', 'login', login)

class Messages(BaseDate):
    """Описание сообщения"""
    # id = None
    # sender = None
    # resipient = None
    # message = None
    # time = None

    def encryption (self, message, key):
        ks = rsa.PublicKey.load_pkcs1(key)
        encrypted_secret = rsa.encrypt(message, ks)
        return encrypted_secret

    def decryption (self, password, key_rsa_encript, message_encrypt):
        key_kuznechik = password.rjust(32, '0').encode('utf-8')
        obj = gostcrypto.gostcipher.new('kuznechik', key_kuznechik, gostcrypto.gostcipher.MODE_ECB, pad_mode=gostcrypto.gostcipher.PAD_MODE_1)
        key_rsa = obj.decrypt(key_rsa_encript).decode('utf-8')
        key_rsa_import = rsa.PrivateKey.load_pkcs1(key_rsa)
        decryption_message = rsa.decrypt(message_encrypt, key_rsa_import).decode('utf-8')
        return decryption_message

    def write(self, sender, resipient, message):
        self.id = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(16)])
        self.sender = sender
        self.resipient = resipient
        self.message = message
        self.time = datetime.datetime.now() + datetime.timedelta(days = 7)
        return self.id

    @BaseDate.verification_existence
    def read(self, id):
        self.id = id
        self.sender = self.check_db('sender', 'secrets', 'key', id)
        self.resipient = self.check_db('recipient', 'secrets', 'key', id)
        self.message = self.check_db('message', 'secrets', 'key', id)
        time_del_message_str = self.check_db('time', 'secrets', 'key', id)
        self.time = datetime.datetime.strptime(time_del_message_str, '%Y-%m-%d %H:%M:%S.%f')

def registration(login, password):
    user = Users(login)
    if user.check_db('login', 'users', 'login', user.login) == None:
        user.write(user.login, password)
        user.add_user(user.login, user.password, user.salt, user.time, user.public_key, user.private_key)
        response = 'Вы зарегистрированы'
    else: response = 'Пользователь с таким логином уже зарегистрирвоан, придумайте другой'
    del user
    show_in_browser(response)
    return response

def send_message(login_sender, password_sender, login_recipient, secret):
    sender = Users(login_sender)
    sender_read = sender.read(sender.login)
    resipient = Users(login_recipient)
    resipient_read = resipient.read(resipient.login)

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
        encrypted_message = message.encryption (secret.encode('utf-8'), resipient.public_key) #шифруем сообщение
        message.write(login_sender, login_recipient, encrypted_message)
        message.add_message(message.id, message.resipient, message.sender, message.message, message.time)
        response = f"Для пользователя {resipient.login} сформерован идентификатор: {message.id}"
        show_in_browser(response)

        values = dict() #создаем словарь
        values['response'] = response
        values['message_id'] = message.id
        return values
    #     del message
    # del sender
    # del resipient 
    # show_in_browser(response)
    

def open_message(login, password, id):
    resipient = Users(login)
    resipient_read = resipient.read(resipient.login)
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
        message.delete_db('secrets', 'key', message.id)
        response = 'Сообщения с таким идентификатором не существует или его срок хранения истек'
        show_in_browser(response)
        return response
    elif resipient.login != message.resipient: 
        response = 'Сообщение предназначено другому пользователю'
        show_in_browser(response)
        return response
    else:
        secret = message.decryption(password, resipient.private_key, message.message)
        response = f"Пользователь {message.sender} отправил Вам сообщение: {secret}"
        message.delete_db('secrets', 'key', message.id) #удаление сообщения после прочтения
        show_in_browser(response)

        values = dict() #создаем словарь
        values['response'] = response
        values['message'] = secret
        return values
    # del resipient
    # del message
    # show_in_browser(response)
    
def main():    
    form = cgi.FieldStorage() #получаем данные из форм

    send_button = form.getfirst("send") #кнопки
    open_button = form.getfirst("open")
    registration_button = form.getfirst("registration")

    login_new = html.escape(form.getfirst("login_new")) # html.escape - экранируем от XXS-атак через форму ввода
    password_new = html.escape(form.getfirst("password1")) 

    login_sender = html.escape(form.getfirst("login_sender")) 
    password_sender = html.escape(form.getfirst("password_sender"))
    login_recipient = html.escape(form.getfirst("login_recipient"))
    secret = html.escape(form.getfirst("secret"))

    login = form.getfirst("login") 
    password = form.getfirst("password")
    id = form.getfirst("key")

    if send_button != None: send_message(login_new, password_new)
    elif open_button != None: open_message(login_sender, password_sender, login_recipient, secret)
    elif registration_button != None: registration(login, password, id)

if __name__ == "__main__":
    main()

    

#rsa.pkcs1.decryptionError
