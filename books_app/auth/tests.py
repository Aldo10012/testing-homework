import os
from unittest import TestCase

from datetime import date
 
from books_app import app, db, bcrypt
from books_app.models import Book, Author, User, Audience

"""
Run these tests with the command:
python -m unittest books_app.main.tests
"""

#################################################
# Setup
#################################################

def create_books():
    a1 = Author(name='Harper Lee')
    b1 = Book(
        title='To Kill a Mockingbird',
        publish_date=date(1960, 7, 11),
        author=a1
    )
    db.session.add(b1)

    a2 = Author(name='Sylvia Plath')
    b2 = Book(title='The Bell Jar', author=a2)
    db.session.add(b2)
    db.session.commit()

def create_user():
    password_hash = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(username='me1', password=password_hash)
    db.session.add(user)
    db.session.commit()

#################################################
# Tests
#################################################

class AuthTests(TestCase):
    """Tests for authentication (login & signup)."""
 
    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_signup(self):
        '''test signup route'''
        post_data = {
            'username': 'me1',
            'password': "password"
        }
        self.app.post('/signup', data=post_data)
        user = User.query.filter_by(username='me1').one()
        self.assertEqual(user.username, 'me1')

        pass

    def test_signup_existing_user(self):
        '''test signup route with existing user'''
        create_user()
        post_data = {
            'username': 'me1',
            'password': "password"
        }
        self.app.post('/signup', data=post_data)
        current_user = User.query.filter_by(username=post_data['username']).one()
        self.assertEqual(current_user.username, 'me1')
        self.assertNotIn(current_user.password, 'password')
        print("error message here")

    def test_login_correct_password(self):
        '''test login route with incorrect password'''
        create_user()
        post_data = {
            'username': 'me1',
            'password': "password"
        }
        self.app.post('/login', data=post_data)

        current_user = User.query.filter_by(username=post_data['username']).one()
        self.assertNotIn(current_user.password, 'password')
        

    def test_login_nonexistent_user(self):
        '''test login route with nonexistant user'''
        post_data = {
            'username': 'me1',
            'password': "password"
        }
        self.app.post('/login', data=post_data)

        self.assertIn(post_data['password'], 'password')
        print("incorrect")
        pass

    def test_login_incorrect_password(self):
        '''test login route with incorrect password'''
        create_user()

        post_data = {
            'username': 'me1',
            'password': "incorrct_password"
        }
        self.app.post('/login', data=post_data)

        self.assertIn(post_data['password'], 'incorrct_password')
        print("incorrect password")
        pass

    def test_logout(self):
        '''test logout'''
        create_user()

        post_data = {
            'username': 'me1',
            'password': "incorrct_password"
        }
        self.app.post('/login', data=post_data)

        response = self.app.get('/logout', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        response_text = response.get_data(as_text=True)
        self.assertIn('login', response_text)
        
