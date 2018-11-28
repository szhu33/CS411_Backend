from flask import Flask, request, session, render_template, flash
from dbconnect import connection
from passlib.hash import sha256_crypt
import gc
import os.path
from pathlib import Path
from flask import jsonify, redirect, url_for
from pymysql import escape_string as thwart # escape SQL injection(security vulnerability )

from wtforms import Form, BooleanField, TextField, PasswordField, validators

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

@app.route('/')
def homepage():
    print("===in movie page")
    c, conn = connection()
    x = c.execute("SELECT * FROM Movie LIMIT 20")
    print("number of affected rows",x)
    movies = c.fetchall()
    printQueryResult(movies)
    movies =  [[str(y) for y in x] for x in movies]

    global postNum
    if os.path.exists("./post_count.txt"):
        f=open("post_count.txt", "r+")
        content = f.read()
        print("postNum:", content)
        if content == "":
            postNum = 0
        else:
            postNum = int(content)
    else:
        f=open("post_count.txt", "w+")
        postNum = 0
    f.close()

    return render_template('index.html', value='pig', movies_instance=movies)

@app.route('/search/<keyword>', methods = ["GET"])
def moviepage(keyword):

    print("===in movie page")
    c, conn = connection()
    x = c.execute("SELECT * FROM Movie LIMIT 20")
    print("number of affected rows",x)
    movies = c.fetchall()
    for x in movies:
        print(x)
    movies =  [[str(y) for y in x] for x in movies]

    return render_template('index.html', value='pig', movies_instance=movies)


@app.route('/movie/<myImdbId>', methods = ["GET", "POST"])
def movieDetailPage(myImdbId):
    print("===in movie detail page")
    print("ImdbId", myImdbId)
    global postNum
    print("postNum", postNum)
    print("session_username", session_username)

    try:
        form = RegistrationForm(request.form)
        if request.method == "POST":
            print("Pressed postButton")
            postNum += 1
            movie = request.form['movie']
            review = request.form['review']
            rating = request.form['rating']
            c, conn = connection()
            print(postNum, review, rating, myImdbId)
            x = c.execute("INSERT INTO Post(postId, review, rating, ImdbId, movieTitle, Username) VALUES (%s, %s, %s, %s, %s, %s)", (postNum, review, rating, myImdbId, movie, session_username))
            conn.commit()
            if int(x)>0:
                print("write", str(postNum))
                f=open("post_count.txt", "w+")
                f.seek(0)
                f.truncate()
                f.write(str(postNum))
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
            print(postNum, review, rating, ImdbId)
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
    print("===in post page")
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

@app.route('/user/<Username>', methods = ["GET", "POST"])
def userProfilePage(username):
    c, conn = connection()
    x = c.execute("SELECT * FROM Users WHERE Username = %s", username)
    print("number of affected rows",x)
    result = c.fetchall()
    printQueryResult(user)
    user = result[0]
    email = user[1]

    x = c.execute("SELECT * FROM Users WHERE Username = %s", username)
	



@app.route('/register/',methods = ["GET","POST"])
def loginPage():
    print("===in login page")
    global session_username
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
                session_username = username

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
