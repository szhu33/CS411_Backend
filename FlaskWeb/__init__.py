from flask import Flask, request, session, render_template, flash
from dbconnect import connection
from passlib.hash import sha256_crypt
import gc
from flask import jsonify
from pymysql import escape_string as thwart # escape SQL injection(security vulnerability )

from wtforms import Form, BooleanField, TextField, PasswordField, validators

class RegistrationForm(Form):
    username = TextField('Username',[validators.Length(min=4, max=10)])
    email = TextField('Email Address',[validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.Required(), validators.EqualTo('confirm', message="Password must match")])
    confirm = PasswordField('Confirm Password')
    accept_tos = BooleanField('I accept the <a href="/tos"/>Terms of Service</a>.', [validators.Required()])

app = Flask(__name__)
app.secret_key = b'\x9e\x02\xc2<W!A\xf8\xe2\x169:v\x97lC'

@app.route('/')
def homepage():
    return "Hi there, how ya doin?"

@app.route('/movie', methods = ["GET"])
def moviepage():
    print("===in movie page")
    c, conn = connection()
    x = c.execute("SELECT * FROM Movie LIMIT 10")
    print("number of affected rows",x)
    movies = c.fetchall()
    for x in movies:
        print(x)
    movies =  [[str(y) for y in x] for x in movies]
    #movies = ['\t'.join(x) for x in movies]
    #movies = '\n'.join(movies)
    #print(type(movies))

    return render_template('index.html', value='pig', movies_instance=movies)

@app.route('/movie/<myImdbId>', methods = ["GET"])
def movieDetailPage():
    print("===in movie detail page")
    print("ImdbId", myImdbId)
    c, conn = connection()
    x = c.execute("SELECT * FROM Movie WHERE ImdbId = myImdbId")
    print("number of affected rows",x)
    movie = c.fetchone()
    print(movie)
    return "movie detail yeah"

@app.route('/tos')
def tospage():
    return "Fake term of service"

@app.route('/register/',methods = ["GET","POST"])
def moviespage():
    print("===in login page")
    try:
        form = RegistrationForm(request.form) # fill in html with form
        if request.method == "POST" and form.validate():

            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt(str(form.password.data))
            print(username, email, password)
            c, conn = connection()
            x = c.execute("SELECT * FROM Users WHERE Username = (%s)", (thwart(username)))
            print(int(x))
            if int(x) > 0:
                flash("The username is already taken, please choose another one.")
                return render_template('register.html', form = form)
            else:
                c.execute("INSERT INTO Users (Username,Email,Password) VALUES (%s, %s, %s)", (thwart(username), thwart(email), thwart(password)))
                conn.commit()

                flash("Thanks for regitering!")
                c.close()
                conn.close()

                gc.collect() #garbage collector

                # set session for this new user
                session['logged_in'] = True
                session['username'] = username

                return "User profile page to be implemented"

    except Exception as e:
        return str(e)

    return render_template("register.html", form=form)

if __name__ == "__main__":
    app.run()
