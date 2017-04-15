from pprint import pprint

import datetime_formatter
import json
import keyboard_formatter
import sys
import time
import telepot
import telepot.aio
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent
import training

# Talk to 'Telegram'
# @ke_cheer_bot
# Click on the link
# Press start

bot = telepot.Bot('379881150:AAG2jacR7YBD_t2lc1v4RogoR-RCe09z6PU')
EXCO_CHAT_ID = -219149765
TITANS_CHAT_ID = -219149765 # This is actually exco chat.
CAPTAIN_USER_ID = 165100852
temp_messages = []

# Reading json file
def read_json(filename):
    datafile = open(filename, 'r',  encoding='utf-8')
    return json.loads(datafile.read())
 
# CS1010S Facebok Group Data as a dictionary object
#bot_data = read_json('cs1010s-fbdata.json')

# Obtain a chat message and handle it accordingly
def on_chat_message(msg):
	# pprint(msg)
	user_id = msg['from']['id']
	chat_id = msg['chat']['id']
	if msg['text'] == '/update':
		if chat_id != EXCO_CHAT_ID:
			bot.sendMessage(chat_id, "OI " + msg['from']['first_name'] + " mai lai. No permission to see.")
		else:
			# Prompt them to select a date (buttons)
			# Give attendance for that date
			bot.sendMessage(chat_id, "No updates yet. Wait long long")
	elif msg['text'] == '/set_training':
		if user_id != CAPTAIN_USER_ID:
			bot.sendMessage(chat_id, "OI " + msg['from']['first_name'] + " mai lai. No permission to set training.")
		elif chat_id in [TITANS_CHAT_ID, EXCO_CHAT_ID]:
			bot.sendMessage(chat_id, "OI " + msg['from']['first_name'] + ", cannot set training in group chat lah. Click @ke_cheer_bot and set training there.")
		else:
			# Bot will collect info from Captain about dates and training_type
			# In Titans chat, bot will announce training, click on him to confirm.
			training_types = ['Training', 'OTOT']
			markup = InlineKeyboardMarkup(inline_keyboard=keyboard_formatter.format(training_types, callback_data_list=['/set_training ' + training_type for training_type in training_types], ncols=2))
			temp_messages.append(bot.sendMessage(chat_id, 'Please choose a training type', reply_markup = markup))
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
	pprint(msg)
	msg_id = msg['message']['message_id']
	query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
	if query_data.startswith('/set_training'):
		split_data = query_data.split(' ')
		if len(split_data) == 2:
			edit_previous_temp_message_id(from_id, 'Training type is set.')
			# /set_training <training_type>
			# Select venue
			venues = ['Communal', 'Dining', 'Tennis', 'Others']
			markup = InlineKeyboardMarkup(inline_keyboard=keyboard_formatter.format(venues, callback_data_list=[query_data + ' ' + venue for venue in venues], ncols=2))
			temp_messages.append(bot.sendMessage(from_id, 'Please choose a venue', reply_markup = markup))
		elif len(split_data) == 3:
			edit_previous_temp_message_id(from_id, 'Venue is set.')
			# /set_training <training_type> <venue>
			# Select month
			months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
			markup = InlineKeyboardMarkup(inline_keyboard=keyboard_formatter.format(months, callback_data_list=[query_data + ' ' + month for month in months], ncols=4))
			temp_messages.append(bot.sendMessage(from_id, 'Please choose a month', reply_markup = markup))
		elif len(split_data) == 4:
			edit_previous_temp_message_id(from_id, 'Month is set.')
			# /set_training <training_type> <venue> <month>
			# Select day-of-month
			month = split_data[-1]
			days = [str(i) for i in range(datetime_formatter.first_valid_day_of(month), datetime_formatter.last_day_of(month) + 1)]
			markup = InlineKeyboardMarkup(inline_keyboard=keyboard_formatter.format(days, callback_data_list=[query_data + ' ' + day for day in days], ncols=7))
			temp_messages.append(bot.sendMessage(from_id, 'Please choose a day\nFirst column is ' + datetime_formatter.first_valid_day_of_week(month), reply_markup = markup))
		elif len(split_data) == 5:
			edit_previous_temp_message_id(from_id, 'Day is set.')
			# /set_training <training_type> <venue> <month> <day>
			# Select start time
			timings = ['1900', '1930', '2000', '2030', '2100', '2130', '2200']
			markup = InlineKeyboardMarkup(inline_keyboard=keyboard_formatter.format(timings, callback_data_list=[query_data + ' ' + timing for timing in timings], ncols=2))
			temp_messages.append(bot.sendMessage(from_id, 'Please choose a start time', reply_markup = markup))
		elif len(split_data) == 6:
			edit_previous_temp_message_id(from_id, 'Start time is set.')
			# /set_training <training_type> <venue> <month> <day> <start_time>
			# Select duration
			durations = ['1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5', '5.5']
			markup = InlineKeyboardMarkup(inline_keyboard=keyboard_formatter.format(durations, callback_data_list=[query_data + ' ' + duration for duration in durations], ncols=2))
			temp_messages.append(bot.sendMessage(from_id, 'Please choose a duration (in hours)', reply_markup = markup))
		elif len(split_data) == 7:
			edit_previous_temp_message_id(from_id, 'Duration is set.')
			# /set_training <training_type> <venue> <month> <day> <start_time> <duration>
			# Select confirmation (YES/NO)
			confirmations = ['Yes', 'No']
			markup = InlineKeyboardMarkup(inline_keyboard=keyboard_formatter.format(confirmations, callback_data_list=[query_data + ' ' + confirmation for confirmation in confirmations], ncols=2))
			temp_messages.append(bot.sendMessage(from_id, 'Please confirm the following details:\n' + training.get_training_details(split_data), reply_markup = markup))
		elif len(split_data) == 8:
			edit_previous_temp_message_id(from_id, 'Confirmation is set.')
			# /set_training <training_type> <venue> <month> <day> <start_time> <duration> <YES/NO>
			if split_data[-1] == 'No':
				bot.answerCallbackQuery(query_id, text='Training details is not saved. Please redo if needed.')
			else:
				# ADD TRAINING TO DATABASE
				bot.answerCallbackQuery(query_id, text='Training details is saved and sent to Titans Chat')
		else:
			# Throw error
			pass
	bot.answerCallbackQuery(query_id, text='Selected: ' + query_data.split(' ')[-1])

def edit_previous_temp_message_id(from_id, new_text):
	message = get_previous_temp_message(from_id)
	message_identifier = telepot.message_identifier(message)
	bot.editMessageText(message_identifier, new_text)
	temp_messages.remove(message)

def get_previous_temp_message(from_id):
	messages_by_user = list(filter(lambda x: x['chat']['id'] == from_id, temp_messages))
	# Handle what happens if there are more than 1 message by user in temp_messages
	message_by_user = messages_by_user[0]
	return message_by_user


# Constantly receives messages and handle it
bot.message_loop({'chat': on_chat_message, 'callback_query': on_callback_query})

# Keep the program running
while 1:
    time.sleep(10)
