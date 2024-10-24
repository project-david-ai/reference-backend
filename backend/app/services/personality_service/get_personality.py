from backend.app.extensions import db
from backend.app.models import Instruction
from backend.app import create_app

# Import the Flask application instance

def get_personality(ai_entity, personality):
    try:
        # Create an application context
        app = create_app()
        with app.app_context():
            instruction = Instruction.query.filter_by(ai_entity=ai_entity).first()
            if instruction and instruction.personality_data:
                return instruction.personality_data.get(personality)

    except Exception as e:
        pass  # Handling of the exception can be logged or managed as needed

if __name__ == "__main__":
    ai_entity = "Q"
    personality = "general_base_personality"
    app = create_app()  # Pass the Flask application instance
    personality_data = get_personality(ai_entity, personality)
    print(personality_data)
    if personality_data:
        for trait in personality_data:
            print(f"{trait['type']}: {trait['value']}")