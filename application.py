from flask import Flask
from config import BaseConfig
from flask import request, render_template, jsonify, url_for, redirect, g, Blueprint
from sqlalchemy.exc import IntegrityError
from utils.auth import generate_token, requires_auth, verify_token

app = Flask(__name__)
app.config.from_object(BaseConfig)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/<path:path>', methods=['GET'])
def any_root_path(path):
    return render_template('index.html')

@app.route("/api/user", methods=["GET"])
@requires_auth
def get_user():
    return jsonify(result=g.current_user,
                    tasks=Task.get_latest_tasks())


@app.route("/api/create_user", methods=["POST"])
def create_user():
    incoming = request.get_json()
    
    try:
        User.create_user(incoming)
    except IntegrityError:
        return jsonify(message="User with that email already exists"), 409

    new_user = User.query.filter_by(email=incoming["email"]).first()

    return jsonify(
        id=new_user.id,
        token=generate_token(new_user)
    )


@app.route("/api/get_token", methods=["POST"])
def get_token():
    incoming = request.get_json()
    user = User.get_user_with_email_and_password(incoming["email"], incoming["password"])
    if user:
        return jsonify(token=generate_token(user))

    return jsonify(error=True), 403


@app.route("/api/is_token_valid", methods=["POST"])
def is_token_valid():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        return jsonify(token_is_valid=True)
    else:
        return jsonify(token_is_valid=False), 403


@app.route("/api/submit_task", methods=["POST"])
def submit_task():
    incoming = request.get_json()

    try:
        Task.add_task(incoming)
    except IntegrityError:
        return jsonify(message="Error submitting task"), 409

    return jsonify(success=True)


@app.route("/api/get_tasks_for_user", methods=["POST"])
def get_tasks_for_user():
    incoming = request.get_json()

    return jsonify(
        tasks=[i.serialize for i in Task.get_tasks_for_user(incoming["user_id"]).all()]
    )


# from application import app
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


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
    def create_user(payload):
        user = User(
            email=payload["email"],
            password=payload["password"],
            first_name=payload["first_name"],
            last_name=payload["last_name"],
        )
        db.session.add(user)

        # try:
        db.session.commit()
        # except IntegrityError:
        #     return jsonify(message="User with that email already exists"), 409

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
    def add_task(incoming):
        task = Task(
            task=incoming["task"],
            user_id=incoming["user_id"],
            status=incoming["status"]
        )
        db.session.add(task)

        # try:
        db.session.commit()
        # except IntegrityError:
        #     return jsonify(message="Error submitting task"), 409
    
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

# if __name__ == "__main__":
#     app.run(host='0.0.0.0')

#GUNICORN_CMD_ARGS="--bind=0.0.0.0:5000 --timeout 600" gunicorn application:app