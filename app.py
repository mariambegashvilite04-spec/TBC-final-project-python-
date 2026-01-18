from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os

app = Flask(__name__)
app.secret_key = 'vivamovie-secret'
DB = 'database.db'
UPLOAD_FOLDER = 'static/uploads'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    return sqlite3.connect(DB)

with get_db() as con:
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS movies (
        movie_name TEXT,
        release_year INTEGER,
        img TEXT
    )''')

    # admin
    cur.execute("INSERT OR IGNORE INTO users VALUES (1,'admin',?)",
        (generate_password_hash('123'),))

    # editor
    cur.execute("INSERT OR IGNORE INTO users VALUES (2,'editor',?)",
        (generate_password_hash('012'),))

    con.commit()

# ---------- ROUTES ----------
@app.route('/')
def index():
    return redirect(url_for('movies'))

@app.route('/movies')
def movies():
    q = request.args.get('q')
    con = get_db()
    if q:
        movies = con.execute("SELECT rowid,* FROM movies WHERE movie_name LIKE ?",('%'+q+'%',)).fetchall()
    else:
        movies = con.execute('SELECT rowid,* FROM movies').fetchall()
    return render_template('movies.html', movies=movies)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pw = generate_password_hash(request.form['password'])
        try:
            con = get_db()
            con.execute('INSERT INTO users(username,password) VALUES (?,?)',(user,pw))
            con.commit()
            return redirect('/login')
        except:
            pass
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        con = get_db()
        data = con.execute('SELECT * FROM users WHERE username=?',(user,)).fetchone()
        if data and check_password_hash(data[2], pw):
            session['user'] = data[1]
            session['id'] = data[0]
            return redirect('/movies')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/movies')

@app.route('/delete/<int:id>')
def delete(id):
    if session.get('id') == 1:
        con = get_db()
        con.execute('DELETE FROM movies WHERE rowid=?',(id,))
        con.commit()
    return redirect('/movies')

@app.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    name = request.form['name']
    year = request.form['year']
    con = get_db()
    con.execute('UPDATE movies SET movie_name=?, release_year=? WHERE rowid=?',(name,year,id))
    con.commit()
    return redirect('/movies')

if __name__ == '__main__':
    app.run(debug=True)
