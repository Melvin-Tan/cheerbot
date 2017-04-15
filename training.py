import datetime_formatter

def get_training_details(split_data):
	command, training_type, venue, month, day, start_time, duration = split_data
	return 'Type: ' + training_type + '\n' \
		+ 'At: ' + venue + '\n' \
		+ 'Date: ' + datetime_formatter.day_of_week(day, month) + ', ' + day + ' ' + month + '\n' \
		+ 'Time: ' + start_time + '\n' \
		+ 'Duration: ' + duration + 'h'
