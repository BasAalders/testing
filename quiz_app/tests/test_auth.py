import unittest
from .base import BaseTestCase
from quiz_app.main.models import User
from quiz_app.main import db

class AuthTestCase(BaseTestCase):

    def register_user(self, username, email, password, confirm_password):
        """Helper method to register a user."""
        return self.client.post(
            '/register',
            data=dict(username=username, email=email, password=password, confirm_password=confirm_password),
            follow_redirects=True
        )

    def login_user(self, email, password):
        """Helper method to log in a user."""
        return self.client.post(
            '/login',
            data=dict(email=email, password=password),
            follow_redirects=True
        )

    def logout_user(self):
        """Helper method to log out a user."""
        return self.client.get('/logout', follow_redirects=True)

    def test_user_registration_successful(self):
        """Test user registration with valid data."""
        response = self.register_user('testuser', 'test@example.com', 'password123', 'password123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your account has been created!', response.data)
        user = User.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')

    def test_user_registration_duplicate_username(self):
        """Test user registration with a duplicate username."""
        self.register_user('testuser', 'test1@example.com', 'password123', 'password123')
        response = self.register_user('testuser', 'test2@example.com', 'password123', 'password123')
        self.assertEqual(response.status_code, 200) # Stays on registration page
        self.assertIn(b'That username is taken.', response.data)

    def test_user_registration_duplicate_email(self):
        """Test user registration with a duplicate email."""
        self.register_user('testuser1', 'test@example.com', 'password123', 'password123')
        response = self.register_user('testuser2', 'test@example.com', 'password123', 'password123')
        self.assertEqual(response.status_code, 200) # Stays on registration page
        self.assertIn(b'That email is already in use.', response.data)

    def test_user_registration_password_mismatch(self):
        """Test user registration with mismatched passwords."""
        response = self.register_user('testuser3', 'test3@example.com', 'password123', 'password321')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Field must be equal to password.', response.data) # Default WTForms message

    def test_user_login_successful(self):
        """Test user login with correct credentials."""
        self.register_user('testlogin', 'login@example.com', 'password123', 'password123')
        # Logout if registration auto-logs in (current app does not, redirects to login)
        # self.logout_user()
        response = self.login_user('login@example.com', 'password123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful!', response.data) # Flash message
        self.assertIn(b'Logout (testlogin)', response.data) # Check if username appears in nav

    def test_user_login_incorrect_password(self):
        """Test user login with an incorrect password."""
        self.register_user('testlogin2', 'login2@example.com', 'password123', 'password123')
        response = self.login_user('login2@example.com', 'wrongpassword')
        self.assertEqual(response.status_code, 200) # Stays on login page
        self.assertIn(b'Login Unsuccessful. Please check email and password', response.data)

    def test_user_login_nonexistent_user(self):
        """Test user login for a user that does not exist."""
        response = self.login_user('nonexistent@example.com', 'password123')
        self.assertEqual(response.status_code, 200) # Stays on login page
        self.assertIn(b'Login Unsuccessful. Please check email and password', response.data)

    def test_user_logout(self):
        """Test user logout."""
        self.register_user('testlogout', 'logout@example.com', 'password123', 'password123')
        self.login_user('logout@example.com', 'password123') # Login first
        response = self.logout_user()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out.', response.data)
        self.assertIn(b'Login', response.data) # Login link should be visible again
        self.assertNotIn(b'Logout (testlogout)', response.data)

if __name__ == '__main__':
    unittest.main()
