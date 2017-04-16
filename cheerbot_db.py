import sqlite3

class Cheerbot_DB:
	def __init__(self, db_name = 'cheerbot.sqlite'):
		self.db_name = db_name
		self.conn = sqlite3.connect(db_name, check_same_thread = False)

	def setup(self):
		training_table = 'CREATE TABLE IF NOT EXISTS trainings (' \
			+ 'training_id integer, ' \
			+ 'venue text, ' \
			+ 'start_datetime datetime, ' \
			+ 'end_datetime datetime, ' \
			+ 'training_type text)'
		user_table = 'CREATE TABLE IF NOT EXISTS users (' \
			+ 'user_id integer, ' \
			+ 'user_name text, ' \
			+ 'name text, ' \
			+ 'admin boolean)'
		attendance_table = 'CREATE TABLE IF NOT EXISTS attendances (' \
			+ 'training_id integer, ' \
			+ 'user_id integer, ' \
			+ 'coming boolean)'
		self.conn.execute(training_table)
		self.conn.execute(user_table)
		self.conn.execute(attendance_table)
		self.conn.commit()

	def get_table_size(self, table):
		statement = 'SELECT COUNT(*) FROM ' + table
		return self.conn.execute(statement).fetchone()[0]

	def add_training(self, venue, start_datetime, end_datetime, training_type):
		training_id = self.get_table_size('trainings') + 1
		statement = 'INSERT INTO trainings (training_id, venue, start_datetime, end_datetime, training_type) ' \
			+ ' VALUES (?, ?, ?, ?, ?)'
		args = (training_id, venue, start_datetime, end_datetime, training_type)
		self.conn.execute(statement, args)
		self.conn.commit()

	def get_upcoming_trainings(self):
		statement = "SELECT * FROM trainings WHERE datetime('now') < end_datetime"
		return [x for x in self.conn.execute(statement)]

	def find_user(self, user_id):
		statement = 'SELECT * FROM users WHERE user_id = (?) LIMIT 1'
		return [x for x in self.conn.execute(statement)]

	def update_user_info(self, user_id, user_name, name):
		statement = 'UPDATE users SET user_name = (?), name = (?) WHERE user_id = (?)'
		args = (user_name, name, user_id)
		self.conn.execute(statement)

	def set_user_access(self, user_id, is_admin):
		statement = 'UPDATE users SET admin = (?) WHERE user_id = (?)'
		admin = 1 if is_admin else 0
		args = (admin, user_id)
		self.conn.execute(statement)

	def add_attendance(self, chat):
		return 

