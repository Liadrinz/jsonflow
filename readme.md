# jsonflow

基于JSON数据流的爬虫框架

## 使用之前

```shell
pip install -r requirements.txt
```

## 入门

### @src资源获取

- 获取单一页面

```py
from jsonflow.decorators import src
from jsonflow.access import get_data

@src('https://baike.baidu.com/item/python')
def download_page():
    with open('python.html', 'wb') as f:
        f.write(get_data().encode('utf-8'))  # 使用get_data从jsonflow容器中获取数据

if __name__ == '__main__':
     download_page()
```

- 使用参数

```py
from jsonflow.decorators import src
from jsonflow.access import get_data

# 直接download_page的参数name作为url后缀
@src('https://baike.baidu.com/item/<name>')
def download_page(name):
    with open(name + '.html', 'wb') as f:
        f.write(get_data().encode('utf-8'))

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        download_page(name=keyword)  # 必须使用关键字传参
```

### @flow数据流

```py
from jsonflow.decorators import src
from jsonflow.access import get_data

from bs4 import BeautifulSoup

@src('https://baike.baidu.com/item/<name>')
@flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text)
def get_title(name):
    return get_data()

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        title = get_title(name=keyword)
        print(title)
        '''
        C++_百度百科
        Python（计算机程序设计语言）_百度百科
        Java（计算机编程语言）_百度百科
        c语言_百度百科
        javascript_百度百科
        '''
```

### 数据流高级用法

- 列表

```py
from hashlib import md5

from jsonflow.decorators import src
from jsonflow.access import get_data

from bs4 import BeautifulSoup

# 获取md5
def digest(s):
    return md5(s.encode()).hexdigest()

@src('https://baike.baidu.com/item/<name>')
@flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text,
    [len, digest])
# 等价于lambda title : [len(title), digest(title)]
# 也等价于[lambda title : len(title), lambda title : digest(title)]
def get_title_length_and_md5(name):
    return get_data()

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        data = get_title_length_and_md5(name=keyword)
        print(data)
        '''
        [8, '93f7521b56af338defb8c37d0b35ed74']
        [22, '06155ef01665f6b0811fe98b6951e0b5']
        [18, 'dd5acc52d482c0ea46bd58c829a86061']
        [8, '5221cb883f355ef52b834e4679f2219b']
        [15, '7b81c50dde0675dced19ebd0e309b84a']
        '''
```

- 字典

```py
@src('https://baike.baidu.com/item/<name>')
@flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text,
    {'length': len, 'md5': digest})
# 等价于lambda title : {'length': len(title), 'md5': digest(title)}
# 也等价于{'length': lambda title : len(title), 'md5': lambda title : digest(title)}
def get_title_length_and_md5(name):
    return get_data()

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        data = get_title_length_and_md5(name=keyword)
        print(data)
        '''
        {'length': 8, 'md5': '93f7521b56af338defb8c37d0b35ed74'}
        {'length': 22, 'md5': '06155ef01665f6b0811fe98b6951e0b5'}
        {'length': 18, 'md5': 'dd5acc52d482c0ea46bd58c829a86061'}
        {'length': 8, 'md5': '5221cb883f355ef52b834e4679f2219b'}
        {'length': 15, 'md5': '7b81c50dde0675dced19ebd0e309b84a'}
        '''
```

- 嵌套

```py
@src('https://baike.baidu.com/item/<name>')
@flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text,
    {'info': [len, digest]})
def get_title_length_and_md5(name):
    return get_data()

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        data = get_title_length_and_md5(name=keyword)
        print(data)
        '''
        {'info': [8, '93f7521b56af338defb8c37d0b35ed74']}
        {'info': [22, '06155ef01665f6b0811fe98b6951e0b5']}
        {'info': [18, 'dd5acc52d482c0ea46bd58c829a86061']}
        {'info': [8, '5221cb883f355ef52b834e4679f2219b']}
        {'info': [15, '7b81c50dde0675dced19ebd0e309b84a']}
        '''
```

- 使用参数

```py
@src('https://baike.baidu.com/item/<name>')
@flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text,
    {'<name>': [len, digest]})  # 以参数name作为key
def get_title_length_and_md5(name):
    return get_data()

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        data = get_title_length_and_md5(name=keyword)
        print(data)
        '''
        {'c++': [8, '93f7521b56af338defb8c37d0b35ed74']}
        {'python': [22, '06155ef01665f6b0811fe98b6951e0b5']}
        {'java': [18, 'dd5acc52d482c0ea46bd58c829a86061']}
        {'c#': [8, '5221cb883f355ef52b834e4679f2219b']}
        {'javascript': [15, '7b81c50dde0675dced19ebd0e309b84a']}
        '''
```

### 模板

模板语句书写在尖括号中, 如`<name>`. 模板语句中除了可以访问所装饰函数的参数外, 还可以直接使用python表达式, 同时支持外部注册变量以供模板访问.

#### Python表达式

