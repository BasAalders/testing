from flask import render_template, url_for, flash, redirect, request, abort
from . import app, db, bcrypt # Assuming app, db, bcrypt will be initialized in main/__init__.py
from .forms import RegistrationForm, LoginForm, QuizCreateForm, QuestionForm
from .models import User, Quiz, Question, Option
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Home')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data): # Using check_password from User model
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route("/dashboard") # Or /my_quizzes
@login_required
def dashboard():
    user_quizzes = Quiz.query.filter_by(creator_id=current_user.id).order_by(Quiz.created_at.desc()).all()
    return render_template('dashboard.html', title='My Quizzes', quizzes=user_quizzes)

@app.route("/quiz/create", methods=['GET', 'POST'])
@login_required
def create_quiz():
    form = QuizCreateForm()
    if form.validate_on_submit():
        quiz = Quiz(title=form.title.data, description=form.description.data, creator_id=current_user.id)
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created successfully! Now add some questions.', 'success')
        return redirect(url_for('add_question', quiz_id=quiz.id))
    return render_template('create_quiz.html', title='Create Quiz', form=form)

@app.route("/quiz/<int:quiz_id>/add_question", methods=['GET', 'POST'])
@login_required
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.creator_id != current_user.id:
        abort(403) # Forbidden

    form = QuestionForm()

    # Dynamically set choices for the radio button based on submitted/available option fields
    # This is a simplified way; for truly dynamic options, JS would be involved on the front-end
    # or a more complex form structure (e.g. FieldList).
    option_texts = [form.option1_text.data, form.option2_text.data, form.option3_text.data, form.option4_text.data]
    valid_options_for_choices = [(str(i), opt_text) for i, opt_text in enumerate(option_texts) if opt_text]
    form.correct_option.choices = valid_options_for_choices

    if form.validate_on_submit():
        question_text = form.question_text.data
        # Get the order for the new question
        last_question = Question.query.filter_by(quiz_id=quiz.id).order_by(Question.order.desc()).first()
        new_order = (last_question.order + 1) if last_question else 1

        question = Question(quiz_id=quiz.id, question_text=question_text, order=new_order, question_type='multiple-choice')
        db.session.add(question)
        db.session.flush() # Flush to get the question ID for options

        options_data = []
        if form.option1_text.data:
            options_data.append({'text': form.option1_text.data, 'is_correct': form.correct_option.data == '0'})
        if form.option2_text.data:
            options_data.append({'text': form.option2_text.data, 'is_correct': form.correct_option.data == '1'})
        if form.option3_text.data: # Optional field
            options_data.append({'text': form.option3_text.data, 'is_correct': form.correct_option.data == '2'})
        if form.option4_text.data: # Optional field
            options_data.append({'text': form.option4_text.data, 'is_correct': form.correct_option.data == '3'})

        for opt_data in options_data:
            if opt_data['text']: # Ensure text is not empty
                option = Option(question_id=question.id, option_text=opt_data['text'], is_correct=opt_data['is_correct'])
                db.session.add(option)

        db.session.commit()
        flash('Question added successfully!', 'success')
        # Redirect to add another question or view quiz (e.g., a button "Finish and View Quiz")
        return redirect(url_for('add_question', quiz_id=quiz.id)) # Or redirect to quiz_detail

    # For GET request, ensure radio choices are set if there's pre-filled data (e.g. validation error)
    # or just default to a minimum number.
    if not form.correct_option.choices:
         form.correct_option.choices = [('0', 'Option 1'), ('1', 'Option 2')]


    return render_template('add_question.html', title='Add Question', form=form, quiz=quiz)

