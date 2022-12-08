import datetime
import time



a = datetime.datetime.now() #расчитали время сейчас
c = a+datetime.timedelta(minutes = 1)
print(a)
print(c)
#time.sleep(5)
date_time_str = '2022-12-09 08:15:27.243860'
b = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f') #преобразуем строку в формат даты и времени
print(b)
print (c-a)

if a >= b:
    print('время истекло')
else: print ('еще действует')

# while True:
