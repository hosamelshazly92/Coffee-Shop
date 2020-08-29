import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

import psycopg2

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO_DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO_DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
    drinks is the list of drinks or appropriate status code indicating reason
    for failure
'''


@app.route('/drinks')
def get_drinks():

    drink = Drink.query.order_by(Drink.id).all()
    drinks = [i.short() for i in drink]

    return jsonify({
        "success": True,
        "drinks": drinks
    })

'''
@TODO_DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks or appropriate status code indicating
    reason for failure
'''


@app.route('/drinks_detail')
@requires_auth(['get:drinks_detail'])
def get_drinks_detail(token):

    drink = Drink.query.order_by(Drink.id).all()
    drinks = [i.long() for i in drink]

    return jsonify({
        "success": True,
        "drinks": drinks
    })

'''
@TODO_DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the newly created drink or appropriate
    status code indicating reason for failure
'''


@app.route('/add', methods=['POST'])
@requires_auth(['post:drinks'])
def add_drinks(token):

    try:
        body = request.get_json()

        title = body.get('title', None)
        get_recipe = body.get('recipe', None)
        recipe = json.dumps(get_recipe)

        drink = Drink(title=title, recipe=recipe)

        drink.insert()

        return jsonify({
            "success": True,
            "drinks": drink.title
        })

    except Exception:
        abort(422)

'''
@TODO_DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the updated drink or appropriate status code
    indicating reason for failure
'''


@app.route('/edit/<int:drink_id>', methods=['PATCH'])
@requires_auth(['patch:drinks'])
def edit_drinks(token, drink_id):

    try:
        body = request.get_json()

        title = body.get('title', None)
        get_recipe = body.get('recipe', None)
        recipe = json.dumps(get_recipe)

        drink = Drink.query.get(drink_id)

        if drink is None:
            abort(404)

        drink.title = title
        drink.recipe = recipe

        drink.insert()

        return jsonify({
            "success": True,
            "drinks": title
        })

    except Exception:
        abort(422)

'''
@TODO_DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id
    is the id of the deleted record or appropriate status code indicating
    reason for failure
'''


@app.route('/delete/<int:drink_id>', methods=['DELETE'])
@requires_auth(['delete:drinks'])
def delete_drinks(token, drink_id):

    drink = Drink.query.get(drink_id)

    if drink is None:
        abort(404)

    drink.delete()

    try:

        return jsonify({
            "success": True,
            "delete": drink_id
        })

    except Exception:
        abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

'''
@TODO_DONE implement error handlers using the @app.errorhandler(error)
decorator each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO_DONE implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': "resource not found"
    }), 404

'''
@TODO_DONE implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': "forbidden"
    }), 403


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': "unauthorized"
    }), 401


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': "bad request"
    }), 400
