# BrainBox Project Guide

## What you can demonstrate

1. Register a new student.
2. Login.
3. Open Dashboard.
4. Select Python > Recursion/Functions or another available topic.
5. Attempt the quiz.
6. Submit and show the automatic score.
7. Return to Dashboard and show attempt history.
8. If the score is below 60%, show the topic under "Topics to Revise".
9. Login with the admin account.
10. Open Admin Panel.
11. Add a new question.
12. Show that the question appears in the question bank.

## Important project explanation

The project uses a rule-based personalization approach rather than machine learning. A topic is considered a revision focus when the student's average performance for that topic is below 60%.

This is simple, explainable and appropriate for a mini project.

## Suggested viva explanation

Frontend:
HTML and CSS are used to create the user interface.

Backend:
Python Flask handles routing, form submission, authentication, quiz evaluation and database operations.

Database:
SQLite stores users, questions, quiz attempts and answer results.

Personalization:
The system groups attempts by subject and topic and calculates the average percentage. Topics below 60% are shown as revision topics.

## Important

This is an academic/demo project. Passwords are stored as plain text in this simplified version so the code is easy to understand. For a real application, passwords should be securely hashed.
