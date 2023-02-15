import pytest, sqlite3, os, sys
sys.path.insert(1, os.path.join(sys.path[0], '../cgi-bin'))
from API import registration, send_message, open_message

@pytest.fixture(autouse=True)
def clear_db():
    db = sqlite3.connect("Users.db")
    db_clear_users = f"DELETE FROM users;"
    db_clear_messages = f"DELETE FROM secrets;"
    db_value_users = db.cursor().execute(db_clear_users)
    db_value_messages = db.cursor().execute(db_clear_messages)
    db.commit()

@pytest.fixture
def add_user():
    registration('User_1', '1234567890Ab')
    registration('User_2', '1234567890Ab')

@pytest.fixture
def add_message():
    values = send_message('User_1', '1234567890Ab', 'User_2', 'Сообщение')
    return values['message_id']

def test_registration():   
    assert registration('User_1', '1234567890Ab') == 'Вы зарегистрированы'
    assert registration('User_2', '1234567890Ab') == 'Вы зарегистрированы'
    assert registration('User_1', '1234567890Ab') == 'Пользователь с таким логином уже зарегистрирвоан, придумайте другой'

def test_send_messege(add_user):
    assert send_message('User_3', '1234567890Ab', 'User_2', 'Сообщение') == 'Вы ввели несуществующий логин или время действия вашей учетной записи истекло'
    assert send_message('User_1', '1234567890Abc', 'User_2', 'Сообщение') == 'Вы ввели неправильный пароль'
    assert send_message('User_1', '1234567890Ab', 'User_3', 'Сообщение') == 'Вы ввели несуществующий логин получателя или время действия его учетной записи истекло'
    
    values = send_message('User_1', '1234567890Ab', 'User_2', 'Сообщение')
    id = values['message_id']
    assert values['response'] == f"Для пользователя User_2 сформерован идентификатор: {id}"

def test_open_message(add_user, add_message):
    assert open_message('User_3', '1234567890Ab', add_message) == 'Вы ввели несуществующий логин или время действия вашей учетной записи истекло'
    assert open_message('User_2', '1234567890Abc', add_message) == 'Вы ввели неправильный пароль'
    assert open_message('User_2', '1234567890Ab', '1234567890abcdef') == 'Сообщения с таким идентификатором не существует или его срок хранения истек'
    assert open_message('User_1', '1234567890Ab', add_message) == 'Сообщение предназначено другому пользователю'

    values = open_message('User_2', '1234567890Ab', add_message)
    message = values['message']
    assert values['response'] == f"Пользователь User_1 отправил Вам сообщение: {message}"

    #проверка на то, что сообщение было удалено после прочтения
    assert open_message('User_2', '1234567890Ab', add_message) == 'Сообщения с таким идентификатором не существует или его срок хранения истек'

if __name__ == "__main__":
    pytest.main()
