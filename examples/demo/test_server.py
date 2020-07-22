import json
from flask import Flask, request, make_response

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    data = request.form.to_dict()
    resp = make_response("success")
    resp.set_cookie('username', data['username'])
    resp.set_cookie('password', data['password'])
    return resp

@app.route('/test_data')
def test_data():
    cookies = request.cookies
    if cookies.get('username') == 'Liadrinz' and cookies.get('password') == '123456':
        return 'Hello, Liadrinz!'
    return 'Fuck off!'

app.run('0.0.0.0', 8000, debug=True)