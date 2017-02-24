from flask import jsonify, request
from functools import wraps
from schema import SchemaError
from werkzeug.exceptions import BadRequest


def _error(msg):
    return {
        'status': 'error',
        'data': msg
    }


def api_response(schema=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if schema:
                try:
                    json = request.get_json()
                except BadRequest:
                    return jsonify(
                        _error('please provide valid json payload')), 400

                if json is None:
                    return (jsonify(_error(
                        'content-type header should be application/json')),
                        400)

                try:
                    validated = schema.validate(json)
                    res = f(validated, *args, **kwargs)
                except SchemaError as ex:
                    return jsonify(_error(ex.message)), 400
            else:
                res = f(*args, **kwargs)
            return jsonify({
                'status': 'success',
                'data': res
            })
        return wrapper
    return decorator
