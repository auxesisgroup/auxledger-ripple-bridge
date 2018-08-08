import telepot
token = '650314389:AAHgry_aMyS4vpvpgErNNfHkVEwzpaSnHPU'
tele_bot = telepot.Bot(token)
print tele_bot.getMe()
print tele_bot.getUpdates()
# tele_bot.sendMessage('565177104','Hi')
# tele_bot.sendMessage('669302591','Hi',reply_to_message_id=2,disable_notification=True)

