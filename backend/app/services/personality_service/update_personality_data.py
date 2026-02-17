import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
)
from personality_design import (artistic_personality, educational_personality,
                                general_base_personality,
                                scientific_technological_personality)

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import Instruction


def update_personality_data(ai_entity, personality_data):
    try:
        # Create an application context
        app = create_app()
        with app.app_context():
            instruction = Instruction.query.filter_by(ai_entity=ai_entity).first()

            if instruction:
                instruction.personality_data = personality_data
                db.session.commit()
                print(
                    f"Personality data updated successfully for AI entity: {ai_entity}"
                )
            else:
                print(f"No instruction found for AI entity: {ai_entity}")
    except Exception as e:
        print(f"An error occurred while updating personality data: {str(e)}")
        db.session.rollback()


# Example usage


ai_entity = "Q"

# These inserts must all be present
# Missing personalities will not be presemnt
personality_data = {
    "general_base_personality": general_base_personality,
    "scientific_technological_personality": scientific_technological_personality,
    "educational_personality": educational_personality,
    "artistic_personality": artistic_personality,
}

if __name__ == "__main__":
    update_personality_data(ai_entity, personality_data)
