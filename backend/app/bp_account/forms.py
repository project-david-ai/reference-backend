# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Regexp


class OTPForm(FlaskForm):
    # Regex pattern for validating international phone numbers
    phone_regex = Regexp(r'^\+\d{1,15}$', message="Enter a valid phone number with international dialing format e.g., +1234567890")

    number = StringField('Phone Number', validators=[DataRequired(), phone_regex])
