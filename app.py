from dis import Instruction
from urllib import response
from flask import Flask, request, render_template, redirect, flash, session, jsonify
import surveys
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

survey_list = surveys.surveys
completed_surveys = []

@app.route('/')
def homepage():
    print(completed_surveys)
    """Route for homepage. Titles of availible surveys are fetched and added to the session.
    on the rendered homepage there are clickable divs (small javascript script) that take you to each survey"""

    # Add list of survey titles to session
    survey_titles = []
    for survey in survey_list:
        survey_titles.append(str(survey))
    session['survey_titles'] = survey_titles

    #Render homepage
    return render_template('homepage.html')

@app.route('/<survey>/survey-setup')
def surv_set(survey):
    """Route for survey setup. Adds all information from the correct survey into the session.
    User then redirected to the first question (question 0) of their choosen survey."""

    # Add survey information to session
    session['cur_survey'] = survey
    session['cur_survey_title'] = survey_list[survey].title
    session['cur_question'] = 0
    session['instructions'] = survey_list[survey].instructions
    session['answers'] = []
    session['completed_surveys'] = completed_surveys
    # Add survey questions to session in a flask friendly format
    questions = []
    for question in survey_list[survey].questions:
        questions.append(question.__dict__)
    session['questions'] = questions
    session['cur_survey_len'] = len(questions)

    # Redirect to question 0
    return redirect('/question/0')

@app.route('/question/<int:question_num>')
def satisfaction_questions(question_num):
    '''Route for rendering the question page. Check if text is allowed for the question here.'''

    # Check if text is allowed on the question and save that info to session

    if bool(session['questions'][(session['cur_question'])]['allow_text']):
        session['text_allowed'] = True
    else:
        session['text_allowed'] = False

    # Render question page

    return render_template('question.html')

@app.route('/update-q')
def update_current_question():
    '''Route for updating questions and answers in session. The submit button of any question leads to this route.
    first answers are added to the session, then current question tracker is updated, then the current question number
    is checked for accuracy. If there are no more questions, user is redirected to the /save-results route'''

    # Answers array pulled from session
    answers = session['answers']

    # Handling answer saving for questions that allow a text input.
    # If text input wasn't allowed:
        # get the answers in plain text
        # store them in the answers list
    # If text input was allowed:
        # appened to the answers a dictionary containing the given answer as a key and text input as a value

    if not request.args.get('text_input'):
        for answer in request.args.keys():
            answers.append(answer)
    else:
        for answer in request.args.keys():
            if answer != 'text_input':
                answers.append({answer: request.args.get('text_input')})

    # Update session answers
    session['answers'] = answers

    # Update current question
    session['cur_question'] = session['cur_question'] + 1
    
    # Corrects current question number in case it was somehow changed
    if not bool(len(session['answers']) == session['cur_question']):
        len(session['answers']) == session['cur_question']

    # If the new current question number is in range (less than len of question list), move on to the next question
    if session['cur_question'] < session['cur_survey_len']:
        return redirect(f'/question/{session["cur_question"]}')
    # If current question is out of range, redirect to /save-results
    else:
        return redirect('/save-results')

@app.route('/save-results')
def save_results():
    '''Route to save results to session'''

    # complete_survey object is created with all the survey info saved from session

    complete_survey = {
            'id': random.randint(1000,2000),
            'title': session['cur_survey_title'],
            'instructions': session['instructions'],
            'questions': session['questions'],
            'answers': session['answers']
        }
    
    # Take out completed surveys array which was initialized in /surv-set and add new survey, resave to session

    completed_surveys = session['completed_surveys']
    completed_surveys.append(complete_survey)
 
    session['completed_surveys'] = completed_surveys

    # Redirect to thank you page

    return redirect('/thankyou')

@app.route('/thankyou')
def render_thanks():
    '''Render thankyou page'''
    survs = session['completed_surveys']
    completed_surveys.append(survs)
    session.clear()
    return render_template('thankyou.html')