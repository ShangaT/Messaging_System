Разработка системы безопасной передачи одноразовых текстовых сообщений 

Актуальность:
Допустим, необходимо передать какой-то пароль или ключ, или другое текстовое сообщение, которое точно должно остаться конфиденциальным. 
Удобнее всего это сделать по средствам Интернет по электронной почте или через какой-то мессенджер (например, телеграмм).
НО, даже в том случаи, когда почтовый сервис или мессенджер обладает достаточными средствами защиты при передаче сообщения остается информационный след (цифровой след).
Следовательно, если аккаунт отправителя или получателя взломан, злоумышленник получает доступ ко всем паролям, которые когда-либо были отправлены или получены. 
К тому же, те у кого есть доступ к серверу, также могут получить доступ и к сообщениям.
Таким, образом, необходимо гарантировать удаление секретного сообщения после получения
На сегодняшний день уже существуют системы передачи одноразовых текстовых сообщений. Они реализованы в виде сайтов, где при отправке сообщения формируется одноразовая ссылка для доступа к сообщению. 
НО эти сайты руководствуются анонимностью, то есть непонятно кому предназначалась эта ссылка и кем она сформирована.
Следовательно, ключи шифрования, который должен оставаться секретным передаются в открытом виде. То есть, на этих сайтах ссылка для доступа к сообщению состоит из идентификатора сообщения и ключа шифрования.

Объект исследования: система передачи данных
Предмет исследования: конфиденциальность и доступность текстовых сообщений
Проблема передачи и использования идентификационных ключей

ЦЕЛЬ РАБОТЫ: Разработка механизма аутентификации, идентификации и авторизации при передачи информации по протоколу http.

КРАТКОЕ ОПИСАНИЕ РАБОТЫ СИСТЕМЫ

Регистрация:
1. Из формы на сервер отправляем логин и пароль
2. Рассчитываем время удаления учетной записи
3. Рассчитываем открытый и закрытый RSA ключи 
4. Закрытый ключ шифруем при помощи пароля, алгоритм "Кузнечик" (надежность шифрования зависит от сложности пароля)
5. Логин, хэш пароля, открытый ключ, зашифрованный закрытый ключ, время удаления учетной записи сохраняем на сервере

Отправка сообщения:
1. Из формы считываем логин и пароль отправителя, логин получателя, сообщение
2. Присваиваем сообщению уникальный идентификатор
3. По логину получателя находим открытый ключ получателя
4. Шифруем сообщение при помощи открытого ключа
5. Рассчитываем время удаления сообщения
6. Идентификатор, отправителя, получателя, зашифрованное сообщение, время удаления сообщения сохраняем на сервере
7. Отправителю выводится идентификатор сообщения, который необходимо отправить получателю любым способом

Просмотр сообщения:
1. Из формы считывается идентификатор сообщения, логин и пароль
2. По идентификатору находится нужное сообщение
3. При помощи пароля расшифровывается закрытый ключ RSA
4. При помощи расшифрованного закрытого ключа расшифровывается сообщение
5. Расшифрованное сообщение выводим пользователю
6. Удаляем сообщение из базы

Если время хранения сообщения на сервере превысило 7 дней, сообщение будет удалено, даже если оно не бело прочитано.
Если время действия учетной записи превысило 365 дней, пользователю необходимо зарегистрироваться повторно.
Невозможно отправить сообщение пользователю, которого нет в базе.

Регистрация проходит ~9 c., так как медленно рассчитываются RSA ключи

Данные от пользователя к серверу передаются в открытом виде, но по зашифрованному каналу связи при помощи OpenSSl 

Где хранить SSl ключи?
