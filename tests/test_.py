import pytest, os, sys
import cx_Oracle
sys.path.insert(1, os.path.join(sys.path[0], '../cgi-bin'))
from check_api import add_user, check_user, send_message, open_message

@pytest.fixture(autouse=True)
def clear_db():
    with open ('auth_db.txt', 'r') as db_file:
        text = db_file.readlines()
        login = text[0]
        password = text[1]
    db = cx_Oracle.connect(f'{login[:-1]}/{password}@localhost:1521/xe')        
    db.cursor().execute("DELETE FROM secrets")
    db.cursor().execute("DELETE FROM users")
    db.commit()
    db.close()

@pytest.fixture
def reg():
    add_user('Alisa', '12345678')
    add_user('Bob123', '12345678')

def test_add_user(clear_db):   
    assert add_user('Alisa', '12345678') == True
    assert add_user('Bob123', '12345678') == True
    assert add_user('Alisa', '1234567890Ab') == False
    assert add_user('User', 12345678) == True
    assert add_user(12345678, '12345678') == True
    assert add_user(None, '12345678') == True
    assert add_user('User_1', None) == True

def test_check_user(reg):
    assert check_user('Alisa', '12345678') == True
    assert check_user('Bob123', '12345678') == True
    assert check_user('User', '12345678') == False
    assert check_user('Alisa', '12345678Ab') == False
    assert check_user('Bob123', '12345678Ab') == False
    assert check_user(12345, '12345678') == False
    assert check_user('Alisa', 12345678) == True

def test_send_messege_1(reg):        
    assert send_message('Test text', 'text', 'Alisa', 'Bob123') != False
    assert send_message('Test text', 'text', 'Alisa', 'User') == False
    assert send_message('Test text', 'text', 'User', 'Alisa') == False
    assert send_message('Test text', 'text', 'User', 'Bob123') == False

def test_send_messege_2(reg):  
    assert send_message('Test text', 'text', 'Alisa', 12345) == False
    assert send_message('Test text', 'text', 12345, 'Bob123') == False
    assert send_message('Test text', 12345, 'Alisa', 'Bob123') == False
    assert send_message(12345, 'text', 'Alisa', 'Bob123') != False 

def test_send_messege_2(reg):
    assert send_message(None, 'text', 'Alisa', 'Bob123') != False
    assert send_message('Test text', None, 'Alisa', 'Bob123') == False
    assert send_message('Test text', 'text', None, 'Bob123') == False
    assert send_message('Test text', 'text', 'Alisa', None) == False

def test_open_message(reg):
    link = send_message('Test text', 'text', 'Alisa', 'Bob123')[27:]
    assert open_message(link[1:], 'Bob123') == False
    assert open_message(link[:1], 'Bob123') == False
    assert open_message(link, 'Alisas') == False
    assert open_message(link, None) == False
    assert open_message(None, 'Bob123') == False
    assert open_message(12345, 'Bob123') == False
    assert open_message(link, 12345) == False    
    assert open_message(link, 'Bob123') != 'Пользователь Alisa отправил вам сообщение: Test text'
    assert open_message(link, 'Bob123') == False

if __name__ == "__main__":
    pytest.main()
