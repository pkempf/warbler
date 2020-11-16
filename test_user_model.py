"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        users = User.query.all()
        for u in users:
            db.session.delete(u)
        Message.query.delete()
        Follows.query.delete()
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Roll back changes."""

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(email="test@test.com", username="testuser", password="HASHED_PASSWORD")

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """Does __repr__ return what it should?"""

        u = User(email="test@test.com", username="testuser", password="HASHED_PASSWORD")

        db.session.add(u)
        db.session.commit()

        self.assertEqual(repr(u), f"<User #{u.id}: testuser, test@test.com>")

    def test_is_following_true(self):
        """Does is_following return true when a user is indeed following another?"""

        user1 = User(
            email="test@test.com", username="testuser", password="HASHED_PASSWORD"
        )
        user2 = User(
            email="test2@test.com", username="testuser2", password="HASHED_PASSWORD_2"
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        user1.following.append(user2)
        db.session.commit()

        self.assertEqual(user1.is_following(user2), True)

    def test_is_following_false(self):
        """Does is_following return false when a user isn't following another?"""

        user1 = User(
            email="test@test.com", username="testuser", password="HASHED_PASSWORD"
        )
        user2 = User(
            email="test2@test.com", username="testuser2", password="HASHED_PASSWORD_2"
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        self.assertEqual(user1.is_following(user2), False)

    def test_is_followed_by_true(self):
        """Does is_followed_by return true when a user is indeed followed by another?"""

        user1 = User(
            email="test@test.com", username="testuser", password="HASHED_PASSWORD"
        )
        user2 = User(
            email="test2@test.com", username="testuser2", password="HASHED_PASSWORD_2"
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        user2.following.append(user1)
        db.session.commit()

        self.assertEqual(user1.is_followed_by(user2), True)

    def test_is_followed_by_false(self):
        """Does is_followed_by return false when a user isn't followed by another?"""

        user1 = User(
            email="test@test.com", username="testuser", password="HASHED_PASSWORD"
        )
        user2 = User(
            email="test2@test.com", username="testuser2", password="HASHED_PASSWORD_2"
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        self.assertEqual(user1.is_followed_by(user2), False)

    def test_create_invalid_user(self):
        """Does User.create work when invalid credentials are given?"""

        user = User(email="test@test.com", username="testuser")

        integrity_error_thrown = False

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            integrity_error_thrown = True

        self.assertEqual(integrity_error_thrown, True)

    def test_authenticate_valid_credentials(self):
        """Does User.authenticate work when given valid credentials?"""

        # currently gives an "invalid salt" ValueError

        user = User(
            email="test@test.com", username="testuser", password="HASHED_PASSWORD"
        )
        db.session.add(user)
        db.session.commit()

        logged_in_user = User.authenticate(
            username="testuser", password="HASHED_PASSWORD"
        )

        self.assertEqual(user, logged_in_user)

    def test_authenticate_invalid_username(self):
        """Does User.authenticate fail when given a bad username?"""

        user = User(
            email="test@test.com", username="testuser", password="HASHED_PASSWORD"
        )
        db.session.add(user)
        db.session.commit()

        logged_in_user = User.authenticate(
            username="wrong_username", password="HASHED_PASSWORD"
        )

        self.assertFalse(logged_in_user)

    def test_authenticate_invalid_password(self):
        """Does User.authenticate fail when given a bad password?"""

        # currently gives an "invalid salt" ValueError

        user = User(
            email="test@test.com", username="testuser", password="HASHED_PASSWORD"
        )
        db.session.add(user)
        db.session.commit()

        logged_in_user = User.authenticate(
            username="testuser", password="WRONG_PASSWORD"
        )

        self.assertFalse(logged_in_user)