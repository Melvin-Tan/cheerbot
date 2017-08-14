import os
import psycopg2
import datetime_util

DATABASE_URL = os.environ.get('DATABASE_URL')

class Cheerbot_DB:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)

    def query(self, sql, data = ()):
        try:
            cur = self.conn.cursor()
            return [x for x in cur.execute(sql, data).fetchall()]
        except Exception as e:
            print(e)

    def mutate(self, sql, data = ()):
        try:
            cur = self.conn.cursor()
            cur.execute(sql, data)
            self.conn.commit()
        except Exception as e:
            print(e)

    def drop_tables(self):
        self.mutate('DROP TABLE IF EXISTS trainings')
        self.mutate('DROP TABLE IF EXISTS users')
        self.mutate('DROP TABLE IF EXISTS attendances')

    def setup(self):
        self.mutate(
            """
            CREATE TABLE IF NOT EXISTS trainings (
                training_id integer,
                venue text,
                start_datetime timestamp,
                end_datetime timestamp,
                training_type text
            );
            """
        )
        self.mutate(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id integer,
                user_name text,
                name text,
                admin boolean
            );
            """
        )
        self.mutate(
            """
            CREATE TABLE IF NOT EXISTS attendances (
                training_id integer,
                user_id integer,
                coming boolean,
                reason text
            );
            """
        )

    def get_table_size(self, table):
        sql = """
              SELECT COUNT(*)
              FROM %(table)s;
              """
        data = {'table': table}
        cur = self.conn.cursor()
        return cur.execute(statement).fetchone()[0]

    def add_training(self, venue, start_datetime, end_datetime, training_type):
        training_id = self.get_table_size('trainings') + 1
        sql = """
              INSERT INTO trainings (training_id, venue, start_datetime, end_datetime, training_type)
              VALUES (%(training_id)s, %(venue)s, %(start_datetime)s, %(end_datetime)s, %(training_type)s);
              """
        data = {'training_id': training_id,
                'venue': venue,
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'training_type': training_type}
        self.mutate(sql, data)

    def find_training(self, training_id):
        sql = """
              SELECT * 
              FROM trainings 
              WHERE training_id = %(training_id)s
              LIMIT 1;
              """
        data = {'training_id': training_id}
        return self.query(sql, data)

    def get_upcoming_trainings(self):
        datetime_now = datetime_util.get_now()
        sql = """
              SELECT * 
              FROM trainings 
              WHERE %(datetime_now)s < start_datetime 
              ORDER BY start_datetime;
              """
        data = {'datetime_now' : datetime_now}
        return self.query(sql, data)

    def get_current_and_upcoming_trainings(self):
        datetime_now = datetime_util.get_now()
        sql = """
              SELECT * 
              FROM trainings 
              WHERE %(datetime_now)s < end_datetime 
              ORDER BY start_datetime;
              """
        data = {'datetime_now' : datetime_now}
        return self.query(sql, data)

    def find_user(self, user_id):
        sql = """
              SELECT *
              FROM users
              WHERE user_id = %(user_id)s
              LIMIT 1;
              """
        data = {'user_id': user_id}
        return self.query(sql, data)

    def update_user_info(self, user_id, user_name, name):
        sql = """
              UPDATE users
              SET user_name = %(user_name)s, name = %(name)s
              WHERE user_id = %(user_id)s;
              """
        data = {'user_name': user_name,
                'user_id': user_id,
                'name': name}
        self.mutate(sql, data)

    def set_user_access(self, user_id, is_admin):
        sql = """
              UPDATE users
              SET admin = %(admin)s
              WHERE user_id = %(user_id)s;
              """
        admin = 1 if is_admin else 0
        args = {'admin': admin,
                'user_id': user_id}
        self.mutate(sql, data)

    def add_user(self, user_id, user_name, name):
        sql = """
              INSERT INTO users (user_id, user_name, name, admin)
              VALUES (%(user_id)s, %(user_name)s, %(name)s, %(admin)s);
              """
        data = {'user_id': user_id,
                'user_name': user_name,
                'name': name,
                'admin': admin}
        self.mutate(sql, data)

    def add_or_update_user(self, user_id, user_name, name):
        if len(self.find_user(user_id)) == 0:
            self.add_user(user_id, user_name, name)
        else:
            self.update_user_info(user_id, user_name, name)

    def find_attendance(self, training_id, user_id):
        sql = """
              SELECT *
              FROM attendances
              WHERE training_id = %(training_id)s AND user_id = %(user_id)s
              LIMIT 1
              """
        data = {'training_id': training_id,
                'user_id': user_id}
        return self.query(sql, data)

    def get_attendances(self, training_id):
        sql = """
              SELECT *
              FROM attendances
              WHERE training_id = %(training_id)s
              ORDER BY coming
              """
        data = {'training_id': training_id}
        return self.query(sql, data)

    def get_no_reply_user_ids(self, training_id):
        sql = """
              SELECT user_id
              FROM users
              EXCEPT
              SELECT user_id
              FROM attendances
              WHERE training_id = %(training_id)s
              """
        data = {'training_id': training_id}
        return self.query(sql, data)

    def add_attendance(self, training_id, user_id, coming):
        sql = """
              INSERT INTO attendances (training_id, user_id, coming)
              VALUES (%(training_id)s, %(user_id)s, %(coming)s)
              """
        data = {'training_id': training_id,
                'user_id': user_id,
                'coming': coming}
        self.mutate(sql, data)

    def update_attendance(self, training_id, user_id, coming):
        sql = """
              UPDATE attendances
              SET coming = %(coming)s
              WHERE training_id = %(training_id)s AND user_id = %(user_id)s
              """
        data = {'training_id': training_id,
                'user_id': user_id,
                'coming': coming}
        self.mutate(sql, data)

    def add_or_update_attendance(self, msg):
        can_attend = 1 if msg['data'].startswith('/can_go') else 0
        training_id = msg['data'].split(' ')[1]
        # reason = ' '.join(msg['data'].split(' ')[2:])
        # Handle user
        chat = msg['message']['chat']
        user_id = chat['id']
        user_name = chat['username'] if 'username' in chat else ''
        name = chat['first_name'] if 'first_name' in chat else ''
        self.add_or_update_user(user_id, user_name, name)
        # Handle attendance
        if len(self.find_attendance(training_id, user_id)) == 0:
            self.add_attendance(training_id, user_id, can_attend)
        else:
            self.update_attendance(training_id, user_id, can_attend)

db = Cheerbot_DB()
db.setup()
print(db.get_table_size('training'))
