from pprint import pprint

import datetime_formatter
import json
import sys
import time
import telepot
import telepot.aio
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent

# Talk to 'Telegram'
# @ke_cheer_bot
# Click on the link
# Press start

bot = telepot.Bot('379881150:AAG2jacR7YBD_t2lc1v4RogoR-RCe09z6PU')
EXCO_CHAT_ID = -219149765
TITANS_CHAT_ID = -219149765 # This is actually exco chat.
CAPTAIN_USER_ID = 165100852

# Reading json file
def read_json(filename):
    datafile = open(filename, 'r',  encoding='utf-8')
    return json.loads(datafile.read())
 
# CS1010S Facebok Group Data as a dictionary object
#bot_data = read_json('cs1010s-fbdata.json')

# Obtain a chat message and handle it accordingly
def on_chat_message(msg):
	pprint(msg)
	user_id = msg['from']['id']
	chat_id = msg['chat']['id']
	if msg['text'] == '/update':
		if chat_id != EXCO_CHAT_ID:
			bot.sendMessage(chat_id, "OI, mai lai. No permission to see.")
		else:
			# Prompt them to select a date (buttons)
			# Give attendance for that date
			bot.sendMessage(chat_id, "No updates yet. Wait long long")
	elif msg['text'] == '/set_training':
		if user_id != CAPTAIN_USER_ID or (not chat_id in [CAPTAIN_USER_ID, EXCO_CHAT_ID]):
			bot.sendMessage(chat_id, "OI, mai lai. No permission to set training.")
		else:
			# Bot will collect info from Captain about dates and official/unofficial
			# In Titans chat, bot will announce training, click on him to confirm.
			markup = InlineKeyboardMarkup(inline_keyboard=[                 \
					[dict(text='Jan', callback_data='Jan'), \
					dict(text='Feb', callback_data='Feb'),  \
					dict(text='Mar', callback_data='Mar')], \
					[dict(text='Apr', callback_data='Apr'), \
					dict(text='May', callback_data='May'),  \
					dict(text='Jun', callback_data='Jun')], \
					[dict(text='Jul', callback_data='Jul'), \
					dict(text='Aug', callback_data='Aug'),  \
					dict(text='Sep', callback_data='Sep')], \
					[dict(text='Oct', callback_data='Oct'), \
					dict(text='Nov', callback_data='Nov'),  \
					dict(text='Dec', callback_data='Dec')]  \
					])
			bot.sendMessage(chat_id, 'Please choose a month', reply_markup = markup)
			# bot.sendMessage(TITANS_CHAT_ID, "Ok hold training. More to be done...")
	elif msg['text'] == '/can_go':
		if msg['chat']['type'] != 'private':
			bot.sendMessage(chat_id, "Please click on me (@ke_cheer_bot) and send your reply there instead.")
		else:
			# Bot will collect more info from user about dates
			bot.sendMessage(chat_id, "Yay, you're coming!")
	elif msg['text'] == '/cant_go':
		if msg['chat']['type'] != 'private':
			bot.sendMessage(chat_id, "Please click on me (@ke_cheer_bot) and send your reply there instead.")
		else:
			# Bot will collect more info from user about dates and reason
			bot.sendMessage(chat_id, "Nuuuuuuuuuu... T.T")

# Obtain a callback query and handle it accordingly
def on_callback_query(msg):
	query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
	print('Callback Query:', query_id, from_id, query_data)

	bot.answerCallbackQuery(query_id, text='Got it')

# Constantly receives messages and handle it
bot.message_loop({'chat': on_chat_message, 'callback_query': on_callback_query})

# Keep the program running
while 1:
    time.sleep(10)