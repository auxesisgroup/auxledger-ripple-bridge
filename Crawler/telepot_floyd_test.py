import time
import random
import datetime
import telepot
from telepot.loop import MessageLoop

def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']

    print 'Got command: %s' % command

    if command == '/start':
        bot.sendMessage(chat_id, 'Hello')
        time.sleep(1)
        bot.sendMessage(chat_id, 'I know you have nothing to do')
        time.sleep(2)
        bot.sendMessage(chat_id, 'So lets dig into something useful')
        time.sleep(2)
        bot.sendMessage(chat_id, 'Wubba Lubba Dub Dub')
        time.sleep(1)
        bot.sendMessage(chat_id, 'Ok')
        time.sleep(1)
        bot.sendMessage(chat_id, 'what if you are high')
        time.sleep(2)
        bot.sendMessage(chat_id, 'And you need to choose to one person to hangout with')
        time.sleep(1)
        bot.sendMessage(chat_id, 'Whom would you choose?')
        time.sleep(1)
        bot.sendMessage(chat_id, '1. Tejinder')
        time.sleep(1)
        bot.sendMessage(chat_id, '2. Runa')
        time.sleep(1)
        bot.sendMessage(chat_id, '3. Rajesh Photography')
        time.sleep(1)
        bot.sendMessage(chat_id, '4. I am sorry you dont have more options')
        time.sleep(1)
        bot.sendMessage(chat_id, 'Please choose an option.')
        time.sleep(1)
        bot.sendMessage(chat_id, 'To restart : Send /start')
    if command == '1':
        bot.sendMessage(chat_id, 'well deserved')
    if command == '2':
        bot.sendMessage(chat_id, 'That good for you')
    if command == '3':
        bot.sendMessage(chat_id, 'deal with it')
    if command not in ['1','2','3','/start']:
        bot.sendMessage(chat_id,'You are not so clever. I am sorry')


bot = telepot.Bot('650314389:AAHgry_aMyS4vpvpgErNNfHkVEwzpaSnHPU')

MessageLoop(bot, handle).run_as_thread()
print 'I am listening ...'

while 1:
    time.sleep(10)
