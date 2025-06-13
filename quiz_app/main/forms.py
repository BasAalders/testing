from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, RadioField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from .models import User # Assuming models.py contains User, Quiz, Question, Option

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class QuizCreateForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired(), Length(min=3, max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Create Quiz')

class QuestionForm(FlaskForm):
    question_text = TextAreaField('Question Text', validators=[DataRequired()])
    # For simplicity, question_type is defaulted in model, could be a SelectField here if needed:
    # question_type = SelectField('Question Type', choices=[('multiple-choice', 'Multiple Choice'), ('true-false', 'True/False')], default='multiple-choice', validators=[DataRequired()])

    # Simplified options - specific to multiple-choice with 2 to 4 options
    # A more dynamic solution would use FieldList of FormField.
    option1_text = StringField('Option 1 Text', validators=[DataRequired()])
    option2_text = StringField('Option 2 Text', validators=[DataRequired()])
    option3_text = StringField('Option 3 Text', validators=[Optional()]) # Optional
    option4_text = StringField('Option 4 Text', validators=[Optional()]) # Optional

    # RadioField to select the correct answer. Choices will be set in the route.
    # The 'choices' attribute will be like [('0', 'Option 1'), ('1', 'Option 2'), ...]
    # The validator ensures one option is chosen.
    correct_option = RadioField('Correct Answer', validators=[DataRequired()], choices=[])

    submit = SubmitField('Add Question')

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        # Dynamically set choices for correct_option based on provided option fields
        # This is a common pattern but might need adjustment based on how options are named/accessed
        # For now, this is a placeholder; actual choices need to be set in the route
        # or based on how many option fields are actually rendered and filled.
        # Example: self.correct_option.choices = [('0', 'Option 1'), ('1', 'Option 2')]
        # This will be handled in the route that uses this form.

class PlayQuizForm(FlaskForm):
    # This form will be populated dynamically with RadioFields in the route.
    # Example: For a question with id 5, a field named 'question_5' (RadioField) will be added.
    submit = SubmitField('Submit Answers')
