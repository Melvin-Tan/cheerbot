import datetime

"""
Args example format
  day: 19
month: 'Jul'
 year: 2017
 time: '2030'
"""

# Convert UNIX date to human-readable datetime string
def get_local_datetime(unix_date):
	return datetime.datetime.fromtimestamp(unix_date).strftime('%d-%m-%Y %H:%M:%S')

def get_time_from_datetime(datetime):
	return str(datetime.hour) + '.' + datetime.strftime('%M%p')

def get_time_from_time(time):
	hour = int(time[:2])
	minute = time[2:]
	am_or_pm = 'AM' if hour < 12 else 'PM'
	hour = hour % 12
	return str(hour) + '.' + minute + am_or_pm

# Get the date for a given day and month
def get_datetime(day, month, time):
	return datetime.datetime(get_year(day, month), to_numeric_month(month), int(day), int(time[:2]), int(time[2:]))

# Get the year for a given day and month
def get_year(day, month):
	today = datetime.date.today()
	month_numeric = to_numeric_month(month)
	date = datetime.date(today.year, month_numeric, int(day))
	return date.year + 1 if (date < today) else date.year

# Get the first valid day of a given month
def first_valid_day_of(month):
	today = datetime.date.today()
	if today.month != to_numeric_month(month):
		return 1
	else:
		return today.day

# Get first valid day of week of a given month (e.g. Tue)
def first_valid_day_of_week(month):
	return day_of_week(first_valid_day_of(month), month)

# Get day of week
def day_of_week(day, month):
	today = datetime.date.today()
	month_numeric = to_numeric_month(month)
	date = datetime.date(today.year, month_numeric, int(day))
	if (date < today):
		date = datetime.date(today.year + 1, month_numeric, day)
	return date.strftime('%A')

# Get the last day of a given month
def last_day_of(month):
	if (month in ['Jan', 'Mar', 'May', 'Jul', 'Aug', 'Oct', 'Dec']):
		return 31
	elif (month in ['Apr', 'Jun', 'Sep', 'Nov']):
		return 30
	else: # month == 'Feb'
		today = datetime.date.today()
		year = today.year if today.month <= to_numeric_month('Feb') else today.year + 1
		return 29 if is_leap_year(year) else 28

# Checks whether a year is a leap year
def is_leap_year(year):
	return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

# Convert month in string to number
def to_numeric_month(month):
	months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	return months.index(month) + 1

# Convert month in number to string
def to_string_month(month_number):
	months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	return months[month_number - 1]