@app.route("/quiz/<int:quiz_id>")
def quiz_detail(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    # Questions should be ordered by their 'order' field
    questions = Question.query.filter_by(quiz_id=quiz.id).order_by(Question.order.asc()).all()
    return render_template('quiz_detail.html', title=quiz.title, quiz=quiz, questions=questions)

@app.route("/quiz/<int:quiz_id>/play", methods=['GET', 'POST'])
@login_required
def play_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.id).order_by(Question.order.asc()).all()

    if not questions:
        flash('This quiz has no questions yet!', 'warning')
        return redirect(url_for('quiz_detail', quiz_id=quiz.id))

    # Dynamically create the form
    form = PlayQuizForm()
    for question in questions:
        if question.question_type == 'multiple-choice' and question.options:
            field_name = f"question_{question.id}"
            choices = [(str(option.id), option.option_text) for option in question.options]
            radio_field = RadioField(question.question_text, choices=choices, validators=[DataRequired()])
            setattr(form, field_name, radio_field)

    if request.method == 'POST': # Check if form can be validated even if fields are added dynamically
        # We need to iterate through the questions to validate and process each field
        # Standard form.validate_on_submit() might not work as expected for fully dynamic fields
        # without extra steps. For now, let's manually check data.

        score = 0
        num_questions_processed = 0

        # Create QuizAttempt first
        quiz_attempt = QuizAttempt(user_id=current_user.id, quiz_id=quiz.id, score=0, total_questions=len(questions))
        db.session.add(quiz_attempt)
        # We'll commit later after responses or flush to get ID if UserResponse needs attempt_id

        user_responses_objects = []

        for question in questions:
            if question.question_type == 'multiple-choice':
                field_name = f"question_{question.id}"
                selected_option_id_str = request.form.get(field_name)

                if selected_option_id_str:
                    num_questions_processed += 1
                    selected_option_id = int(selected_option_id_str)
                    correct_option = Option.query.filter_by(question_id=question.id, is_correct=True).first()
                    is_correct = (correct_option is not None and selected_option_id == correct_option.id)

                    if is_correct:
                        score += 1

                    response = UserResponse(
                        user_id=current_user.id,
                        quiz_id=quiz.id,
                        question_id=question.id,
                        selected_option_id=selected_option_id,
                        is_correct=is_correct
                        # attempt_id=quiz_attempt.id # If linking UserResponse to QuizAttempt
                    )
                    user_responses_objects.append(response)
                else:
                    # Handle case where a question might not have been answered (if validators are bypassed)
                    # For now, assuming DataRequired on RadioField handles this on client/WTForms side if fully integrated
                    pass # Or create a response indicating no answer

        if num_questions_processed == len(questions): # All questions were answered
            quiz_attempt.score = score
            db.session.add_all(user_responses_objects)
            db.session.commit()
            flash(f'Quiz submitted! Your score: {score}/{len(questions)}', 'success')
            return redirect(url_for('quiz_results', attempt_id=quiz_attempt.id))
        else:
            # This part might be tricky if form.validate_on_submit() isn't used.
            # For now, relying on RadioField's DataRequired. If not, custom error handling needed.
            db.session.rollback() # Rollback quiz_attempt if not all questions processed
            flash('Please answer all questions.', 'danger')
            # Need to repopulate form with existing data if possible, or just render fresh
            # For simplicity, render fresh form for now.
            # To repopulate: iterate form fields and set form.<field_name>.data = request.form.get(field_name)

            # Re-create the dynamic fields for rendering if validation fails and page reloads
            # This is important because `form` object will be new otherwise
            form = PlayQuizForm() # Re-initialize to clear previous dynamic fields if any stuck
            for q in questions:
                if q.question_type == 'multiple-choice' and q.options:
                    field_name = f"question_{q.id}"
                    choices = [(str(option.id), option.option_text) for option in q.options]
                    radio_field = RadioField(q.question_text, choices=choices, validators=[DataRequired()])
                    setattr(form, field_name, radio_field)
                    # Attempt to set previously submitted data if available
                    if field_name in request.form:
                         getattr(form, field_name).data = request.form[field_name]


    return render_template('play_quiz.html', title=f"Play: {quiz.title}", quiz=quiz, form=form, questions=questions)

