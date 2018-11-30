from flask import Flask, request, session, render_template, flash
from dbconnect import connection
from passlib.hash import sha256_crypt
import gc
import os.path
from pathlib import Path
from flask import jsonify, redirect, url_for
from pymysql import escape_string as thwart # escape SQL injection(security vulnerability )
from flask_socketio import SocketIO, emit, join_room
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from datetime import datetime

def printQueryResult(arr):
	for x in arr:
		print(x)

class RegistrationForm(Form):
    username = TextField('Username',[validators.Length(min=4, max=10)])
    email = TextField('Email Address',[validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.Required(), validators.EqualTo('confirm', message="Password must match")])
    confirm = PasswordField('Confirm Password')
    accept_tos = BooleanField('I accept the <a href="/tos"/>Terms of Service</a>.', [validators.Required()])

app = Flask(__name__)
app.secret_key = b'\x9e\x02\xc2<W!A\xf8\xe2\x169:v\x97lC'
socketio = SocketIO(app)

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

@app.route('/chat')
def chatPage():
	return render_template('chat.html', username=session['username'])


@app.route('/', methods = ["GET"])
def homepage():
    print("===in movie page")
    print("current user:", session['username'])
    c, conn = connection()
    x = c.execute("SELECT * FROM Movie LIMIT 20")
    print("number of affected rows",x)
    movies = c.fetchall()
    printQueryResult(movies)
    movies =  [[str(y) for y in x] for x in movies]

    return render_template('index.html', value='pig', movies_instance=movies, myUsername=session['username'])

@app.route('/search', methods = ["GET"])
def searchpage():
    print("===in search page")
    c, conn = connection()
    keyword = request.args.get('keyword')
    searchsql = "SELECT * FROM Movie WHERE title LIKE %s"
    print(searchsql)
    print("%" + keyword + "%")
    x = c.execute(searchsql, ("%" + keyword + "%",))
    print("number of affected rows",x)
    movies = c.fetchall()
    for x in movies:
        print(x)
    movies =  [[str(y) for y in x] for x in movies]
    print(movies)

    return render_template('index.html', value='pig', movies_instance=movies)

@app.route('/movie/<myImdbId>', methods = ["GET", "POST"])
def movieDetailPage(myImdbId):
    print("===in movie detail page")
    print("ImdbId", myImdbId)

    print("session['username']", session['username'])

    try:
        form = RegistrationForm(request.form)
        if request.method == "POST":
            print("Pressed postButton")
            movie = request.form['movie']
            review = request.form['review']
            rating = request.form['rating']
            c, conn = connection()
            print( review, rating, myImdbId)
            x = c.execute("INSERT INTO Post( review, rating, ImdbId, movieTitle, Username) VALUES ( %s, %s, %s, %s, %s)", ( review, rating, myImdbId, movie, session['username']))
            conn.commit()
            if int(x)>0:
                print("INSERT POST SUCCESS")
            print("INSERT: number of affected rows",x)

    except Exception as e:
        return str(e)

    c, conn = connection()
    sql = "SELECT * FROM Movie WHERE ImdbId = %s"
    x = c.execute(sql, myImdbId)
    print("SELECT: number of affected rows",x)
    movie = c.fetchall()
    printQueryResult(movie)

    return render_template('movie_detail.html', movie=movie)

@app.route('/movie_edit/<ImdbId>&<postId>', methods = ["GET", "POST"])
def movieDetailEditPage(ImdbId, postId):
    print("===in movie detail edit page")
    print("postId", postId, "ImdbId",ImdbId)
    try:
        form = RegistrationForm(request.form)
        if request.method == "POST":
            print("Pressed postButton")
            #movie = request.form['movie']
            review = request.form['review']
            rating = request.form['rating']
            c, conn = connection()
            print( review, rating, ImdbId)
            x = c.execute("UPDATE Post SET rating=%s, review=%s WHERE postId=%s", (rating, review, postId))
            conn.commit()
            print("UPDATE: number of affected rows",x)

    except Exception as e:
        return str(e)

    c, conn = connection()
    x = c.execute("SELECT * FROM Movie WHERE ImdbId = %s", ImdbId)
    print("SELECT: number of affected rows",x)
    movie = c.fetchall()
    printQueryResult(movie)

    return render_template('movie_detail_edit.html', movie=movie)

