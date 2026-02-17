from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import ConversationSession, Users
from config import config


def create_conversation_session(user_id, thread_id=None, config_name="default"):
    """
    Creates a new conversation session for the specified user.
    Optionally, a thread_id can be provided.
    """
    app = create_app()
    with app.app_context():
        user = Users.query.filter_by(id=user_id).first()
        if user is None:
            print(f"User with ID '{user_id}' not found.")
            return

        new_session = ConversationSession(user_id=user_id, thread_id=thread_id)
        db.session.add(new_session)
        db.session.commit()
        print(
            f"Conversation session created successfully for user {user.username} with session ID {new_session.id}."
        )


create_conversation_session(
    user_id="c8475de4-e267-4ef7-bf76-f51138721727",
    thread_id="thread_HnG5za7m2n2XrzezrVH4RiHW",
    config_name="default",
)