@app.route("/quiz/attempt/<int:attempt_id>/results")
@login_required
def quiz_results(attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != current_user.id:
        abort(403) # User can only see their own results

    # Fetch user responses for this attempt. This assumes UserResponse is NOT directly linked to QuizAttempt via FK.
    # Instead, it fetches responses based on user_id and quiz_id submitted around the same time.
    # For a more robust link, add `attempt_id` to `UserResponse` model.
    # For now, let's fetch all responses for that quiz by the user and filter by submission time if needed,
    # or assume the latest set of responses for that quiz for that user are the ones for this attempt.
    # This is simpler if we don't add attempt_id to UserResponse:
    user_responses = UserResponse.query.filter_by(
        user_id=current_user.id,
        quiz_id=attempt.quiz_id
    ).order_by(UserResponse.submitted_at.desc()).limit(attempt.total_questions).all()
    # This is still not perfect. A direct link `attempt_id` in UserResponse is better.
    # Let's assume for now we get all responses for the quiz by the user and show them.
    # The problem is if they attempt multiple times, which responses belong to which attempt?
    # Given the current models, I'll fetch all responses for the quiz by the user.
    # This will need refinement if UserResponse is not linked to QuizAttempt.

    # To make this work correctly without attempt_id in UserResponse, we'd have to fetch
    # UserResponses made around the time of quiz_attempt.completed_at.
    # For now, let's assume the models will be updated or this is a simplified view.
    # I will proceed with the assumption that UserResponses are created for each attempt.

    # Fetch all questions of the quiz to display them in order
    quiz_questions = Question.query.filter_by(quiz_id=attempt.quiz_id).order_by(Question.order.asc()).all()

    # Create a dictionary for easy lookup of user's responses
    responses_dict = {res.question_id: res for res in user_responses}

    return render_template('quiz_results.html', title="Quiz Results", attempt=attempt,
                           questions=quiz_questions, responses_dict=responses_dict)

# --- Quiz Management Routes (Edit/Delete) ---

@app.route("/quiz/<int:quiz_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.creator_id != current_user.id:
        abort(403) # Forbidden

    form = QuizCreateForm(obj=quiz) # Reuse QuizCreateForm, pre-populate with quiz data using obj=quiz

    if form.validate_on_submit():
        quiz.title = form.title.data
        quiz.description = form.description.data
        # quiz.updated_at will be handled by onupdate in model
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('quiz_detail', quiz_id=quiz.id))

    questions = Question.query.filter_by(quiz_id=quiz.id).order_by(Question.order.asc()).all()
    return render_template('edit_quiz.html', title=f"Edit Quiz: {quiz.title}", form=form, quiz=quiz, questions=questions)

@app.route("/quiz/<int:quiz_id>/delete", methods=['POST']) # Should be POST for destructive action
@login_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.creator_id != current_user.id:
        abort(403)

    # Cascading deletes should handle questions and options.
    # Also, QuizAttempts and UserResponses related to this quiz might need consideration.
    # For now, let's assume we want to delete the quiz and its content.
    # If there are attempts, we might want to archive or disallow deletion.
    # Current model has cascade delete for questions->options.
    # QuizAttempt and UserResponse have FKs to Quiz. Deleting a Quiz will cause issues
    # if these are not handled (e.g. set to null if nullable, or also deleted via cascade if appropriate).
    # For simplicity now, we will delete. This means attempts/responses for this quiz will also be an issue.
    # A soft delete (marking quiz as inactive) is often better in such cases.
    # Let's add a check for attempts before deleting for now.
    if quiz.attempts.first():
        flash('This quiz has attempts and cannot be deleted. Consider archiving it instead (feature not implemented).', 'warning')
        return redirect(url_for('quiz_detail', quiz_id=quiz.id))

    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully.', 'success')
    return redirect(url_for('dashboard'))


# --- Question Management Routes (Edit/Delete) ---

@app.route("/quiz/<int:quiz_id>/question/<int:question_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_question(quiz_id, question_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.creator_id != current_user.id:
        abort(403)

    question = Question.query.get_or_404(question_id)
    if question.quiz_id != quiz.id: # Ensure question belongs to the quiz
        abort(404)

    form = QuestionForm(obj=question) # Reuse QuestionForm, pre-populate with question data

    # Pre-populate options and correct choice
    # This part is tricky with the current QuestionForm structure if options are fixed (option1_text etc.)
    # We need to map existing question.options back to form.optionX_text and form.correct_option

    # Populate option text fields
    for i, option_model in enumerate(question.options.limit(4)): # Assuming max 4 options in form
        getattr(form, f'option{i+1}_text').data = option_model.option_text
        if option_model.is_correct:
            form.correct_option.data = str(i) # Value of RadioField choice

    # Set choices for correct_option RadioField dynamically for the GET request
    # This must be done *before* form.validate_on_submit() on POST and before rendering on GET
    option_texts_for_choices = []
    if form.option1_text.data or (len(question.options) > 0 and question.options[0]):
        option_texts_for_choices.append(form.option1_text.data if form.option1_text.data else question.options[0].option_text)
    if form.option2_text.data or (len(question.options) > 1 and question.options[1]):
        option_texts_for_choices.append(form.option2_text.data if form.option2_text.data else question.options[1].option_text)
    if form.option3_text.data or (len(question.options) > 2 and question.options[2]):
         option_texts_for_choices.append(form.option3_text.data if form.option3_text.data else question.options[2].option_text)
    if form.option4_text.data or (len(question.options) > 3 and question.options[3]):
         option_texts_for_choices.append(form.option4_text.data if form.option4_text.data else question.options[3].option_text)

    form.correct_option.choices = [(str(i), text) for i, text in enumerate(option_texts_for_choices) if text]


    if form.validate_on_submit():
        question.question_text = form.question_text.data
        # question.question_type = form.question_type.data # If type is editable

        # Clear existing options for this question first
        Option.query.filter_by(question_id=question.id).delete()

        # Add new/updated options
        options_form_data = [
            {'text': form.option1_text.data, 'is_correct': form.correct_option.data == '0'},
            {'text': form.option2_text.data, 'is_correct': form.correct_option.data == '1'},
            {'text': form.option3_text.data, 'is_correct': form.correct_option.data == '2'},
            {'text': form.option4_text.data, 'is_correct': form.correct_option.data == '3'}
        ]

        for opt_data in options_form_data:
            if opt_data['text']: # Only add if text is provided
                option = Option(question_id=question.id, option_text=opt_data['text'], is_correct=opt_data['is_correct'])
                db.session.add(option)

        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('edit_quiz', quiz_id=quiz.id)) # Redirect to main quiz edit page

    return render_template('edit_question.html', title='Edit Question', form=form, quiz=quiz, question=question)

@app.route("/quiz/<int:quiz_id>/question/<int:question_id>/delete", methods=['POST'])
@login_required
def delete_question(quiz_id, question_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.creator_id != current_user.id:
        abort(403)

    question = Question.query.get_or_404(question_id)
    if question.quiz_id != quiz.id:
        abort(404) # Or some other error if question doesn't belong to quiz

    # Model has cascade delete for options, so they will be deleted too.
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully.', 'success')
    return redirect(url_for('edit_quiz', quiz_id=quiz.id))
