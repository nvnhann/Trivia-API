import os
import random
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def pagination(req, questions):
    start = (req.args.get('page', 1, type=int) - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questionsp = [question.format() for question in questions]
    return questionsp[start:end]

def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        formatted_categories = {}
        for category in categories:
            formatted_categories[f'{category.id}'] = f'{category.type}'
        return jsonify({'success': True, 'categories': formatted_categories})

    @app.route('/questions')
    def get_questions():
        questions = Question.query.all()
        pagination_questions = pagination(request, questions)
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]
        return jsonify({'success': True, 'questions': pagination_questions, 'total_questions': len(questions), 'current_category': None, 'categories': formatted_categories})

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        try:
            question = Question(
                question=body.get('question', None),
                answer=body.get('answer', None),
                category=body.get('category', None),
                difficulty=body.get('difficulty', None)
            )
            question.insert()
            questions = Question.query.all()
            pagination_questions = pagination(request, questions)
            return jsonify({'success': True, 'created': question.id, 'questions': pagination_questions, 'total_questions': len(questions)})
        except:
            abort(500)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()
        if question is None:
            abort(404)
        try:
            question.delete()
            questions = Question.query.all()
            paginated_questions = pagination(request, questions)
            return jsonify({'success': True, 'deleted': question_id, 'questions': paginated_questions, 'total_questions': len(questions)})
        except:
            abort(500)

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        search_term = request.get_json('searchTerm')
        questions = Question.query.filter(Question.question.ilike(f'%{search_term["searchTerm"]}%')).all()
        if not len(questions):
            abort(404)
        pagination_questions = pagination(request, questions)
        return jsonify({'success': True, 'questions': pagination_questions, 'total_questions': len(questions)})

    @app.route('/categories/<category_type>/questions', methods=['GET'])
    def get_questions_by_category(category_type):
        questions = Question.query.filter(Question.category.ilike(category_type)).all()
        if not len(questions):
            abort(404)
        paginated_questions = pagination(request, questions)
        return jsonify({'success': True, 'questions': paginated_questions, 'total_questions': len(questions)})

    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():
        try:
            body = request.get_json()
            previous_questions = body.get('previous_questions', [])
            quiz_category = body.get('quiz_category', None)
            if quiz_category is None:
                abort(400)
            category_id = quiz_category.get('id', None)
            if category_id == 0:
                questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
            else:
                questions = Question.query.filter(Question.id.notin_(previous_questions), Question.category == category_id).all()
            if not questions:
                return jsonify({'success': True, 'question': None})
            question = random.choice(questions)
            return jsonify({'success': True, 'question': question.format()})
        except Exception:
            abort(500)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": 404, "message": "resource not found"}), 404
    
    @app.errorhandler(500)
    def unprocessable(error):
        return jsonify({"success": False, "error": 500, "message": "Internal server error"}), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"success": False, "error": 405, "message": "method not allowed"}), 405

    return app
