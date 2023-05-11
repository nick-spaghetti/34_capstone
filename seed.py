from models import db, connect_db, User, Team
from app import app
import random
import string

db.drop_all()
db.create_all()

user1 = User.register('user1', 'asdf', 'user1@email.com',
                      'user1', 'user', 'None')
user2 = User.register('user2', 'asdf', 'user2@email.com',
                      'user2', 'user', 'yellow')
user3 = User.register('user3', 'asdf', 'user3@email.com',
                      'user3', 'user', 'red')
user4 = User.register('user4', 'asdf', 'user4@email.com',
                      'user4', 'user', 'yellow')
user5 = User.register('user5', 'asdf', 'user5@email.com',
                      'user5', 'user', 'blue')

db.session.add(user1)
db.session.add(user2)
db.session.add(user3)
db.session.add(user4)
db.session.add(user5)
db.session.commit()


usernames = ['user1', 'user2', 'user3', 'user4', 'user5']
team_names = [f"team{i}" for i in range(1, 11)]

for team_name in team_names:
    team = Team(name=team_name, username=random.choice(usernames))
    db.session.add(team)

db.session.commit()
