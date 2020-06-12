from hashlib import md5

from jsonflow.decorators import src, flow, thread
from jsonflow.access import get_data
from jsonflow.core import jflow
from jsonflow import config

from bs4 import BeautifulSoup

config.max_workers = 4  # 线程数

# 注册变量
jflow.prefix = 'lang-'
jflow.suffix = '-info'

# 获取md5
def digest(s):
    return md5(s.encode()).hexdigest()

@thread(callback=lambda data : print(data))  # 通过回调获取数据
@src('https://baike.baidu.com/item/<name>')
@flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text,
    {'<self.prefix + name + self.suffix>': [len, digest]})  # 通过self访问注册的变量, 通过名称访问参数
def get_title_length_and_md5(name):
    return get_data()

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        get_title_length_and_md5(name=keyword)