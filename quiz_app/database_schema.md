# Database Schema for Quiz Application

This document outlines the schema for the database used by the Quiz Application.

## 1. Users Table (`users`)

Stores information about registered users.

-   `id`: INTEGER - Primary Key, Auto-increment.
-   `username`: VARCHAR(255) - Unique, Not Null. User's chosen username.
-   `password_hash`: VARCHAR(255) - Not Null. Hashed password for security.
-   `email`: VARCHAR(255) - Unique, Not Null. User's email address.
-   `created_at`: TIMESTAMP - Default: CURRENT_TIMESTAMP. Timestamp of when the user account was created.

## 2. Quizzes Table (`quizzes`)

Stores information about the quizzes created by users.

-   `id`: INTEGER - Primary Key, Auto-increment.
-   `title`: VARCHAR(255) - Not Null. The title of the quiz.
-   `description`: TEXT - Nullable. A more detailed description of the quiz.
-   `creator_id`: INTEGER - Not Null, Foreign Key referencing `users.id`. The user who created the quiz.
-   `created_at`: TIMESTAMP - Default: CURRENT_TIMESTAMP. Timestamp of when the quiz was created.
-   `updated_at`: TIMESTAMP - Default: CURRENT_TIMESTAMP, ON UPDATE CURRENT_TIMESTAMP. Timestamp of the last update to the quiz.

## 3. Questions Table (`questions`)

Stores the individual questions that belong to a quiz.

-   `id`: INTEGER - Primary Key, Auto-increment.
-   `quiz_id`: INTEGER - Not Null, Foreign Key referencing `quizzes.id`. The quiz to which this question belongs.
-   `question_text`: TEXT - Not Null. The actual text of the question.
-   `question_type`: VARCHAR(50) - Not Null. Type of question (e.g., 'multiple-choice', 'true-false', 'short-answer').
-   `order`: INTEGER - Not Null. Determines the order in which questions appear within a quiz.
-   `created_at`: TIMESTAMP - Default: CURRENT_TIMESTAMP. Timestamp of when the question was created.

## 4. Options Table (`options`)

Stores the possible answers/options for multiple-choice or true-false questions.

-   `id`: INTEGER - Primary Key, Auto-increment.
-   `question_id`: INTEGER - Not Null, Foreign Key referencing `questions.id`. The question to which this option belongs.
-   `option_text`: TEXT - Not Null. The text of the option.
-   `is_correct`: BOOLEAN - Not Null. Indicates if this option is the correct answer for the question.
-   `created_at`: TIMESTAMP - Default: CURRENT_TIMESTAMP. Timestamp of when the option was created.

*Note: For 'short-answer' questions, this table might not be directly used. For 'true-false' questions, options like "True" and "False" would be stored here.*

## 5. User Responses Table (`user_responses`)

Stores the responses given by users to individual questions in a quiz attempt.

-   `id`: INTEGER - Primary Key, Auto-increment.
-   `user_id`: INTEGER - Not Null, Foreign Key referencing `users.id`. The user who submitted the response.
-   `quiz_id`: INTEGER - Not Null, Foreign Key referencing `quizzes.id`. The quiz for which the response was submitted.
-   `question_id`: INTEGER - Not Null, Foreign Key referencing `questions.id`. The specific question being answered.
-   `selected_option_id`: INTEGER - Nullable, Foreign Key referencing `options.id`. The option selected by the user (for multiple-choice).
-   `answer_text`: TEXT - Nullable. The text answer provided by the user (for short-answer questions).
-   `is_correct`: BOOLEAN - Not Null. Indicates if the user's response was correct. This is typically evaluated upon submission.
-   `submitted_at`: TIMESTAMP - Default: CURRENT_TIMESTAMP. Timestamp of when the response was submitted.

## 6. Quiz Attempts Table (`quiz_attempts`)

Stores information about a user's attempt at completing a quiz.

-   `id`: INTEGER - Primary Key, Auto-increment.
-   `user_id`: INTEGER - Not Null, Foreign Key referencing `users.id`. The user who attempted the quiz.
-   `quiz_id`: INTEGER - Not Null, Foreign Key referencing `quizzes.id`. The quiz that was attempted.
-   `score`: INTEGER - Not Null. The overall score achieved by the user for this attempt.
-   `started_at`: TIMESTAMP - Default: CURRENT_TIMESTAMP. Timestamp of when the user started the quiz attempt.
-   `completed_at`: TIMESTAMP - Nullable. Timestamp of when the user completed or submitted the quiz attempt. If null, the attempt might be in progress or abandoned.
