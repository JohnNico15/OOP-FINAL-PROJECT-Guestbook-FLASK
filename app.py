from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///guestbook.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Guestbook Model
class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guestno = db.Column(db.String(20), unique=True, nullable=False)
    guestname = db.Column(db.String(50), nullable=False)
    company = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    contactno = db.Column(db.String(15), nullable=False)

# User Model for login and register
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Route for Home (Dashboard)
@app.route('/')
def home():
    if 'username' in session:
        guests = Guest.query.all()
        return render_template('home.html', guests=guests)
    return redirect(url_for('login'))

# Route for Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            flash("Login successful!", 'success')
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials!", 'danger')
    return render_template('login.html')

# Route for Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully!", 'info')
    return redirect(url_for('login'))

# Route for Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!", 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Route for Insert Data
@app.route('/add_guest', methods=['GET', 'POST'])
def add_guest():
    if request.method == 'POST':
        guestno = request.form['guestno']
        guestname = request.form['guestname']
        company = request.form['company']
        address = request.form['address']
        contactno = request.form['contactno']
        new_guest = Guest(guestno=guestno, guestname=guestname, company=company, address=address, contactno=contactno)
        db.session.add(new_guest)
        db.session.commit()
        flash("Guest added successfully!", 'success')
        return redirect(url_for('home'))
    return render_template('guestbook.html')

# Route for Delete Data
@app.route('/delete_guest/<int:id>')
def delete_guest(id):
    guest = Guest.query.get_or_404(id)
    db.session.delete(guest)
    db.session.commit()
    flash("Guest deleted successfully!", 'warning')
    return redirect(url_for('home'))

# Route for Search Functionality
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form['search']
        results = Guest.query.filter(Guest.guestname.contains(search_query)).all()
        return render_template('home.html', guests=results)
    return redirect(url_for('home'))

# Route for Reset (Clearing Session or Fields)
@app.route('/reset')
def reset():
    session.clear()
    flash("Session reset!", 'info')
    return redirect(url_for('login'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)