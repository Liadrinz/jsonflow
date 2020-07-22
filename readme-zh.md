# jsonflow

基于JSON数据流和装饰器的爬虫框架([See English Version](readme.md))

## 使用之前

```shell
pip install -r requirements.txt
```

## 入门

### @src资源获取

- 获取单一页面

```py
from jsonflow.core import jf

@jf.src('https://en.wikipedia.org/wiki/wiki/python')
def download_page():
    with open('python.html', 'wb') as f:
        f.write(jf.data.encode('utf-8'))  # use get_data to fetch data from jsonflow container

if __name__ == '__main__':
     download_page()
```

- 使用参数

```py
from jsonflow.core import jf

# Use the parameter "name" of function "download_page" as the url suffix
@jf.src('https://en.wikipedia.org/wiki/<name>')
def download_page(name):
    with open(name + '.html', 'wb') as f:
        f.write(jf.data.encode('utf-8'))

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        download_page(name=keyword)  # should be keyword arguments here
```

### @flow数据流

```py
from jsonflow.core import jf

from bs4 import BeautifulSoup

@jf.src('https://en.wikipedia.org/wiki/<name>')
@jf.flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text)
def get_title(name):
    return jf.data

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        title = get_title(name=keyword)
        print(title)
        '''
        C++ - Wikipedia
        Python - Wikipedia
        Java - Wikipedia
        C - Wikipedia
        JavaScript - Wikipedia
        '''
```

### 数据流高级用法

- 列表

```py
from hashlib import md5

from jsonflow.core import jf

from bs4 import BeautifulSoup

# get md5
def digest(s):
    return md5(s.encode()).hexdigest()

@jf.src('https://en.wikipedia.org/wiki/<name>')
@jf.flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text,
    [len, digest])
# equals to lambda title : [len(title), digest(title)]
# also equals to [lambda title : len(title), lambda title : digest(title)]
def get_title_length_and_md5(name):
    return jf.data

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        data = get_title_length_and_md5(name=keyword)
        print(data)
        '''
        [15, 'b47f94ac21757616e99c4256320236c3']
        ...
        '''
```

- 字典

```py
@jf.src('https://en.wikipedia.org/wiki/<name>')
@jf.flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text,
    {'length': len, 'md5': digest})
# equals to lambda title : {'length': len(title), 'md5': digest(title)}
# also equals to {'length': lambda title : len(title), 'md5': lambda title : digest(title)}
def get_title_length_and_md5(name):
    return jf.data

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        data = get_title_length_and_md5(name=keyword)
        print(data)
        '''
        {'length': 15, 'md5': 'b47f94ac21757616e99c4256320236c3'}
        ...
        '''
```

- 嵌套

```py
@jf.src('https://en.wikipedia.org/wiki/<name>')
@jf.flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text,
    {'info': [len, digest]})
def get_title_length_and_md5(name):
    return jf.data

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        data = get_title_length_and_md5(name=keyword)
        print(data)
        '''
        {'info': [15, 'b47f94ac21757616e99c4256320236c3']}
        ...
        '''
```

- 使用参数

```py
@jf.src('https://en.wikipedia.org/wiki/<name>')
@jf.flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text,
    {'<name>': [len, digest]})  # 以参数name作为key
def get_title_length_and_md5(name):
    return jf.data

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        data = get_title_length_and_md5(name=keyword)
        print(data)
        '''
        {'c++': [15, 'b47f94ac21757616e99c4256320236c3']}
        ...
        '''
```

### 模板

模板语句书写在尖括号中, 如`<name>`. 模板语句中除了可以访问所装饰函数的参数外, 还可以直接使用python表达式, 同时支持外部注册变量以供模板访问.

#### Python表达式

```py
@jf.src('https://en.wikipedia.org/wiki/<name>')
@jf.flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text,
    {'<name + "-" + str(len(name))>': [len, digest]})
def get_title_length_and_md5(name):
    return jf.data

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        data = get_title_length_and_md5(name=keyword)
        print(data)
        '''
        {'c++-3': [15, 'b47f94ac21757616e99c4256320236c3']}
        ...
        '''
```

#### 转义

在模板的表达式中使用大于号和小于号时需要进行转义

```py
@jf.src('https://en.wikipedia.org/wiki/<name>')
@jf.flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text,
    {'<name + "-" + str(len(name) &lt; 3)>': [len, digest]})  # escape
def get_title_length_and_md5(name):
    return jf.data

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        data = get_title_length_and_md5(name=keyword)
        print(data)
        '''
        {'c++-False': [15, 'b47f94ac21757616e99c4256320236c3']}
        ...
        '''
```

#### 使用外部变量

```py
from jsonflow.core import jf

# Register variables
jf.prefix = 'lang-'
jf.suffix = '-info'

@jf.src('https://en.wikipedia.org/wiki/<name>')
@jf.flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text,
    {'<self.prefix + name + self.suffix>': [len, digest]})  # access through "self"
def get_title_length_and_md5(name):
    return jf.data

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        data = get_title_length_and_md5(name=keyword)
        print(data)
        '''
        {'lang-c++-info': [15, 'b47f94ac21757616e99c4256320236c3']}
        ...
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
@jf.src(
    'http://localhost:8000/login',
    method='post',
    data = {
        'username': 'Liadrinz',
        'password': '123456'
    }
)
@jf.src('http://localhost:8000/test_data', inherit_cookies=True)
def get_greet():
    return jf.data
```

- 就近原则: inherit_cookies为True的@src向上继承离它最近的inherit_cookies为False的@src的cookie

```py
@jf.src(
    'http://localhost:8000/login',
    method='post',
    data = {
        'username': 'Liadrinz',
        'password': '123456'
    }
)
@jf.src('http://localhost:8000/test_data', inherit_cookies=True)
@jf.src('http://localhost:8000/test_data', inherit_cookies=True)
@jf.src(
    'http://localhost:8000/login',
    method='post',
    data = {
        'username': 'StevenZ',
        'password': '123456'
    }
)
@jf.src('http://localhost:8000/test_data', inherit_cookies=True)
@jf.src('http://localhost:8000/test_data', inherit_cookies=True)
def get_greet():
    return jf.data
```

- 登录示例

```py
@jf.src(
    'http://localhost:8000/login',
    method='post',
    data = {
        'username': 'Liadrinz',
        'password': '123456'
    }
)
def login():
    return get_data()

@jf.src('http://localhost:8000/test_data', inherit_cookies=True)
def get_greet():
    return get_data()

if __name__ == '__main__':
    login()
    data = get_greet()
    print(data)
```

### @thread多线程

```py
from jsonflow.core import jf

config.max_workers = 4  # max number of workers

# register external variables
jflow.prefix = 'lang-'
jflow.suffix = '-info'

@jf.thread(callback=lambda data : print(data))  # access data through callbacks
@jf.src('https://en.wikipedia.org/wiki/<name>')
@jf.flow(
    lambda data : BeautifulSoup(data, 'lxml'),
    lambda soup : soup.title.text,
    {'<self.prefix + name + self.suffix>': [len, digest]})  # access through "self"
def get_title_length_and_md5(name):
    return jf.data

if __name__ == '__main__':
    for keyword in ['c++', 'python', 'java', 'c#', 'javascript']:
        get_title_length_and_md5(name=keyword)
        '''
        ...
        {'lang-c++-info': [15, 'b47f94ac21757616e99c4256320236c3']}
        ...
        '''
    jf.wait()  # wait for the thread pool
```
