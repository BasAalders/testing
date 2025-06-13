import unittest
from quiz_app.main import app, db
from quiz_app.main.models import User, Quiz, Question, Option, QuizAttempt, UserResponse

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test variables."""
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF forms handling for tests
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use in-memory SQLite
        app.config['LOGIN_DISABLED'] = False # Ensure login is not disabled unless specifically tested

        self.app = app
        self.client = self.app.test_client() # Create a test client
        self.app_context = self.app.app_context()
        self.app_context.push() # Push an application context

        db.create_all() # Create all database tables

    def tearDown(self):
        """Executed after each test."""
        db.session.remove() # Remove database session
        db.drop_all() # Drop all database tables
        self.app_context.pop() # Pop the application context

    # Helper methods can be added here later, e.g., for user registration/login

if __name__ == '__main__':
    unittest.main()
