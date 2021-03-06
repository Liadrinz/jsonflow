import re

from jsonflow.core import jf
from jsonflow import config

from bs4 import BeautifulSoup

config.max_workers = 4  # 线程数

def preprocess_item(html):
    data = {}
    soup = BeautifulSoup(html, 'lxml')
    basicInfoBox = soup.find('div', {'class': 'basic-info'})
    for dl in basicInfoBox.findAll('dl'):
        for k, v in zip(dl.findAll('dt'), dl.findAll('dd')):
            data[k.text] = v.text
    return data

@jf.thread(callback=lambda data : print(data))
@jf.src('https://baike.baidu.com/item/<name>', inherit_cookies=True)
@jf.flow(
    preprocess_item,
    lambda data: {re.sub('\s', '', k) : re.sub('\s', '', data[k]) for k in data}
)
def get_abstract(name):
    return jf.data

@jf.src(
    'http://localhost:8000/login',
    method='post',
    data = {
        'username': 'Liadrinz',
        'password': '123456'
    }
)
def login():
    return jf.data

@jf.src('http://localhost:8000/test_data', inherit_cookies=True)
def get_greet():
    return jf.data

def test_abstract():
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        get_abstract(name=keyword)

def test_greeting():
    data = get_greet()
    print(data)

if __name__ == '__main__':
    test_abstract()
    login()
    test_greeting()