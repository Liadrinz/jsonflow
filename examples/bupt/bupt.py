import re
import json

from base64 import b64encode

from jsonflow.core import jf

from bs4 import BeautifulSoup
from flask import Flask, request, render_template, abort

@jf.register
def parse_info(username, password):
    return (b64encode(username.encode()) + b'%%%' + b64encode(password.encode())).decode()

def trim(s):
    return re.sub(r'\s', '', s)

def avg(courses):
    score_total = 0
    point_total = 0
    for course in courses:
        if course.get('课程属性', '') == '任选':
            continue
        try:
            score = float(course.get('成绩', 0))
            point = float(course.get('学分', 0))
        except ValueError:
            continue
        score_total += score * point
        point_total += point
    return score_total / point_total

app = Flask(__name__)

@jf.src(
    url='http://jwgl.bupt.edu.cn/jsxsd/xk/LoginToXk',
    method='post',
    data={
        'userAccount': '<username>',
        'userPassword': '',
        'encoded': '<self.parse_info(username, password)>'
    }
)
@jf.src('http://jwgl.bupt.edu.cn/jsxsd/kscj/cjcx_list')
@jf.flow(
    lambda raw : BeautifulSoup(raw, 'lxml'),
    lambda soup : soup.find('table'),
    [lambda table : [trim(th.text) for th in table.find_all('th')], lambda table : table.find_all('tr')],
    [lambda result: result[0], lambda result : [[trim(td.text) for td in row.find_all('td')] for row in result[1]]]
)
def get_avg(username, password):
    courses = []
    headers, rows = jf.data
    for row in rows:
        courses.append(dict(zip(headers, row)))
    return avg(courses)

@app.route('/', methods=['GET', 'POST'])
def average():
    if request.method == 'GET':
        return render_template('index.html', info='')
    username = request.form.get('username')
    password = request.form.get('password')
    try:
        score = get_avg(username=username, password=password)
        return render_template('index.html', info=f'加权平均分：{score}')
    except:
        return render_template('index.html', info='学号或密码错误，或者是你没挂VPN')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, debug=True)