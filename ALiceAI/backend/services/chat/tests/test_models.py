import unittest
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm import Session

from app.models import Base, Conversation, Message, MessageRole


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:", execution_options={"schema_translate_map": {"public": None}}
        )
        with self.engine.connect() as connection:
            connection.exec_driver_sql("PRAGMA foreign_keys=ON")
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.addCleanup(self.engine.dispose)
        self.addCleanup(self.session.close)

    def test_defaults_roles_and_timestamps(self):
        conversation = Conversation(user_id="firebase-user")
        self.session.add(conversation)
        self.session.flush()
        self.assertEqual(conversation.title, "New Chat")
        self.assertIsNotNone(conversation.id)
        self.assertIsNotNone(conversation.created_at)
        self.assertIsNotNone(conversation.updated_at)
        for role in MessageRole:
            message = Message(conversation_id=conversation.id, role=role, content="Hello")
            self.session.add(message)
            self.session.flush()
            self.assertEqual(message.content, "Hello")
            self.assertIsNotNone(message.created_at)
            self.assertIsNotNone(message.updated_at)

    def test_updates_preserve_creation_time(self):
        old = datetime(2000, 1, 1, tzinfo=UTC)
        conversation = Conversation(
            user_id="firebase-user", created_at=old, updated_at=old
        )
        self.session.add(conversation)
        self.session.flush()
        message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content="Hello",
            created_at=old,
            updated_at=old,
        )
        self.session.add(message)
        self.session.flush()
        conversation.title = "Renamed"
        message.role = MessageRole.ASSISTANT
        self.session.flush()
        for model in (conversation, message):
            self.assertEqual(model.created_at, old)
            self.assertGreater(model.updated_at, old)

    def test_invalid_role_rejected(self):
        self.session.add(Message(conversation_id=uuid4(), role="system", content="Hello"))
        with self.assertRaises(StatementError):
            self.session.flush()

    def test_database_rejects_invalid_role(self):
        conversation = Conversation(user_id="firebase-user")
        self.session.add(conversation)
        self.session.flush()
        with self.assertRaises(IntegrityError):
            self.session.execute(
                text("INSERT INTO messages (id, conversation_id, role, content) "
                     "VALUES (:id, :conversation_id, 'system', 'Hello')"),
                {"id": uuid4().hex, "conversation_id": conversation.id.hex},
            )

    def test_missing_conversation_rejected(self):
        self.session.add(Message(conversation_id=uuid4(), role=MessageRole.USER, content="Hello"))
        with self.assertRaises(IntegrityError):
            self.session.flush()


if __name__ == "__main__":
    unittest.main()
