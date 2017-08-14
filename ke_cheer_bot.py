from pprint import pprint
from cheerbot_db import Cheerbot_DB
import datetime_util
import json
import keyboard_formatter
import sys
import time
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent
import training

# Talk to 'Telegram'
# @ke_cheer_bot
# Click on the link
# Press start

"""
# Only for deployment to PythonAnywhere

import urllib3
# You can leave this bit out if you're using a paid PythonAnywhere account
proxy_url = "http://proxy.server:3128"
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
}
telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))
# end of the stuff that's only needed for free accounts
"""

bot = telepot.Bot('379881150:AAG2jacR7YBD_t2lc1v4RogoR-RCe09z6PU')
EXCO_CHAT_ID = 165100852# -219149765
TITANS_CHAT_ID = 165100852# -198395968
CAPTAIN_USER_ID = 165100852
temp_messages = []
db = Cheerbot_DB()
# db.drop_tables() # Turn this off in production
db.setup()

# Obtain a chat message and handle it accordingly
def on_chat_message(msg):
	# pprint(msg)
	user_id = msg['from']['id']
	chat_id = msg['chat']['id']
	db.add_or_update_user(msg)
	if msg['text'].startswith('/update'):
		if chat_id != EXCO_CHAT_ID and user_id != CAPTAIN_USER_ID:
			bot.sendMessage(chat_id, "OI " + msg['from']['first_name'] + " mai lai. No permission to see.")
		else:
			# Prompt them to select a date (buttons)
			# Give attendance for that date
			upcoming_trainings = db.get_current_and_upcoming_trainings()
			if len(upcoming_trainings) == 0:
				bot.sendMessage(chat_id, 'No available trainings leh...')
				return
			dates = [training.get_datetime(upcoming_training) for upcoming_training in upcoming_trainings]
			training_ids = [upcoming_training[0] for upcoming_training in upcoming_trainings]
			markup = InlineKeyboardMarkup(inline_keyboard=keyboard_formatter.format(dates, callback_data_list=['/update ' + str(training_id) for training_id in training_ids], ncols=1))
			temp_messages.append(bot.sendMessage(chat_id, 'Please choose a date', reply_markup = markup))
	elif msg['text'].startswith('/remind'):
		if user_id != CAPTAIN_USER_ID:
			bot.sendMessage(chat_id, "OI " + msg['from']['first_name'] + " mai lai. No permission to remind.")
		else:
			# Prompt them to select a date (buttons)
			# Remind titans main chat for that date
			upcoming_trainings = db.get_upcoming_trainings()
			if len(upcoming_trainings) == 0:
				bot.sendMessage(chat_id, 'No available trainings leh...')
				return
			dates = [training.get_datetime(upcoming_training) for upcoming_training in upcoming_trainings]
			training_ids = [upcoming_training[0] for upcoming_training in upcoming_trainings]
			markup = InlineKeyboardMarkup(inline_keyboard=keyboard_formatter.format(dates, callback_data_list=['/remind ' + str(training_id) for training_id in training_ids], ncols=1))
			temp_messages.append(bot.sendMessage(chat_id, 'Please choose a date', reply_markup = markup))
	elif msg['text'].startswith('/set_training'):
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
	elif msg['text'].startswith('/can_go'):
		if msg['chat']['type'] != 'private':
			bot.sendMessage(chat_id, "Please click on me (@ke_cheer_bot) and send your reply there instead.")
		else:
			# Bot will collect more info from user about dates
			upcoming_trainings = db.get_upcoming_trainings()
			if len(upcoming_trainings) == 0:
				bot.sendMessage(user_id, 'No available trainings leh...')
				return
			dates = [training.get_datetime(upcoming_training) for upcoming_training in upcoming_trainings]
			training_ids = [upcoming_training[0] for upcoming_training in upcoming_trainings]
			markup = InlineKeyboardMarkup(inline_keyboard=keyboard_formatter.format(dates, callback_data_list=['/can_go ' + str(training_id) for training_id in training_ids], ncols=1))
			temp_messages.append(bot.sendMessage(chat_id, 'Please choose a date', reply_markup = markup))
	elif msg['text'].startswith('/cant_go'):
		if msg['chat']['type'] != 'private':
			bot.sendMessage(chat_id, "Please click on me (@ke_cheer_bot) and send your reply there instead.")
		else:
			# Bot will collect more info from user about dates and reason
			upcoming_trainings = db.get_upcoming_trainings()
			if len(upcoming_trainings) == 0:
				bot.sendMessage(user_id, 'No available trainings leh...')
				return
			dates = [training.get_datetime(upcoming_training) for upcoming_training in upcoming_trainings]
			training_ids = [upcoming_training[0] for upcoming_training in upcoming_trainings]
			markup = InlineKeyboardMarkup(inline_keyboard=keyboard_formatter.format(dates, callback_data_list=['/cant_go ' + str(training_id) for training_id in training_ids], ncols=1))
			temp_messages.append(bot.sendMessage(chat_id, 'Please choose a date', reply_markup = markup))

