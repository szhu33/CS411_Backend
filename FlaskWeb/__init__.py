from flask import Flask, request, session, render_template, flash
from dbconnect import connection
from passlib.hash import sha256_crypt
import gc
from flask import jsonify
from pymysql import escape_string as thwart # escape SQL injection(security vulnerability )

from wtforms import Form, BooleanField, TextField, PasswordField, validators

postNum = 0

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
    #postNum = 0
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
  
    return render_template('index.html', value='pig', movies_instance=movies)

@app.route('/movie/<myImdbId>', methods = ["GET"])
def movieDetailPage(myImdbId):
    print("===in movie detail page")
    print("ImdbId", myImdbId)
    c, conn = connection()
    sql = "SELECT * FROM Movie WHERE ImbdId = %s"
    x = c.execute(sql, myImdbId)
    print("number of affected rows",x)
    movie = c.fetchall()
    printQueryResult(movie)
    return render_template('movie_detail.html', movie=movie)

@app.route('/post', methods = ["GET", "POST"])
def postPage():
    global postNum
    print("===in post page")
    try:
        form = RegistrationForm(request.form)
        if request.method == "POST":
            postNum += 1
            movie = request.form['movie']
            review = request.form['review']
            rating = request.form['rating']
            c, conn = connection()
            print("movie", movie, "review", "fill", "rating", "fill")
            x = c.execute("SELECT * FROM Movie WHERE title = %s", movie)
            ImbdId = c.fetchall()[0][0]
            print("movie imbdId", ImbdId)
            print(postNum, review, rating, ImbdId)
            x = c.execute("INSERT INTO Post(postId, review, rating, ImbdId, movieTitle) VALUES (%s, %s, %s, %s, %s)", (postNum, review, rating, ImbdId, movie))
            print(x)
            conn.commit()
            print("number of affected rows",x)
			
    except Exception as e:
        return str(e)
    print("after submitting")
    c, conn = connection()
    x = c.execute("SELECT * FROM Post")
    post = c.fetchall()
    printQueryResult(post)
    
    return render_template('post.html', form=form, posts=post)

@app.route('/register/',methods = ["GET","POST"])
def loginPage():
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
