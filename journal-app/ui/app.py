from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure, random key in production

# Define service endpoints based on Docker Compose service names
app.config['AUTH_SERVICE_URL'] = 'http://auth:5001'
app.config['JOURNAL_SERVICE_URL'] = 'http://journal:5002'
app.config['QUOTE_SERVICE_URL'] = 'http://quote:5003'

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# A simple User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = str(id)
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user_data = session.get('user')
    if user_data and str(user_data.get('user_id')) == user_id:
        return User(user_data['user_id'], user_data['username'])
    return None

@app.route('/')
@login_required
def index():
    # Retrieve daily quote from the quote service
    try:
        res = requests.get(f"{app.config['QUOTE_SERVICE_URL']}/api/daily_quote")
        if res.status_code == 200:
            quote = res.json()
        else:
            quote = {'content': 'No quote available', 'author': ''}
    except Exception as e:
        quote = {'content': 'No quote available', 'author': ''}
    
    # Retrieve user journal entries from the journal service
    try:
        res_entries = requests.get(f"{app.config['JOURNAL_SERVICE_URL']}/api/entries", params={'user_id': current_user.id})
        if res_entries.status_code == 200:
            entries = res_entries.json()
        else:
            entries = []
    except Exception as e:
        entries = []
    
    return render_template('index.html', quote=quote, entries=entries)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Call the auth service for registration
        try:
            res = requests.post(f"{app.config['AUTH_SERVICE_URL']}/api/register", json={'username': username, 'password': password})
            if res.status_code == 200:
                flash('Registration successful. Please login.')
                return redirect(url_for('login'))
            else:
                flash(res.json().get('error', 'Registration failed.'))
        except Exception as e:
            flash('Error connecting to authentication service.')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            res = requests.post(f"{app.config['AUTH_SERVICE_URL']}/api/login", json={'username': username, 'password': password})
            if res.status_code == 200:
                data = res.json()
                user = User(data['user_id'], data['username'])
                login_user(user)
                session['user'] = data
                flash('Logged in successfully.')
                return redirect(url_for('index'))
            else:
                flash(res.json().get('error', 'Login failed.'))
        except Exception as e:
            flash('Error connecting to authentication service.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user', None)
    flash('Logged out.')
    return redirect(url_for('login'))

@app.route('/quote_refresh')
@login_required
def quote_refresh():
    try:
        res = requests.get(f"{app.config['QUOTE_SERVICE_URL']}/api/daily_quote?refresh=true")
        if res.status_code == 200:
            flash('Quote refreshed.', 'success')
        else:
            flash('Failed to refresh quote.', 'error')
    except Exception as e:
        flash('Error connecting to quote service.', 'error')
    return redirect(url_for('index'))

@app.route('/quote_json')
@login_required
def quote_json():
    try:
        res = requests.get(f"{app.config['QUOTE_SERVICE_URL']}/api/daily_quote?refresh=true")
        if res.status_code == 200:
            return jsonify(res.json())
        else:
            return jsonify({"error": "Failed to refresh quote."}), 400
    except Exception as e:
        return jsonify({"error": "Error connecting to quote service."}), 500

@app.route('/profile')
@login_required
def profile():
    # Display a simple profile with basic statistics (e.g., count of journal entries)
    try:
        res_entries = requests.get(f"{app.config['JOURNAL_SERVICE_URL']}/api/entries", params={'user_id': current_user.id})
        if res_entries.status_code == 200:
            entries = res_entries.json()
            count = len(entries)
        else:
            count = 0
    except Exception as e:
        count = 0
    return render_template('profile.html', user=current_user, entry_count=count)

@app.route('/journal/new', methods=['GET', 'POST'])
@login_required
def new_entry():
    if request.method == 'POST':
        content = request.form.get('content')
        try:
            res = requests.post(f"{app.config['JOURNAL_SERVICE_URL']}/api/entries", json={'user_id': current_user.id, 'content': content})
            if res.status_code == 200:
                flash('Journal entry added.')
                return redirect(url_for('index'))
            else:
                flash(res.json().get('error', 'Failed to add entry.'))
        except Exception as e:
            flash('Error connecting to journal service.')
    return render_template('journal_form.html', action='New')

@app.route('/journal/edit/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    if request.method == 'POST':
        content = request.form.get('content')
        try:
            res = requests.put(f"{app.config['JOURNAL_SERVICE_URL']}/api/entries/{entry_id}", json={'content': content})
            if res.status_code == 200:
                flash('Entry updated.')
                return redirect(url_for('index'))
            else:
                flash(res.json().get('error', 'Failed to update entry.'))
        except Exception as e:
            flash('Error connecting to journal service.')
    else:
        # To edit, fetch all entries and filter for the one to edit
        try:
            res_entries = requests.get(f"{app.config['JOURNAL_SERVICE_URL']}/api/entries", params={'user_id': current_user.id})
            if res_entries.status_code == 200:
                entries = res_entries.json()
                entry = next((e for e in entries if e['id'] == entry_id), None)
                if not entry:
                    flash('Entry not found.')
                    return redirect(url_for('index'))
            else:
                flash('Failed to fetch entry details.')
                return redirect(url_for('index'))
        except Exception as e:
            flash('Error connecting to journal service.')
            return redirect(url_for('index'))
        return render_template('journal_form.html', action='Edit', entry=entry)
    return render_template('journal_form.html', action='Edit')

@app.route('/journal/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    try:
        res = requests.delete(f"{app.config['JOURNAL_SERVICE_URL']}/api/entries/{entry_id}")
        if res.status_code == 200:
            flash('Entry deleted.')
        else:
            flash(res.json().get('error', 'Failed to delete entry.'))
    except Exception as e:
        flash('Error connecting to journal service.')
    return redirect(url_for('index'))

@app.route('/journal/history')
@login_required
def journal_history():
    try:
        res_entries = requests.get(f"{app.config['JOURNAL_SERVICE_URL']}/api/entries", params={'user_id': current_user.id})
        if res_entries.status_code == 200:
            entries = res_entries.json()
        else:
            entries = []
    except Exception as e:
        entries = []
    return render_template('journal_history.html', entries=entries)

def format_datetime(value):
    try:
        dt = datetime.datetime.fromisoformat(value)
        # Format: abbreviated weekday, abbreviated month, day, year, hour:minute
        return dt.strftime("%a, %b %d, %Y %H:%M")
    except Exception as e:
        return value

app.jinja_env.filters['format_datetime'] = format_datetime

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 