# Obtain a callback query and handle it accordingly
def on_callback_query(msg):
	# pprint(msg)
	msg_id = msg['message']['message_id']
	query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
	if query_data.startswith('/set_training'):
		split_data = query_data.split(' ')
		if len(split_data) == 2:
			edit_previous_temp_message_id(from_id, 'Training type is set.')
			# /set_training <training_type>
			# Select venue
			venues = ['Communal', 'Dining', 'Tennis', 'Others']
			markup = InlineKeyboardMarkup( \
				inline_keyboard=keyboard_formatter.format(venues, \
					callback_data_list=[query_data + ' ' + venue for venue in venues], \
				ncols=2))
			temp_messages.append(bot.sendMessage(from_id, 'Please choose a venue', reply_markup = markup))
		elif len(split_data) == 3:
			edit_previous_temp_message_id(from_id, 'Venue is set.')
			# /set_training <training_type> <venue>
			# Select month
			months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
			markup = InlineKeyboardMarkup( \
				inline_keyboard=keyboard_formatter.format(months, \
					callback_data_list=[query_data + ' ' + month for month in months], \
				ncols=4))
			temp_messages.append(bot.sendMessage(from_id, 'Please choose a month', reply_markup = markup))
		elif len(split_data) == 4:
			edit_previous_temp_message_id(from_id, 'Month is set.')
			# /set_training <training_type> <venue> <month>
			# Select day-of-month
			month = split_data[-1]
			days = [str(i) for i in range(datetime_util.first_valid_day_of(month), datetime_util.last_day_of(month) + 1)]
			markup = InlineKeyboardMarkup( \
				inline_keyboard=keyboard_formatter.format(days, \
					callback_data_list=[query_data + ' ' + day for day in days], \
				ncols=7))
			temp_messages.append(bot.sendMessage(from_id, 'Please choose a day\nFirst column is ' + datetime_util.first_valid_day_of_week(month), reply_markup = markup))
		elif len(split_data) == 5:
			edit_previous_temp_message_id(from_id, 'Day is set.')
			# /set_training <training_type> <venue> <month> <day>
			# Select start time
			timings = ['1900', '1930', '2000', '2030', '2100', '2130', '2200']
			markup = InlineKeyboardMarkup( \
				inline_keyboard=keyboard_formatter.format(timings, \
					callback_data_list=[query_data + ' ' + timing for timing in timings], \
				ncols=2))
			temp_messages.append(bot.sendMessage(from_id, 'Please choose a start time', reply_markup = markup))
		elif len(split_data) == 6:
			edit_previous_temp_message_id(from_id, 'Start time is set.')
			# /set_training <training_type> <venue> <month> <day> <start_time>
			# Select duration
			timings = ['2100', '2130', '2200', '2230', '2300', '2330', '0000']
			markup = InlineKeyboardMarkup( \
				inline_keyboard=keyboard_formatter.format(timings, \
					callback_data_list=[query_data + ' ' + timing for timing in timings], \
				ncols=2))
			temp_messages.append(bot.sendMessage(from_id, 'Please choose an end time', reply_markup = markup))
		elif len(split_data) == 7:
			edit_previous_temp_message_id(from_id, 'End time is set.')
			# /set_training <training_type> <venue> <month> <day> <start_time> <end_time>
			# Select confirmation (YES/NO)
			confirmations = ['Yes', 'No']
			markup = InlineKeyboardMarkup( \
				inline_keyboard=keyboard_formatter.format(confirmations, \
					callback_data_list=[query_data + ' ' + confirmation for confirmation in confirmations], \
				ncols=2))
			temp_messages.append(bot.sendMessage(from_id, 'Please confirm the following details:\n' + training.get_training_details(split_data), reply_markup = markup))
		elif len(split_data) == 8:
			edit_previous_temp_message_id(from_id, 'Confirmation is set.')
			# /set_training <training_type> <venue> <month> <day> <start_time> <end_time> <YES/NO>
			if split_data[-1] == 'No':
				bot.answerCallbackQuery(query_id, text='Training details is not saved. Please redo if needed.')
			else:
				training_tuple = training.get_training(split_data)
				db.add_training(training_tuple[0], training_tuple[1], training_tuple[2], training_tuple[3])
				bot.answerCallbackQuery(query_id, text='Training details is saved and sent to Titans Chat')
				bot.sendMessage(TITANS_CHAT_ID, training.get_chat_training_details(split_data))
				return
		else:
			# Throw error
			pass
		bot.answerCallbackQuery(query_id, text='Selected: ' + query_data.split(' ')[-1])
	elif query_data.startswith('/can_go'):
		edit_previous_temp_message_id(from_id, 'Going for this training.')
		db.add_or_update_attendance(msg)
		bot.answerCallbackQuery(query_id, text='Training date is chosen.')
		bot.sendMessage(from_id, "Yay, you're coming! :D")
	elif query_data.startswith('/cant_go'):
		edit_previous_temp_message_id(from_id, 'Not going for this training.')
		db.add_or_update_attendance(msg)
		bot.answerCallbackQuery(query_id, text='Training date is chosen.')
		bot.sendMessage(from_id, "Nuuuuuuuuuu... T.T Cya next training then!")
		# markup = ForceReply()
		# training_id = query_data.split(' ')[-1]
		# temp_unattendance.append((training_id, from_id))
		# temp_messages.append(bot.sendMessage(from_id, 'Please provide a reason', reply_markup = markup))
	elif query_data.startswith('/update'):
		# edit_previous_temp_message_id(from_id, 'Training date is chosen.')
		bot.answerCallbackQuery(query_id, text='Training date is chosen.')
		training_id = query_data.split(' ')[1]
		training_details = db.find_training(training_id)
		training_details = training_details[0] if len(training_details) > 0 else ('this', 'is', 'a', 'place', 'holder') 
		attendances = db.get_attendances(training_id)
		no_reply_user_ids = db.get_no_reply_user_ids(training_id)
		bot.sendMessage(EXCO_CHAT_ID, training.get_attendance_details(db, training_details, attendances, no_reply_user_ids))
	elif query_data.startswith('/remind'):
		bot.answerCallbackQuery(query_id, text='Training date is chosen.')
		training_id = query_data.split(' ')[1]
		training_details = db.find_training(training_id)
		training_details = training_details[0] if len(training_details) > 0 else ('this', 'is', 'a', 'place', 'holder') 
		no_reply_user_ids = db.get_no_reply_user_ids(training_id)
		bot.sendMessage(TITANS_CHAT_ID, training.get_reminder_details(db, training_details, no_reply_user_ids))

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
