# Project 1

Web Programming with Python and JavaScript

First, set up DATABASE
1. books table was created by following sql code:
CREATE TABLE books(
  id serial NOT NULL,
  isbn varchar UNIQUE NOT NULL,
  title varchar NOT NULL,
  author varchar NOT NULL,
  year integer NOT NULL,
  review varchar NULL,
  rating integer NULL
  )

books.csv was imported to books table by import.py

2. users table was created by following sql code:
CREATE TABLE users(
  id serial NOT NULL,
  name varchar NOT NULL,
  username varchar NOT NULL,
  password varchar NOT NULL
  )
Second, register, login, logout, booksearch, book information and json query

1. In register function, username is unique, and password has to be confirmed by inputing twice. The password
will be encoded by SALT
2. In login page, when locate the user information by username, the password provided by user will be translated
into hashcode by applying the SALT variable. If password matches, the login will be successful and a session will
be created.
3. In booksearch app, part of isbn, title or author will be accepted. It will come back a list of url with the books
satisfied to the search input.
4. In book bage, book information will be displayed. Also a place will be provided to take comments and rating form
users. The comments and rating made by users will be shown in the page as well. Also, average_rating and review_counts from Goodreads API are also displayed.
5. In api access app, the book information including title, author, year, isbn, review_count and average_score are jsonified and provided upon url request with isbn  
