import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def questions_pagination(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  if current_questions == 0:
    abort(404)
  return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'/': {'origins': '*'}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories')
  def get_categories():
    get_categories = Category.query.all()

    if (len(get_categories) == 0):
      abort(404)

    sorted_categories = {}
    for category in get_categories:
      sorted_categories[category.id] = category.type

    return jsonify({
      'success': True,
      'categories': sorted_categories
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def get_questions():
    selection = Question.query.order_by(Question.id).all()
    get_categories = Category.query.all()

    questions_with_pagination = questions_pagination(request, selection)

    sorted_categories = {}
    for category in get_categories:
      sorted_categories[category.id] = category.type

    return jsonify({
      'success': True,
      'questions': questions_with_pagination,
      'total_questions': len(selection),
      'current_category': None,
      'categories': sorted_categories
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(422)

      question.delete()

      return jsonify({
        'success': True,
        'deleted_question': question_id,
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    question = body.get('question') if body.get('question') else abort(422)
    answer = body.get('answer') if body.get('answer') else abort(422)
    category = body.get('category') if body.get('category') else abort(422)
    difficulty = body.get('difficulty') if body.get('difficulty') else abort(422)

    try:
      question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
      question.insert()

      return jsonify({
        'success': True,
        'new_question': question.id,
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search = body.get('searchTerm', None)
    if search:
      results = Question.query.filter(Question.question.ilike('%{}%'.format(search))).all()

      return jsonify({
        'success': True,
        'questions': [question.format() for question in results],
        'total_questions': len(results),
        'current_category': None
      })
    abort(404)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    try:
      questions = Question.query.filter(Question.category == str(category_id)).all()

      sorted_questions = []
      for question in questions:
        sorted_questions.append(question.format())

      return jsonify({
        'success': True,
        'current_category': category_id,
        'questions': sorted_questions,
        'total_questions': len(questions),
      })
    except:
      abort(404)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def play_quiz():

    try:

      body = request.get_json()

      category = body.get('quiz_category')
      previous_questions = body.get('previous_questions')

      if category is None or previous_questions is None:
        abort(422)

      if category['id'] == 0:
        questions = Question.query.all()
        sorted_questions = [question for question in questions if question.id not in previous_questions]
      else:
        selectedQuestions = Question.query.filter_by(category=category['id']).all()
        sorted_questions = [question for question in selectedQuestions if question.id not in previous_questions]

      if len(sorted_questions) <= 0:
        random_question = None
      else:
        random.shuffle(sorted_questions)
        random_question = sorted_questions[0].format()

      return jsonify({
        'success': True,
        'question': random_question
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def page_not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "Page or resource not found"
    }), 404

  @app.errorhandler(422)
  def request_cannot_be_processed(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "Request entity cannot be processed"
    }), 422

  @app.errorhandler(400)
  def bad_request_sent(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request sent, please review your request"
    }), 400

  return app

