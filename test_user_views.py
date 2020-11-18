"""User View tests."""

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


class UserViewTestCase(TestCase):
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

        db.session.commit()

        self.uid_test = self.testuser.id
        self.uid_1 = self.user_1.id
        self.uid_2 = self.user_2.id

    def tearDown(self):
        """Rolls back any changes made in the test."""

        db.session.rollback()

    def test_view_own_profile(self):
        """Can user view own profile?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_test

            resp = c.get(f"/users/{self.uid_test}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                f"""@testuser</a></h4>""",
                html,
            )
            self.assertIn("Edit</button>", html)

    def test_view_other_profile(self):
        """Can user view someone else's profile?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1

            resp = c.get(f"/users/{self.uid_2}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                f"""@user2</a></h4>""",
                html,
            )
            self.assertNotIn("Edit</button>", html)

    def test_view_own_follows_followers(self):
        """Can a user view their own followed users and followers?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_test

            resp_following = c.get(f"/users/{self.uid_test}/following")
            html_following = resp_following.get_data(as_text=True)

            resp_followers = c.get(f"users/{self.uid_test}/followers")
            html_followers = resp_followers.get_data(as_text=True)

            self.assertIn(f"Followed by @{self.testuser.username}:", html_following)
            self.assertIn(f"Followers of @{self.testuser.username}:", html_followers)

    def test_view_own_likes(self):
        """Can a user view their own liked messages?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1

            resp = c.get(f"/users/{self.uid_1}/likes")
            html = resp.get_data(as_text=True)

            self.assertIn("Liked by @user1:", html)

    def test_view_other_likes(self):
        """Can a user view someone else's liked messages?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1

            resp = c.get(f"/users/{self.uid_2}/likes")
            html = resp.get_data(as_text=True)

            self.assertIn("Liked by @user2:", html)

    def test_list_users(self):
        """Does the list of users show all users?"""

        with self.client as c:
            resp = c.get("/users")
            html = resp.get_data(as_text=True)

            self.assertIn("testuser", html)
            self.assertIn("user1", html)
            self.assertIn("user2", html)

    def test_sign_up(self):
        """Does posting to /signup work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                if sess.get(CURR_USER_KEY):
                    del sess[CURR_USER_KEY]

            resp = c.post(
                "/signup",
                data={
                    "username": "newuser",
                    "email": "newuser@test.com",
                    "password": "password",
                },
            )

            user = User.query.filter_by(email="newuser@test.com").first()

            self.assertEqual(user.username, "newuser")
