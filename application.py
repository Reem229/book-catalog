from flask import (Flask, render_template,
                   request, redirect,
                   jsonify, url_for,
                   flash)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, BookCatalog, Book
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
app.secret_key = "super secret key"

# Load Client ID from JSON file.
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Book Catalog Application"

# Connect to DB.
engine = create_engine('sqlite:///bookscatalog.db?check_same_thread=False')
Base.metadata.bind = engine

# Create DB session.
DBSession = sessionmaker(bind=engine)
session = DBSession()
# ------------------------------
# Home Page.
# ------------------------------


@app.route('/')
@app.route('/book_catalog')
def book_catalog():
    # TODO: i need to add information about last books in HTML file.
    book_catalog = session.query(BookCatalog).order_by(asc(BookCatalog.name))
    return render_template('bookcatalog.html', book_catalog=book_catalog)

# ------------------------------
# CRUD methods.
# ------------------------------
# ------------------------------READ
# Route of the list of books.


@app.route('/book_catalog/<int:bookcatalog_id>/')
@app.route('/book_catalog/<int:bookcatalog_id>/list')
def books_list(bookcatalog_id):
    bookcatalog = session.query(BookCatalog).filter_by(id=bookcatalog_id).one()
    creator = getUserInfo(bookcatalog.user_id)
    books = session.query(Book).filter_by(bookcatalog_id=bookcatalog_id).all()
    if 'username' not in login_session:
        return render_template(
            'publiclist.html',
            bookcatalog=bookcatalog,
            books=books,
            creator=creator)
    else:
        return render_template(
            'list.html',
            bookcatalog=bookcatalog,
            books=books,
            creator=creator)

# #Route to show the book.


@app.route('/book_catalog/<int:bookcatalog_id>/list/<int:book_id>')
def book(bookcatalog_id, book_id):
    bookcatalog = session.query(BookCatalog).filter_by(id=bookcatalog_id).one()
    books = session.query(Book).filter_by(
        bookcatalog_id=bookcatalog_id, id=book_id).one()
    return render_template('book.html', books=books)

# ------------------------------CREATE
# Route to add new book.


@app.route('/book_catalog/<int:bookcatalog_id>/add', methods=['GET', 'POST'])
@app.route(
    '/book_catalog/<int:bookcatalog_id>/list/add',
    methods=[
        'GET',
        'POST'])
def add_book(bookcatalog_id):
    if 'username' not in login_session:
        return redirect('/login')
    bookcatalog = session.query(BookCatalog).filter_by(id=bookcatalog_id).one()
    if request.method == 'POST':
        newBook = Book(
            name=request.form['name'],
            user_id=login_session['user_id'],
            author=request.form['author'],
            description=request.form['description'],
            bookcatalog_id=bookcatalog.id,
            pages=request.form['pages'],
            picture=request.form['picture'])
        session.add(newBook)
        flash('New Book %s Successfully Created' % newBook.name)
        session.commit()
        return redirect(url_for('books_list', bookcatalog_id=bookcatalog_id))
    else:
        return render_template('newbook.html', bookcatalog_id=bookcatalog_id)

# ------------------------------UPDATE
# Route to edit any information of book.


@app.route(
    '/book_catalog/<int:bookcatalog_id>/list/<int:book_id>/edit',
    methods=[
        'GET',
        'POST'])
def edit_book(bookcatalog_id, book_id):
    if 'username' not in login_session:
        return redirect('/login')
    bookcatalog = session.query(BookCatalog).filter_by(id=bookcatalog_id).one()
    edited_book = session.query(Book).filter_by(id=book_id).one()
    if login_session['user_id'] != edited_book.user_id:
        return "<script>function myFunction() {alert('You are" \
               " not authorized to edit this book. Please create " \
               "your own Books in order to edit it.');}</script><body" \
               " onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            edited_book.name = request.form['name']
        if request.form['author']:
            edited_book.author = request.form['author']
        if request.form['pages']:
            edited_book.pages = request.form['pages']
        if request.form['picture']:
            edited_book.picture = request.form['picture']
        if request.form['description']:
            edited_book.description = request.form['description']
        session.add(edited_book)
        session.commit()
        flash('Book Successfully Edited')
        return redirect(url_for('books_list', bookcatalog_id=bookcatalog_id))
    else:
        return render_template(
            'editbook.html',
            bookcatalog_id=bookcatalog_id,
            book_id=book_id,
            book=edited_book)

# ------------------------------DELETE
# Route to delete any book.


@app.route(
    '/book_catalog/<int:bookcatalog_id>/list/<int:book_id>/delete',
    methods=[
        'GET',
        'POST'])
def delete_book(bookcatalog_id, book_id):
    if 'username' not in login_session:
        return redirect('/login')
    bookcatalog = session.query(BookCatalog).filter_by(id=bookcatalog_id).one()
    book_to_delete = session.query(Book).filter_by(id=book_id).one()
    if login_session['user_id'] != book_to_delete.user_id:
        return "<script>function myFunction() {alert('You are " \
               "not authorized to delete this Book. Please create " \
               "your own Books in order to delete it.');}</script>" \
               "<body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(book_to_delete)
        session.commit()
        flash('Book Successfully Deleted')
        return redirect(url_for('books_list', bookcatalog_id=bookcatalog_id))
    else:
        return render_template('deletebook.html', book=book_to_delete)


# ------------------------------
# JSON methods.
# ------------------------------
@app.route('/book_catalog/json')
def bookcatalogJSON():
    bookcatalogs = session.query(BookCatalog).all()
    return jsonify(bookcatalogs=[r.serialize for r in bookcatalogs])


@app.route('/book_catalog/<int:bookcatalog_id>/list/json')
def bookcatalogofbookJSON(bookcatalog_id):
    bookcatalog = session.query(BookCatalog).filter_by(id=bookcatalog_id).one()
    books = session.query(Book).filter_by(bookcatalog_id=bookcatalog_id).all()
    return jsonify(books=[b.serialize for b in books])


@app.route('/book_catalog/<int:bookcatalog_id>/list/<int:book_id>/json')
def bookJSON(bookcatalog_id, book_id):
    bookcatalog = session.query(BookCatalog).filter_by(id=bookcatalog_id).one()
    books = session.query(Book).filter_by(id=book_id).one()
    return jsonify(books=books.serialize)


# ------------------------------
# Login
# ------------------------------
# ------------------------------Login page
# Create anti-forgery state token.
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# ------------------------------ gconnect method


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;' \
              'border-radius: 150px;-webkit-border-radius: 150px;' \
              '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# ------------------------------ disconnect method
# Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        # Reset the user's session.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response


# ------------------------------
# User Helper methods.
# ------------------------------
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


# ------------------------------
# main
# ------------------------------
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
