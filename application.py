import os
import hashlib
import requests

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
SALT = "54motisdesdfsdfs"

@app.route("/")
def index():
    return render_template("index.html")
#Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        #Check if username already exists
        if db.execute("SELECT * FROM users WHERE username=:username", {"username":username}):
            return render_template("error.html", message="Username existed!")
        password = request.form.get("password")
        confirmed = request.form.get("confirmed")
        #Check if password input match
        if password == confirmed:
            password += SALT
            password_hashed = hashlib.md5(password.encode()).hexdigest()
            db.execute("INSERT INTO users(name, username, password) VALUES (:name, :username, :password)",
                                          {"name":name, "username": username, "password":password_hashed})
            db.commit()
            return redirect(url_for("login"))
        else:
            return render_template("register.html")
    return render_template("register.html")
#Login
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method =="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        password += SALT
        password_hashed = hashlib.md5(password.encode()).hexdigest()
        password_db = db.execute("SELECT id, password FROM users WHERE username=:username", {"username":username}).fetchone()
        #Login when password hashcode matches the one stored in the database
        if password_db.password == password_hashed:
        # Remember which user has logged in
            session["user_id"] = password_db["id"]
            return redirect(url_for("booksearch"))
        return render_template("register.html")
    return render_template("login.html")

@app.route("/booksearch", methods=["GET", "POST"])
def booksearch():
    if request.method =="POST":
        val=request.form.get("inputvalue")
        val= '%'+val+'%'
        searchresult=db.execute("SELECT isbn, title, author FROM books WHERE (isbn LIKE :val OR LOWER(title) LIKE LOWer(:val) OR LOWER(author) LIKE LOWER(:val))", {"val":val}).fetchall()
        if searchresult ==[]:
            return render_template("error.html", message="No books found!")
        return render_template("books.html", books=searchresult)
    return render_template("booksearch.html")

@app.route("/booksearch/<string:book_isbn>", methods=["GET", "POST"])
def book(book_isbn):
    if request.method=="POST":
        review_in=request.form.get("comments")
        rating= request.form.get("rating")
        if rating is not "":
            rating=int(rating)
        #Pull out the comments already made and not allow to have second comment
        comm=db.execute("SELECT review FROM books WHERE isbn=:isbn", {"isbn":book_isbn}).fetchone()
        if comm[0] is not None:
            return render_template("error.html", message="Has Commented")
        #Insert review and rating
        db.execute("UPDATE books SET review = :review WHERE isbn=:isbn", {"review":review_in, "isbn":book_isbn})
        if (rating >=1 and rating <=5):
            db.execute("UPDATE books SET rating = :rating WHERE isbn=:isbn", {"rating":rating, "isbn":book_isbn})
        else:
            return render_template("error.html", message="Rating out of range!")
        db.commit()
    #Obtain the updated book
    book= db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn":book_isbn}).fetchone()
    #Request review information from goodreads
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "57bUGMI4AKgFlr7vdts2w", "isbns": book_isbn})
    if res.status_code==200:
        review_count=res.json()["books"][0]["reviews_count"]
        review_rating=res.json()["books"][0]["average_rating"]
    review_count=None
    review_rating=None
    return render_template("book.html", book=book, review_count=review_count, review_rating=review_rating)

@app.route("/api/books/<string:book_isbn>")
def book_api(book_isbn):
    #Query the book information using isbn
    book0=db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn":book_isbn}).fetchone()
    #Collect all the isbn from books and check if the input isbn is in the list or not
    isbn0 = db.execute("SELECT isbn FROM books").fetchall()
    lis_new=[]
    for lis in isbn0:
        lis_new.append(lis[0])
    if book_isbn not in lis_new:
        return jsonify({"error": "Invalid Isbn"}), 422
    #Only one review was input to the book, thus the reviewcount will be either 1 or 0
    if book0.review==None:
        reviewcount=0
    reviewcount=1
    #Jsonify the book information
    return jsonify({
            "title": book0.title,
            "author":book0.author,
            "year":str(book0.year),
            "isbn":book_isbn,
            "review_count": reviewcount,
            "average_score": book0.rating
    })

@app.route('/logout')
def logout():
    # Clear any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")
