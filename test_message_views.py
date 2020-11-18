"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config["WTF_CSRF_ENABLED"] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(
            username="testuser",
            email="test@test.com",
            password="testuser",
            image_url=None,
        )

        self.user_1 = User.signup("user1", "user1@test1.com", "password", None)
        self.user_2 = User.signup("user2", "user2@test2.com", "password", None)
        self.user_3 = User.signup("user3", "user3@test3.com", "password", None)
        self.user_4 = User.signup("user4", "user4@test4.com", "password", None)

        db.session.commit()

        self.uid_test = self.testuser.id
        self.uid_1 = self.user_1.id
        self.uid_2 = self.user_2.id
        self.uid_3 = self.user_3.id
        self.uid_4 = self.user_4.id

    def tearDown(self):
        """Rolls back any changes made in the test."""

        db.session.rollback()

    # MESSAGE TESTS #################################################

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    # LIKE TESTS ####################################################

    def create_likes(self):
        """Sets up some messages and likes for testing purposes."""

        msg_1 = Message(text="Test Message 1", user_id=self.uid_1)
        m

    def test_add_like(self):
        """Can a user like someone else's message?"""