from flask_app import app
from flask import render_template, request, redirect, session, flash, jsonify, request, url_for
from flask_bcrypt import Bcrypt
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pprint
from functools import wraps
from flask_app.models.user_model import User
from flask_app.models.review_model import Review
import flask_app.constants

# Initialize Bcrypt object
bcrypt = Bcrypt(app) 

# ==== Spotify API ====
CLIENT_ID = flask_app.constants.CLIENT_ID
CLIENT_SECRET = flask_app.constants.CLIENT_SECRET
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# ==== Landing Page ====
@app.route('/') 
def index():
    return render_template('landing_page.html')

# ==== Register ====
@app.route('/register')
def register_form():
    session['page'] = 'register'
    return render_template('register_form.html')

@app.route('/users/register', methods=['POST']) 
def register():
    if not User.validate(request.form): # Validate form data
        return redirect('/register')
    hashed_password = bcrypt.generate_password_hash(request.form['password']) # Hash password
    data = {
        **request.form,
        'password': hashed_password
    }
    id = User.create(data) # Add user to database
    session['user_id'] = id # Initialize session
    return redirect('/dashboard') # Redirect to dashboard

@app.route('/login') # ROUTE: login form
def login_form():
    if 'user_id' in session: # Check if user is logged in
        return redirect('/dashboard')
    session['page'] = 'login'
    return render_template('login_form.html')

@app.route('/users/login', methods=['POST']) # ROUTE: login user
def login():
    user_in_db = User.get_one_by_email({'email': request.form['email']}) # Validate email
    if not user_in_db:
        flash('Invalid login info', "log")
        return redirect('/login')
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']): # Validate password
        flash("Invalid login info", "log")
        return redirect('/login')
    session['user_id'] = user_in_db.id # Initialize session
    return redirect('/dashboard') # Redirect: Dashboard

@app.route('/users/logout') # ROUTE: logout user
def logout():
    session.clear() # Clear session
    return redirect('/login') # Redirect to register/login page

# ==== Dashboard ====
@app.route('/dashboard') # ROUTE: dashboard
@login_required
def dashboard():
    logged_user = User.get_one_by_id({'id': session['user_id']}) # Get user's data
    logged_user_reviews = Review.get_all_by_user_id({'user_id': session['user_id']}) # Get user's reviews
    for review in logged_user_reviews:
        album_results = sp.album(review.album_id) # Get album data for each review
        album_data = {
            "album_id": album_results['id'],
            "album_name": album_results['name'],
            "album_artist": album_results['artists'][0]['name'],
        }
        review.album_data = album_data
    return render_template('dashboard.html', logged_user = logged_user, logged_user_reviews = logged_user_reviews)

# ==== Music Tab ====
@app.route('/users/music/search_form') # ROUTE: search music engine
@login_required
def search_music_form(all_albums=[]):
    return render_template('music_search.html') 

@app.route('/users/music/search', methods=['POST']) # ROUTE: search for music
def search_music():
    album_name = request.form['album_name']
    search_results = sp.search(album_name, limit=4, offset=0, type='album', market=None)
    album_results = search_results['albums']['items']
    all_albums = []
    for album in album_results:
        one_album = {
            'album_id': album['id'],  
            'album_name': album['name'],
            'album_artist': album['artists'][0]['name']
        }
        all_albums.append(one_album)
    return jsonify(all_albums)

@app.route('/users/music/view/<album_id>') # ROUTE: view album info 
def view_music(album_id):
    album_results = sp.album(album_id)
    album_tracks_results = sp.album_tracks(album_id)
    album_tracks = []
    for item in album_tracks_results['items']:
        album_tracks.append(item['name'])
    album_data = {
        "album_id": album_results['id'],
        "album_name": album_results['name'],
        "album_artist": album_results['artists'][0]['name'],
        "album_img": album_results['images'][0]['url'],
        "album_tracks": album_tracks
    }

    return render_template('music_view.html', album_data = album_data)

# ==== Users Tab ====
@app.route('/users/user_search') # ROUTE: search users page
@login_required
def search_users():
    return render_template('user_search.html')

@app.route('/users/user_view') # ROUTE: view user's profile
def view_user():
    return render_template('user_view.html')