from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to Quizzes
    quizzes = db.relationship('Quiz', backref='creator', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to Questions
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Quiz {self.title}>'

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False, default='multiple-choice') # e.g., 'multiple-choice', 'true-false', 'short-answer'
    order = db.Column(db.Integer, nullable=False, default=0) # For ordering questions within a quiz
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to Options
    options = db.relationship('Option', backref='question', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Question {self.id} - {self.question_text[:30]}...>'

class Option(db.Model):
    __tablename__ = 'options'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Option {self.id} - {self.option_text[:30]}... (Correct: {self.is_correct})>'

class UserResponse(db.Model):
    __tablename__ = 'user_responses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=True) # Nullable if question_type is not multiple-choice
    answer_text = db.Column(db.Text, nullable=True) # For short-answer or other types
    is_correct = db.Column(db.Boolean, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('responses', lazy='dynamic'))
    quiz = db.relationship('Quiz', backref=db.backref('responses', lazy='dynamic'))
    question = db.relationship('Question', backref=db.backref('responses', lazy='dynamic'))
    selected_option = db.relationship('Option', backref=db.backref('responses', lazy='dynamic'))

    def __repr__(self):
        return f'<UserResponse u{self.user_id}-q{self.question_id} opt:{self.selected_option_id} correct:{self.is_correct}>'

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False) # Could be percentage or raw score
    total_questions = db.Column(db.Integer, nullable=False, default=0) # Store how many questions were in this attempt
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('quiz_attempts', lazy='dynamic'))
    quiz = db.relationship('Quiz', backref=db.backref('attempts', lazy='dynamic'))
    # If you want to link UserResponses to a specific attempt:
    # responses = db.relationship('UserResponse', backref='attempt', lazy='dynamic', foreign_keys='[UserResponse.attempt_id]') # Requires adding attempt_id to UserResponse

    def __repr__(self):
        return f'<QuizAttempt u{self.user_id}-qz{self.quiz_id} score:{self.score}>'
