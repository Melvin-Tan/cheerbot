import datetime
import datetime_util

proper_venue_names = {'Communal' : 'Comm Hall', 'Dining' : 'Dining Hall', 'Tennis' : 'Tennis Court', 'Others' : 'Others'}

def get_training_details(split_data):
	command, training_type, venue, month, day, start_time, end_time = split_data
	return 'Type: ' + training_type + '\n' \
		+ 'At: ' + proper_venue_names[venue] + '\n' \
		+ 'Date: ' + datetime_util.day_of_week(day, month) + ', ' + day + ' ' + month + '\n' \
		+ 'Time: ' + start_time + ' to ' + end_time

def get_chat_training_details(split_data):
	command, training_type, venue, month, day, start_time, end_time, confirmation = split_data
	return 'Hi titans!\n\nUpcoming ' + training_type + '!\n' \
		+ 'At: ' + proper_venue_names[venue] + '\n' \
		+ 'Date: ' + datetime_util.day_of_week(day, month) + ', ' + day + ' ' + month + '\n' \
		+ 'Time: ' + datetime_util.get_time_from_time(start_time) + ' to ' + datetime_util.get_time_from_time(end_time) + '\n\n' \
		+ 'Come down 15 minutes earlier to set up mats thanks!\n\n' \
		+ 'Lastly, do remember to indicate attendance by clicking on me (@ke_cheer_bot) and type /can_go or /cant_go.\n\n' \
		+ 'Cya! :D'

def get_attendance_details(db, training, attendances, no_reply_user_ids):
	return training[4] + ' on ' + get_datetime(training) + ' in ' + training[1] + '\n\n' \
		+ 'No reply:\n' \
		+ get_no_reply_members(db, no_reply_user_ids) + '\n' \
		+ 'Not Coming:\n' \
		+ get_not_coming_members(db, attendances) + '\n' \
		+ 'Coming:\n' \
		+ get_coming_members(db, attendances)

def get_reminder_details(db, training, no_reply_user_ids):
	return 'REMINDER\n\n' + training[4] + ' on ' + get_datetime(training) + ' in ' + training[1] + '\n\n' \
		+ 'Come down 15 minutes earlier to set up mats thanks!\n\n' \
		+ "Lastly, for those who haven't reply:\n" \
		+ get_no_reply_members(db, no_reply_user_ids) \
		+ 'Do remember to indicate attendance by clicking on me (@ke_cheer_bot) and type /can_go or /cant_go.\n\n'
		+ 'Cya on the mats! :D'

def get_no_reply_members(db, no_reply_user_ids):
	result = ''
	list_index = 1
	for user_id in no_reply_user_ids:
		user = db.find_user(user_id[0])[0]
		result += str(list_index) + '. ' + user[2] + ' (@' + user[1] + ')\n'
		list_index += 1
	return result if list_index > 1 else 'All replied, yay!\n'

def get_coming_members(db, attendances):
	result = ''
	list_index = 1
	for attendance in attendances:
		if attendance[2] == 1:
			user = db.find_user(attendance[1])[0]
			result += str(list_index) + '. ' + user[2] + ' (@' + user[1] + ')\n'
			list_index += 1
	return result if list_index > 1 else 'None yet\n'

def get_not_coming_members(db, attendances):
	result = ''
	list_index = 1
	for attendance in attendances:
		if attendance[2] == 0:
			user = db.find_user(attendance[1])[0]
			result += str(list_index) + '. ' + user[2] + ' (@' + user[1] + ')\n'
			list_index += 1
	return result if list_index > 1 else 'None yet\n'

def get_training(split_data):
	command, training_type, venue, month, day, start_time, end_time, confirmation = split_data
	return (proper_venue_names[venue], \
		datetime_util.get_datetime(day, month, start_time), \
		datetime_util.get_datetime(day, month, end_time), \
		training_type)

def get_datetime(training):
	training_id, venue, start_datetime, end_datetime, training_type = training
	start_datetime = datetime.datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
	end_datetime = datetime.datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
	return start_datetime.strftime('%a, %d %b') + ', ' \
		+ datetime_util.get_time_from_datetime(start_datetime) + ' - ' \
		+ datetime_util.get_time_from_datetime(end_datetime)