@app.route('/post', methods = ["GET", "POST"])
def postPage():
    print("===In post page")
    try:
        form = RegistrationForm(request.form)
        if request.method == "POST":
            if request.form["submitButton"] == "Delete":
                print("Pressed delete button")
                print("postId", request.form.get("postId"))
                postId = request.form.get("postId")
                c, conn = connection()
                x = c.execute("DELETE FROM Post WHERE postId = %s", postId)
                conn.commit()
                print("DELETE: number of affected rows",x)
            elif request.form["submitButton"] == "Edit":
                print("Pressed Edit button")
                ImdbId = request.form.get("ImdbId")
                print("ImdbId: ", ImdbId)
                c, conn = connection()
                x = c.execute("SELECT * FROM Movie WHERE ImdbId = %s", ImdbId)
                print("SELECT: number of affected rows",x)
                movie = c.fetchall()
                printQueryResult(movie)
                rating = request.form.get("rating")
                postId = request.form.get("postId")
                print("raing", rating)
                return redirect('http://127.0.0.1:5000/movie_edit/{}&{}'.format(ImdbId,postId), code=302)

    except Exception as e:
        return str(e)

    c, conn = connection()
    x = c.execute("SELECT * FROM Post")
    post = c.fetchall()
    printQueryResult(post)

    return render_template('post.html', form=form, posts=post)

@app.route('/user/<username>', methods = ["GET", "POST"])
def userProfilePage(username):
    print("===In User Profile Page")
    print("current user,", session['username'])
    c, conn = connection()
    x = c.execute("SELECT * FROM Users WHERE Username = %s", session['username'])
    user = c.fetchall()[0]
    username = user[0]
    email = user[1]
    print(username, email)

    x = c.execute("SELECT * FROM Post WHERE Username = %s", username)
    print("number of affected rows",x)
    posts = c.fetchall()
    printQueryResult(posts)

    return render_template('user.html', myUsername=username, myEmail=email, myPosts=posts)
    #return redirect('http://127.0.0.1:5000/user/{}'.format(user[0]), code=302)

@app.route('/login/',methods = ["GET","POST"])
def loginPage():
    print("===In login page")
    error = ""
    form = RegistrationForm(request.form) # fill in html with form
    if request.method == "POST":
        username = form.username.data
        #password = sha256_crypt.encrypt(str(form.password.data))
        #print(username, password)
        c, conn = connection()
        x = c.execute("SELECT * FROM Users WHERE Username = (%s)", (thwart(username)))
        if int(x) == 0:
            error = "No such user!"
            print("No such user!")
            return render_template("login.html", form=form, error=error)

        user = c.fetchall()[0]
        if sha256_crypt.verify(form.password.data, user[2]):
            session['logged_in'] = True
            session['username'] = username
            return redirect('http://127.0.0.1:5000/user/{}'.format(username), code=302)

        else:
            error = "Invalid username or password!"
            print("Invalid username or password")

    return render_template("login.html", form=form, error=error)

@app.route('/register/',methods = ["GET","POST"])
def registerPage():
    print("===In register page")
    error = ""
    try:
        form = RegistrationForm(request.form) # fill in html with form
        if request.method == "POST":
            print("request method == post")
            username = form.username.data
            if len(username) < 4:
                error = "Please enter a username more than 3 letters!"
                print("Please enter a username more than 3 letters!")
                return render_template('register.html', form=form, error=error)

            if len(email) < 6:
                error = "Please enter a email more than 6 characters!"
                print("Please enter a email more than 6 characters!")
                return render_template('register.html', form=form, error=error)

            email = form.email.data
            password = sha256_crypt.encrypt(str(form.password.data))
            print(username, email, password)
            c, conn = connection()
            x = c.execute("SELECT * FROM Users WHERE Username = (%s)", (thwart(username)))
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

                return redirect('http://127.0.0.1:5000/user/{}'.format(username), code=302)

    except Exception as e:
        return str(e)

    return render_template("register.html", form=form)


@app.route('/logout',methods = ["GET"])
def logoutPage():

	session['logged_in'] = False
	session['username'] = ""

	return redirect('http://127.0.0.1:5000')

@app.route('/explore',methods = ["GET","POST"])
def explorePage():
    print("===in explore page")
    if (len(request.args) == 0):
	    print("dalse")
	    return render_template("search.html", searched=False)

    yearmin = request.args.get('release_year-min')
    yearmax = request.args.get('release_year-max')
    runtimemin = request.args.get('runtime-min')
    runtimemax = request.args.get('runtime-max')
    ratingmin = request.args.get('user_rating-min')
    ratingmax = request.args.get('user_rating-max')
    genres = request.args.getlist('genres')
    c, conn = connection()
    sql = "SELECT * FROM Movie WHERE releaseYear>=%s AND releaseYear<=%s AND runtime>%s AND runtime<%s AND rating>=%s AND rating<=%s ORDER BY rating ASC LIMIT 20"
    x = c.execute(sql, (yearmin,yearmax,runtimemin,runtimemax,ratingmin,ratingmax))
    movies = c.fetchall()
    print(movies)

    movies =  [[str(y) for y in x] for x in movies]

    return render_template("search.html", searched=True, movies_instance=movies)

if __name__ == "__main__":
    app.run()
