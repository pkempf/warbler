"""Message model tests."""


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from models import db, User, Message, Follows

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"

from app import app

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

        user = User.signup(
            email="test@test.com", username="testuser", password="PASSWORD"
        )
        db.session.commit()

        self.user_id = user.id

        self.client = app.test_client()

    def tearDown(self):
        """Roll back changes."""

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        message = Message(text="Test Message Content", user_id=self.user_id)

        db.session.add(message)
        db.session.commit()

        self.assertIsInstance(message.id, int)
        self.assertEquals(message.text, "Test Message Content")
        self.assertEquals(message.user_id, self.user_id)
        self.assertIsInstance(message.timestamp, datetime)

    def test_repr(self):
        """Does __repr__ return what it should?"""

        message = Message(text="Test Message Content", user_id=self.user_id)

        db.session.add(message)
        db.session.commit()

        self.assertEqual(
            repr(message),
            f"<Message #{message.id}: Test Message Content | User {message.user_id} | {message.timestamp}>",
        )

    def test_create_empty_message(self):
        """Does Message.create fail (as it should) when no text is given?"""

        message = Message(user_id=self.user_id)

        integrity_error_thrown = False

        try:
            db.session.add(message)
            db.session.commit()
        except IntegrityError:
            integrity_error_thrown = True

        self.assertEqual(integrity_error_thrown, True)

    def test_create_orphaned_message(self):
        """Does Message.create fail (as it should) when no user_id is given?"""

        message = Message(text="Test Message Content")

        integrity_error_thrown = False

        try:
            db.session.add(message)
            db.session.commit()
        except IntegrityError:
            integrity_error_thrown = True

        self.assertEqual(integrity_error_thrown, True)

    def test_delete_message_when_orphaned(self):
        """When a message's user is deleted, is that message also deleted?"""

        message = Message(text="Test Message Content", user_id=self.user_id)
        db.session.commit()

        user = User.query.get(self.user_id)
        db.session.delete(user)
        db.session.commit()

        self.assertIsNone(message.id)
        self.assertIsNone(message.timestamp)
