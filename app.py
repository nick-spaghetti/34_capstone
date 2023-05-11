import os
import requests
from flask import Flask, request, jsonify, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Pokemon, Team
from forms import UserForm, LoginForm, CreateTeamForm, AssembleTeamForm
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from random import randint

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    'DATABASE_URL', "postgres://neek:1OMeHLjyIj9eHcCVOIRguJFxzm5ZlrHg@dpg-chdedb2k728nnn68v7rg-a/pokemanz")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)
base = 'https://pokeapi.co/api/v2/'


connect_db(app)


@app.route('/')
def root():
    if 'user_id' not in session:
        flash('please login first', 'error')
        return redirect('/login')
    else:
        return redirect('/homepage')


@app.route('/homepage')
def homepage():
    user_id = session.get('user_id')
    if user_id is None:
        flash('Please login first', 'warning')
        return redirect('/login')
    else:
        user = User.query.get_or_404(user_id)
        color = session.get('color', 'default')
        teams = Team.query.all()
        return render_template('homepage.html', user=user, color=color, teams=teams, title='search for your favorite pokemon')


# auth routes


@app.route('/register', methods=['get', 'post'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        team = form.team.data
        username = form.username.data
        password = form.password.data
        email = form.email.data
        new_user = User.register(
            first_name, last_name, username, password, email, team)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('username taken')
            return render_template('users/user_form.html', form=form, title='register user')
        session['user_id'] = new_user.id
        return redirect('/homepage')
    else:
        return render_template('users/user_form.html', form=form, title='register user')


@app.route('/login', methods=['get', 'post'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            flash(f'welcome back {user.username}', 'success')
            session['user_id'] = user.id
            return redirect('/homepage')
        else:
            form.username.errors = ['invalid username or password']
    else:
        return render_template('users/user_login.html', form=form, title='login user')


@app.route("/logout")
def logout():
    """Logs user out and redirects to homepage."""
    session.pop("user_id")
    flash('goodbye', 'success')
    return redirect("/login")


# user routes


@app.route("/users/<int:user_id>")
def find_user(user_id):
    '''show details about a single pet'''
    user = User.query.get_or_404(user_id)
    return render_template('/users/user_details.html', user=user, title='user details')


@app.route('/users/<int:user_id>/edit', methods=['get', 'post'])
def users_edit_form(user_id):
    """Show a form to edit an existing user"""
    if 'user_id' not in session:
        flash('please login first', 'error')
        return redirect('/login')
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():

        user.username = form.username.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.team = form.team.data

        db.session.commit()
        flash('user info updated', 'success')
        return redirect("/homepage")

    else:
        return render_template('/users/user_form.html', user=user, form=form, title='edit user form')


@app.route('/users/<int:user_id>/delete', methods=["post"])
def delete_user(user_id):
    """Handle form submission for deleting an existing user"""
    user = User.query.get_or_404(user_id)
    if user.id == session['user_id']:
        db.session.delete(user)
        db.session.commit()
        session.pop('user_id', None)
        flash('user deleted', 'info')
        return redirect('/')
    else:
        flash('do not have required permissions', 'error')
        return redirect('/')


# pokemon routes


@app.route('/word-search')
def poke_search():
    user = User.query.get_or_404(session['user_id'])
    word = request.args["word"].lower()
    # Get the team ID from the query string
    # Pass the team ID to the get_details() function
    data = get_details(word)
    return render_template('/poke_pages/poke_details.html', word=word,  data=data, user=user, title=f'its: {word}')


def get_details(word):
    fields = ['name', 'id', 'types', 'moves', 'stats', 'sprites.front_default']
    params = {'fields': ','.join(fields)}
    res = requests.get(f"{base}/pokemon/{word}", params=params)
    data = res.json()
    return data


@app.route('/random-poke')
def random_poke():
    user = User.query.get_or_404(session['user_id'])
    num = randint(1, 1281)
    data = get_details(num)
    name = data['name']
    return render_template('/poke_pages/poke_details.html', num=num, user=user, data=data, title=f'its: {name}')


def get_details(num):
    res = requests.get(f"{base}/pokemon/{num}")
    data = res.json()
    return data


# team routes


@app.route('/teams/create', methods=['get'])
def create_team():
    user_id = session.get('user_id')
    if user_id is None:
        flash('Please login first', 'warning')
        return redirect('/login')
    user = User.query.get_or_404(user_id)
    form = CreateTeamForm()
    return render_template('/poke_pages/team_form.html', form=form, user=user, title='Create a new team')


@app.route('/teams/create', methods=['get', 'post'])
def create_team_form():
    user_id = session.get('user_id')
    if user_id is None:
        flash('Please login first', 'warning')
        return redirect('/login')
    user = User.query.get_or_404(user_id)
    new_team = Team(name=request.form['name'], username=user.username)
    form = CreateTeamForm()
    if form.validate_on_submit():
        db.session.add(new_team)
        db.session.commit()
        flash('Team created!', 'success')
        return redirect('/homepage')
    return render_template('/poke_pages/team_form.html', form=form, user=user, title='Create a new team')


@app.route("/teams/assemble/<int:poke_id>", methods=["get"])
def set_team(poke_id):
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    form = AssembleTeamForm()
    user_teams = user.user_teams
    form.team_id.choices = [(team.id, team.name)
                            for team in user_teams]
    return render_template("/poke_pages/team_form.html", user=user, form=form, poke_id=poke_id)


@app.route("/teams/assemble/<int:poke_id>", methods=["get", "post"])
def set_team_form(poke_id):
    """Add a pokemon to a team and redirect to team."""
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    data = get_details(poke_id)
    form = AssembleTeamForm()

    # Get the user's teams
    teams = user.user_teams

    # Filter out teams that already have the selected pokemon
    form.team_id.choices = [(team.id, team.name)
                            for team in teams]

    if form.validate_on_submit():
        # Add the pokemon to the selected team
        team = Team.query.get(form.team_id.data)
        pokemon = Pokemon(team_id=form.team_id.data,
                          poke_id=poke_id, name=data['name'], sprite=data['sprites']['front_default'], height=data['height'], weight=data['weight'])
        db.session.add(pokemon)
        db.session.commit()
        flash(f'caught a wild {pokemon.name}!')
        return redirect(f"/teams/{team.id}")
    else:
        return render_template("/poke_pages/poke_details.html", user=user, form=form, data=data, title='its a ')


def get_details(pokemon_id):
    res = requests.get(f"{base}/pokemon/{pokemon_id}")
    data = res.json()
    return data


@app.route("/teams/<int:team_id>", methods=["get"])
def team_details(team_id):
    user = User.query.get_or_404(session['user_id'])
    team = Team.query.get_or_404(team_id)
    pokemon = team.team_pokemon
    return render_template('/poke_pages/team_details.html', team=team, pokemon=pokemon, user=user, title=f'{team.name} details')


@app.route("/teams/<int:team_id>/delete", methods=['post'])
def delete_team(team_id):
    user = User.query.get_or_404(session['user_id'])
    team = Team.query.get_or_404(team_id)
    if user.id == session['user_id']:
        db.session.delete(team)
        db.session.commit()
        flash('team deleted', 'info')
        return redirect('/')
    else:
        flash('do not have required permissions', 'error')
        return redirect('/')


@app.route('/pokemon/<int:id>/delete', methods=['get', 'post'])
def remove_pokemon(id):
    if not session.get('user_id'):
        flash('Please log in first', 'error')
        return redirect('/login')

    pokemon = Pokemon.query.get_or_404(id)
    if pokemon.poke_team.users.id != session['user_id']:
        flash('You do not have the required permissions', 'error')
        return redirect('/')

    db.session.delete(pokemon)
    db.session.commit()
    flash('Pokemon deleted', 'info')
    return redirect(f'/teams/{pokemon.poke_team.id}')
