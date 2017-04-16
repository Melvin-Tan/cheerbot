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
			+ 'coming boolean, ' \
			+ 'reason text)'
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

	def find_training(self, training_id):
		statement = 'SELECT * FROM trainings WHERE training_id = (?) LIMIT 1'
		args = (training_id,)
		return [x for x in self.conn.execute(statement, args)]

	def get_upcoming_trainings(self):
		statement = "SELECT * FROM trainings WHERE datetime('now') < end_datetime"
		return [x for x in self.conn.execute(statement)]

	def find_user(self, user_id):
		statement = 'SELECT * FROM users WHERE user_id = (?) LIMIT 1'
		args = (user_id,)
		return [x for x in self.conn.execute(statement, args)]

	def update_user_info(self, user_id, user_name, name):
		statement = 'UPDATE users SET user_name = (?), name = (?) WHERE user_id = (?)'
		args = (user_name, name, user_id)
		self.conn.execute(statement, args)
		self.conn.commit()

	def set_user_access(self, user_id, is_admin):
		statement = 'UPDATE users SET admin = (?) WHERE user_id = (?)'
		admin = 1 if is_admin else 0
		args = (admin, user_id)
		self.conn.execute(statement, args)
		self.conn.commit()

	def add_user(self, user_id, user_name, name):
		statement = 'INSERT INTO users (user_id, user_name, name, admin) ' \
			+ ' VALUES (?, ?, ?, ?)'
		args = (user_id, user_name, name, 0)
		self.conn.execute(statement, args)
		self.conn.commit()

	def add_or_update_user(self, user_id, user_name, name):
		if len(self.find_user(user_id)) == 0:
			self.add_user(user_id, user_name, name)
		else:
			self.update_user_info(user_id, user_name, name)

	def find_attendance(self, training_id, user_id):
		statement = 'SELECT * FROM attendances WHERE training_id = (?) AND user_id = (?) LIMIT 1'
		args = (training_id, user_id)
		return [x for x in self.conn.execute(statement, args)]

	def get_attendances(self, training_id):
		statement = 'SELECT * FROM attendances WHERE training_id = (?) ORDER BY coming'
		args = (training_id,)
		return [x for x in self.conn.execute(statement, args)]

	def add_attendance(self, training_id, user_id, coming):
		statement = 'INSERT INTO attendances (training_id, user_id, coming) ' \
			+ ' VALUES (?, ?, ?)'
		args = (training_id, user_id, coming)
		self.conn.execute(statement, args)
		self.conn.commit()

	def update_attendance(self, training_id, user_id, coming):
		statement = 'UPDATE attendances SET coming = (?) WHERE training_id = (?) AND user_id = (?)'
		args = (coming, training_id, user_id)
		self.conn.execute(statement, args)
		self.conn.commit()

	def add_or_update_attendance(self, msg):
		can_attend = 1 if msg['data'].startswith('/can_go') else 0
		training_id = msg['data'].split(' ')[1]
		# reason = ' '.join(msg['data'].split(' ')[2:])
		# Handle user
		chat = msg['message']['chat']
		user_id = chat['id']
		self.add_or_update_user(user_id, chat['username'], chat['first_name'])
		# Handle attendance
		if len(self.find_attendance(training_id, user_id)) == 0:
			self.add_attendance(training_id, user_id, can_attend)
		else:
			self.update_attendance(training_id, user_id, can_attend)
