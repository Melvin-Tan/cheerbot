import datetime

# Convert UNIX date to human-readable datetime string
def get_local_datetime(unix_date):
	return datetime.datetime.fromtimestamp(unix_date).strftime('%d-%m-%Y %H:%M:%S')