```py
@src('https://baike.baidu.com/item/<name>')
@flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text,
    {'<name + "-" + str(len(name))>': [len, digest]})
def get_title_length_and_md5(name):
    return get_data()

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        data = get_title_length_and_md5(name=keyword)
        print(data)
        '''
        {'c++-3': [8, '93f7521b56af338defb8c37d0b35ed74']}
        {'python-6': [22, '06155ef01665f6b0811fe98b6951e0b5']}
        {'java-4': [18, 'dd5acc52d482c0ea46bd58c829a86061']}
        {'c#-2': [8, '5221cb883f355ef52b834e4679f2219b']}
        {'javascript-10': [15, '7b81c50dde0675dced19ebd0e309b84a']}
        '''
```

#### 转义

在模板的表达式中使用大于号和小于号时需要进行转义

```py
@src('https://baike.baidu.com/item/<name>')
@flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text,
    {'<name + "-" + str(len(name) &lt; 3)>': [len, digest]})  # 转义
def get_title_length_and_md5(name):
    return get_data()

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        data = get_title_length_and_md5(name=keyword)
        print(data)
        '''
        {'c++-False': [8, '93f7521b56af338defb8c37d0b35ed74']}
        {'python-False': [22, '06155ef01665f6b0811fe98b6951e0b5']}
        {'java-False': [18, 'dd5acc52d482c0ea46bd58c829a86061']}
        {'c#-True': [8, '5221cb883f355ef52b834e4679f2219b']}
        {'javascript-False': [15, '7b81c50dde0675dced19ebd0e309b84a']}
        '''
```

#### 使用外部变量

```py
from jsonflow.core import jflow

# 注册变量
jflow.prefix = 'lang-'
jflow.suffix = '-info'

@src('https://baike.baidu.com/item/<name>')
@flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text,
    {'<self.prefix + name + self.suffix>': [len, digest]})  # 通过self访问
def get_title_length_and_md5(name):
    return get_data()

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        data = get_title_length_and_md5(name=keyword)
        print(data)
        '''
        {'lang-c++-info': [8, '93f7521b56af338defb8c37d0b35ed74']}
        {'lang-python-info': [22, '06155ef01665f6b0811fe98b6951e0b5']}
        {'lang-java-info': [18, 'dd5acc52d482c0ea46bd58c829a86061']}
        {'lang-c#-info': [8, '5221cb883f355ef52b834e4679f2219b']}
        {'lang-javascript-info': [15, '7b81c50dde0675dced19ebd0e309b84a']}
        '''
```

### Cookie继承

本节可使用test_server.py提供的测试服务器来进行测试

```shell
pip install flask  # 若已安装requirements.txt则省略此步
python test_server.py
```

- 继承上层src的响应cookie作为下层src的请求cookie

```py
@src(
    'http://localhost:8000/login',
    method='post',
    data = {
        'username': 'Liadrinz',
        'password': '123456'
    }
)
@src('http://localhost:8000/test_data', inherit_cookies=True)
def get_greet():
    return get_data()
```

- 就近原则: inherit_cookies为True的@src向上继承离它最近的inherit_cookies为False的@src的cookie

```py
@src(
    'http://localhost:8000/login',
    method='post',
    data = {
        'username': 'Liadrinz',
        'password': '123456'
    }
)
@src('http://localhost:8000/test_data', inherit_cookies=True)
@src('http://localhost:8000/test_data', inherit_cookies=True)
@src(
    'http://localhost:8000/login',
    method='post',
    data = {
        'username': 'StevenZ',
        'password': '123456'
    }
)
@src('http://localhost:8000/test_data', inherit_cookies=True)
@src('http://localhost:8000/test_data', inherit_cookies=True)
def get_greet():
    return get_data()
```

- 登录示例

```py
@src(
    'http://localhost:8000/login',
    method='post',
    data = {
        'username': 'Liadrinz',
        'password': '123456'
    }
)
def login():
    return get_data()

@src('http://localhost:8000/test_data', inherit_cookies=True)
def get_greet():
    return get_data()

if __name__ == '__main__':
    login()
    data = get_greet()
    print(data)
```

### @thread多线程

```py
from jsonflow.decorators import src, flow, thread
from jsonflow import config

config.max_workers = 4  # 线程数

# 注册变量
jflow.prefix = 'lang-'
jflow.suffix = '-info'

@thread(callback=lambda data : print(data))  # 通过回调获取数据
@src('https://baike.baidu.com/item/<name>')
@flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text,
    {'<self.prefix + name + self.suffix>': [len, digest]})  # 通过self访问
def get_title_length_and_md5(name):
    return get_data()

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        get_title_length_and_md5(name=keyword)
        '''
        {'lang-javascript-info': [15, '7b81c50dde0675dced19ebd0e309b84a']}
        {'lang-c++-info': [8, '93f7521b56af338defb8c37d0b35ed74']}
        {'lang-c#-info': [8, '5221cb883f355ef52b834e4679f2219b']}
        {'lang-java-info': [18, 'dd5acc52d482c0ea46bd58c829a86061']}
        {'lang-python-info': [22, '06155ef01665f6b0811fe98b6951e0b5']}
        '''
```
