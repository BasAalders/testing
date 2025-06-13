import unittest
from .base import BaseTestCase
from quiz_app.main.models import User, Quiz, Question, Option, QuizAttempt, UserResponse
from quiz_app.main import db

class QuizTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        # Create and log in a default user for many tests
        self.register_user('testcreator', 'creator@example.com', 'password123')
        self.login_user('creator@example.com', 'password123')

        # Get user object if needed for associating with quizzes
        self.user = User.query.filter_by(email='creator@example.com').first()

    # --- Helper Methods ---
    def register_user(self, username, email, password):
        return self.client.post('/register', data=dict(
            username=username, email=email, password=password, confirm_password=password
        ), follow_redirects=True)

    def login_user(self, email, password):
        return self.client.post('/login', data=dict(
            email=email, password=password
        ), follow_redirects=True)

    def logout_user(self):
        return self.client.get('/logout', follow_redirects=True)

    def create_quiz(self, title, description):
        """Helper to create a quiz via POST request."""
        return self.client.post('/quiz/create', data=dict(
            title=title,
            description=description
        ), follow_redirects=True)

    def add_question_to_quiz(self, quiz_id, question_text, options, correct_option_index):
        """
        Helper to add a multiple-choice question to a quiz.
        options: list of strings for option texts.
        correct_option_index: 0-based index for the correct option in the list.
        """
        form_data = {
            'question_text': question_text,
            'correct_option': str(correct_option_index) # Value for RadioField
        }
        for i, option_text in enumerate(options):
            form_data[f'option{i+1}_text'] = option_text

        # Fill remaining option fields if fewer than 4 options provided, to satisfy QuestionForm
        for i in range(len(options), 4):
             form_data[f'option{i+1}_text'] = ''


        return self.client.post(f'/quiz/{quiz_id}/add_question', data=form_data, follow_redirects=True)

    # --- Test Cases ---

    def test_create_quiz_get_page(self):
        """Test GET request for create quiz page."""
        response = self.client.get('/quiz/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create New Quiz', response.data)

    def test_create_quiz_successful(self):
        """Test successful quiz creation."""
        response = self.create_quiz('My First Quiz', 'A simple quiz about something.')
        self.assertEqual(response.status_code, 200) # Redirects to add_question
        self.assertIn(b'Quiz created successfully!', response.data)
        self.assertIn(b'Add Question to "My First Quiz"', response.data)
        quiz = Quiz.query.filter_by(title='My First Quiz').first()
        self.assertIsNotNone(quiz)
        self.assertEqual(quiz.creator_id, self.user.id)

    def test_create_quiz_requires_login(self):
        """Test that creating a quiz requires login."""
        self.logout_user()
        response = self.create_quiz('Another Quiz', 'Should not be created.')
        self.assertEqual(response.status_code, 200) # Redirects to login
        self.assertIn(b'Please log in to access this page.', response.data) # Flash message from login_required
        quiz = Quiz.query.filter_by(title='Another Quiz').first()
        self.assertIsNone(quiz)

    def test_edit_quiz(self):
        """Test editing an existing quiz's metadata."""
        # Create a quiz first
        self.create_quiz('Original Title', 'Original Description')
        quiz = Quiz.query.filter_by(title='Original Title').first()
        self.assertIsNotNone(quiz)

        # Edit the quiz
        response = self.client.post(f'/quiz/{quiz.id}/edit', data=dict(
            title='Updated Title',
            description='Updated Description'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Quiz updated successfully!', response.data)
        self.assertIn(b'Updated Title', response.data) # On quiz_detail page

        updated_quiz = Quiz.query.get(quiz.id)
        self.assertEqual(updated_quiz.title, 'Updated Title')
        self.assertEqual(updated_quiz.description, 'Updated Description')

    def test_delete_quiz_no_attempts(self):
        """Test deleting a quiz that has no attempts."""
        self.create_quiz('Quiz to Delete', 'This quiz will be deleted.')
        quiz = Quiz.query.filter_by(title='Quiz to Delete').first()
        self.assertIsNotNone(quiz)

        response = self.client.post(f'/quiz/{quiz.id}/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Redirects to dashboard
        self.assertIn(b'Quiz deleted successfully.', response.data)
        deleted_quiz = Quiz.query.get(quiz.id)
        self.assertIsNone(deleted_quiz)

    def test_add_question_to_quiz(self):
        """Test adding a question to an existing quiz."""
        self.create_quiz('Quiz For Questions', 'Adding questions here.')
        quiz = Quiz.query.filter_by(title='Quiz For Questions').first()
        self.assertIsNotNone(quiz)

        response = self.add_question_to_quiz(
            quiz.id,
            'What is 2+2?',
            ['3', '4', '5'],
            1 # '4' is correct
        )
        self.assertEqual(response.status_code, 200) # Stays on add_question page
        self.assertIn(b'Question added successfully!', response.data)

        question = Question.query.filter_by(quiz_id=quiz.id, question_text='What is 2+2?').first()
        self.assertIsNotNone(question)
        self.assertEqual(len(question.options.all()), 3)
        correct_option = Option.query.filter_by(question_id=question.id, is_correct=True).first()
        self.assertIsNotNone(correct_option)
        self.assertEqual(correct_option.option_text, '4')

    def test_edit_question(self):
        """Test editing an existing question."""
        self.create_quiz('Quiz For Editing Q', '...')
        quiz = Quiz.query.filter_by(title='Quiz For Editing Q').first()
        self.add_question_to_quiz(quiz.id, 'Old Question Text?', ['OptA', 'OptB'], 0)
        question = Question.query.filter_by(quiz_id=quiz.id).first()
        self.assertIsNotNone(question)

        response = self.client.post(f'/quiz/{quiz.id}/question/{question.id}/edit', data=dict(
            question_text='New Question Text?',
            option1_text='NewOptX',
            option2_text='NewOptY',
            option3_text='', # Optional
            option4_text='', # Optional
            correct_option='1' # NewOptY is correct
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Redirects to edit_quiz page
        self.assertIn(b'Question updated successfully!', response.data)

        updated_question = Question.query.get(question.id)
        self.assertEqual(updated_question.question_text, 'New Question Text?')
        self.assertEqual(len(updated_question.options.all()), 2) # Only two options provided
        correct_option = Option.query.filter_by(question_id=updated_question.id, is_correct=True).first()
        self.assertEqual(correct_option.option_text, 'NewOptY')

    def test_delete_question(self):
        """Test deleting a question from a quiz."""
        self.create_quiz('Quiz For Deleting Q', '...')
        quiz = Quiz.query.filter_by(title='Quiz For Deleting Q').first()
        self.add_question_to_quiz(quiz.id, 'Q to Delete', ['Yes', 'No'], 0)
        question = Question.query.filter_by(quiz_id=quiz.id).first()
        self.assertIsNotNone(question)
        question_id = question.id # Save id as question will be deleted from session

        response = self.client.post(f'/quiz/{quiz.id}/question/{question.id}/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Redirects to edit_quiz page
        self.assertIn(b'Question deleted successfully!', response.data)
        deleted_question = Question.query.get(question_id)
        self.assertIsNone(deleted_question)
        # Also check options are deleted due to cascade
        self.assertEqual(Option.query.filter_by(question_id=question_id).count(), 0)


    def test_quiz_play_and_results(self):
        """Test playing a quiz and checking results."""
        self.create_quiz('Playable Quiz', 'Let us play.')
        quiz = Quiz.query.filter_by(title='Playable Quiz').first()
        self.add_question_to_quiz(quiz.id, 'Q1: 2+2=?', ['3', '4', '5'], 1) # Correct: 4 (id will be X)
        self.add_question_to_quiz(quiz.id, 'Q2: Capital of France?', ['London', 'Paris', 'Berlin'], 1) # Correct: Paris (id will be Y)

        q1 = Question.query.filter_by(question_text='Q1: 2+2=?').first()
        q2 = Question.query.filter_by(question_text='Q2: Capital of France?').first()

        q1_correct_option_id = Option.query.filter_by(question_id=q1.id, is_correct=True).first().id
        q2_wrong_option_id = Option.query.filter_by(question_id=q2.id, option_text='London').first().id

        # Play the quiz
        play_data = {
            f'question_{q1.id}': str(q1_correct_option_id), # Correct answer for Q1
            f'question_{q2.id}': str(q2_wrong_option_id)    # Incorrect answer for Q2
        }
        response = self.client.post(f'/quiz/{quiz.id}/play', data=play_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Redirects to results page
        self.assertIn(b'Quiz submitted! Your score: 1/2', response.data) # Score: 1 out of 2

        attempt = QuizAttempt.query.filter_by(quiz_id=quiz.id, user_id=self.user.id).first()
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.score, 1)
        self.assertEqual(attempt.total_questions, 2)

        # Check UserResponses
        responses = UserResponse.query.filter_by(quiz_id=quiz.id, user_id=self.user.id).all()
        self.assertEqual(len(responses), 2)

        q1_response = UserResponse.query.filter_by(question_id=q1.id, user_id=self.user.id).first()
        self.assertTrue(q1_response.is_correct)
        self.assertEqual(q1_response.selected_option_id, q1_correct_option_id)

        q2_response = UserResponse.query.filter_by(question_id=q2.id, user_id=self.user.id).first()
        self.assertFalse(q2_response.is_correct)
        self.assertEqual(q2_response.selected_option_id, q2_wrong_option_id)

        # Check results page content
        self.assertIn(b'Q1: 2+2=?', response.data)
        self.assertIn(b'Your answer was correct.', response.data)
        self.assertIn(b'Q2: Capital of France?', response.data)
        self.assertIn(b'Your answer was incorrect.', response.data)


    def test_edit_quiz_unauthorized(self):
        """Test that a user cannot edit another user's quiz."""
        # creator@example.com creates a quiz
        self.create_quiz('Creators Quiz', '...')
        quiz = Quiz.query.filter_by(title='Creators Quiz').first()

        # New user logs in
        self.logout_user()
        self.register_user('otheruser', 'other@example.com', 'password123')
        self.login_user('other@example.com', 'password123')

        response = self.client.get(f'/quiz/{quiz.id}/edit', follow_redirects=True)
        self.assertEqual(response.status_code, 403) # Forbidden

        response = self.client.post(f'/quiz/{quiz.id}/edit', data={'title': 'Hacked'}, follow_redirects=True)
        self.assertEqual(response.status_code, 403) # Forbidden


if __name__ == '__main__':
    unittest.main()
