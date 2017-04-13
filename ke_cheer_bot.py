import datetime
from pprint import pprint
import sys
import time
import telepot

# Talk to 'Telegram'
# @ke_cheer_bot
# Click on the link
# Press start

bot = telepot.Bot('379881150:AAG2jacR7YBD_t2lc1v4RogoR-RCe09z6PU')
# print(bot.getMe())

# Obtain a message and handle it accordingly
def handle(msg):
	relevant_info = get_relevant_info(msg)
	user_id = relevant_info['from']['id']
	bot.sendMessage(user_id, "You just sent: " + relevant_info['text'])
	pprint(relevant_info)

# Convert UNIX date to human-readable datetime string
def get_local_datetime(unix_date):
	return datetime.datetime.fromtimestamp(unix_date).strftime('%d-%m-%Y %H:%M:%S')

# Filter only useful information from message
def get_relevant_info(msg):
	return {'from' : msg['from'],
			'text' : msg['text'],
			'date' : get_local_datetime(msg['date'])}

# Constantly receives messages and handle it
bot.message_loop(handle)

# Keep the program running
while 1:
    time.sleep(10)