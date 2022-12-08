import cgi
import sqlite3
import random, string
import html, hashlib
import datetime, time

form = cgi.FieldStorage() #получаем данные из форм

send = form.getfirst("send") #кнопки
open = form.getfirst("open")
registration = form.getfirst("registration")

db = sqlite3.connect("Users.db") #подключаемся к базе данных

def Show_in_browser(text):
    print ("Content-type:text/html")
    print()
    print(text)

def Add_Message (key, recipient, sender, message, time):
    value = key, recipient, sender, message, time
    db.cursor().execute("INSERT INTO secrets (key, recipient, sender, message, time) VALUES (?, ?, ?, ?, ?)", (value))
    db.commit()

def Add_User(login, password, salt, time):
    value = login, password, salt, time
    db.cursor().execute("INSERT INTO users (login, password, salt, time) VALUES (?, ?, ?, ?)", (value)) #кортеж от SQL-инъекций
    db.commit() #сохраняем базу

def Check_db(select, fromm, where, value):
    db = sqlite3.connect("Users.db")
    db.row_factory = lambda cursor, row: row[0]
    db_req = f'SELECT {select} FROM {fromm} WHERE {where} == "{value}";' #ищем есть ли в базе
    db_value = db.cursor().execute(db_req).fetchone() #записываем в переменную
    return db_value

def Delete_db(value):
    db = sqlite3.connect("Users.db")
    db.row_factory = lambda cursor, row: row[0]
    db_req = f"DELETE FROM secrets WHERE key == '{value}';"
    db_value = db.cursor().execute(db_req)
    db.commit()


def Send():
    login_sender = html.escape(form.getfirst("login_sender")) # html.escape - экранируем от XXS-атак через форму ввода
    password_sender = html.escape(form.getfirst("password_sender")).encode('utf-8')
    login_recipient = html.escape(form.getfirst("login_recipient"))
    secret = html.escape(form.getfirst("secret"))

    salt = Check_db('salt', 'users', 'login', login_sender)
    hash_password_sender = hashlib.sha256(password_sender + salt).hexdigest()

    time_rec = datetime.datetime.now() #расчитали время сейчас
    time_del = time_rec+datetime.timedelta(minutes = 1) #расчитываем время удаления сообщения

    if Check_db('password', 'users', 'login', login_sender) == hash_password_sender:
        if Check_db('login', 'users', 'login', login_recipient) == login_recipient:
            k = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(16)])

            if Check_db('key', 'secrets', 'key', k) != None: # на случай, если сгенерированный ключ уже есть в базе
                while Check_db('key', 'secrets', 'key', k) != None:
                    k = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(16)])
                    Check_db('key', 'secrets', 'key', k)
            if Check_db('key', 'secrets', 'key', k) == None:
                Add_Message(k, login_recipient, login_sender, secret, time_del)

            Show_in_browser(f"Для пользователя {login_recipient} сформерован идентификатор: {k}\n")
            print(''' <html lang = "ru"> <body> <br>
                Отправьте ключ получателю секретного сообщения.<br>
                Чтобы получить доступ к секретному сообщению, получателю необходимо ввести этот ключ в соответсвующее поле.
                </body>
            </html>''')
        else: Show_in_browser(f'Пользователь {login_recipient} не зарегистрирован')
    else: Show_in_browser('Неправельный логин или пароль, возможно, Вы не зарегистрированы')


def Open():
    login = form.getfirst("login") #поля для получения
    password = form.getfirst("password").encode('utf-8')
    key = form.getfirst("key")

    salt = Check_db('salt', 'users', 'login', login)
    hash_password = hashlib.sha256(password + salt).hexdigest()

    if Check_db('password', 'users', 'login', login) == hash_password:
        if Check_db('recipient', 'secrets', 'key', key) == login:

            time_del_str = Check_db('time', 'secrets', 'recipient', login)
            time_del = datetime.datetime.strptime(time_del_str, '%Y-%m-%d %H:%M:%S.%f') #преобразуем строку в формат даты и времени

            if datetime.datetime.now() < time_del: #проверям не истекло ли время хранения сообщения
                sender = Check_db('sender', 'secrets', 'key', key)
                message = Check_db('message', 'secrets', 'key', key)
                Show_in_browser(f"Пользователь {sender} отправил Вам сообщение: {message}")
                Delete_db(key)
            else:
                Show_in_browser("Истек срок хранения сообщения")
                Delete_db(key)
        else: Show_in_browser("Ключ недействителен или сообщение предназначено другому пользователю")
    else: Show_in_browser("Неправильный логин или пароль")


def Registration():
    login_new = html.escape(form.getfirst("login_new"))
    password1 = html.escape(form.getfirst("password1")).encode('utf-8')
    password2 = html.escape(form.getfirst("password2")).encode('utf-8')

    salt = ''.join([random.choice(string.ascii_lowercase + string.digits) for i in range(64)]).encode('utf-8')
    hash_password1 = hashlib.sha256(password1 + salt).hexdigest()
    hash_password2 = hashlib.sha256(password2 + salt).hexdigest()

    time_rec = datetime.datetime.now() #расчитали время сейчас
    time_del = time_rec+datetime.timedelta(minutes = 1) #расчитываем время удаления пользователя

    if Check_db('login', 'users', 'login', login_new) == None:
        if hash_password1 == hash_password2:
            Add_User(login_new, hash_password1, salt, time_del)
            Show_in_browser("Вы зарегестрированы, теперь вы можете отправлять и получать секретные сообщения")
        else: Show_in_browser("Вы не прошли проверку пароля, попробуйте еще раз")
    else: Show_in_browser("Такой логин уже существует, придумайте другой")

if send != None: Send()
elif open != None: Open()
elif registration != None: Registration()
