from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, HiddenField
from wtforms.validators import InputRequired, length, DataRequired


class UserForm(FlaskForm):
    first_name = StringField(label='first name', validators=[InputRequired()])
    last_name = StringField(label='last name', validators=[InputRequired()])
    team = SelectField(label='team', choices=[('none', 'none'),
                                              ('blue', 'blue'), ('red', 'red'), ('yellow', 'yellow')])
    email = StringField(label='email', validators=[
                        InputRequired(), length(max=50)])
    username = StringField(label='username', validators=[InputRequired()])
    password = PasswordField(label='password', validators=[InputRequired()])


class LoginForm(FlaskForm):
    username = StringField(label='username', validators=[InputRequired()])
    password = PasswordField(label='password', validators=[InputRequired()])


class CreateTeamForm(FlaskForm):
    name = StringField('Team Name', validators=[InputRequired()])


class AssembleTeamForm(FlaskForm):
    """Form for adding a song to playlist."""
    team_id = SelectField('add to a team', coerce=int)
