from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)


class User(db.Model):
    """Site user."""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    team = db.Column(db.String, nullable=True)
    user_teams = db.relationship("Team", backref="owner",
                                 cascade="all, delete-orphan")

    @classmethod
    def register(cls, username, pwd, email, first_name, last_name, team):
        '''register user with hashed password and return user'''
        hashed = bcrypt.generate_password_hash(pwd)
        hashed_utf8 = hashed.decode('utf8')
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name, team=team)

    @classmethod
    def authenticate(cls, username, pwd):
        '''validate that user exists and pwd is correct
        return user if valid; else return false
        '''
        u = User.query.filter_by(username=username).first()
        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False

    def greet(self):
        '''greet using name'''
        return f"Hi, {self.username}"


class Pokemon(db.Model):
    """pokemon."""
    __tablename__ = "pokemon"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sprite = db.Column(db.String, nullable=False)
    name = db.Column(db.Text, nullable=False)
    poke_id = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey(
        'teams.id'), nullable=True)
    poke_team = db.relationship('Team', backref='team_pokemon')


class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    username = db.Column(db.String(20), db.ForeignKey(
        'users.username'), nullable=False)

    users = db.relationship(
        'User',
        backref="teams",
    )
