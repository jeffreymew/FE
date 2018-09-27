from index import db, bcrypt
from datetime import datetime, timedelta


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.active = True
        self.password = User.hashed_password(password)

    @staticmethod
    def hashed_password(password):
        return bcrypt.generate_password_hash(password).decode("utf-8")

    @staticmethod
    def get_user_by_id(user_id):
        user = User.query.filter_by(id=user_id).first()
        return user

    @staticmethod
    def get_user_with_email_and_password(email, password):
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return None


class Task(db.Model):
    class STATUS:
        COMPLETED = 'COMPLETED'
        IN_PROGRESS = 'IN_PROGRESS'

    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.DateTime())
    task = db.Column(db.String(255))
    user_id = db.Column(db.String(255))
    status = db.Column(db.String(255))
    
    def __init__(self, task, user_id, status):
        self.date = datetime.utcnow().date()
        self.task = task
        self.user_id = user_id
        self.status = status
    
    @staticmethod
    def get_latest_tasks():
        # import pdb;pdb.set_trace()
        user_to_task = {}

        result = db.engine.execute(
            """SELECT date, task, t.user_id, status from task t 
                INNER JOIN (SELECT user_id, max(date) as MaxDate from task group by user_id) tm 
                on t.user_id = tm.user_id and t.date = tm.MaxDate""")
        for t in result:

        
        # Task.query.join(subq, and_(Task.user_id == subq.user_id, Task.date == subq.date))
        

        # all_tasks = Task.query.filter(Task.date >= datetime.utcnow().date())
        # user_to_task = {}
        # for t in all_tasks:
            if t.user_id in user_to_task:
                user_to_task.get(t.user_id).append(dict(t))
            else:
                user_to_task[t.user_id] = [dict(t)]
       
        return user_to_task

    @staticmethod
    def get_tasks_for_user(user_id):
        return Task.query.filter_by(user_id=user_id)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'date'       : self.date.strftime("%Y-%m-%d"),
           'task'       : self.task,
           'user_id'    : self.user_id,
           'status'     : self.status,
       }
