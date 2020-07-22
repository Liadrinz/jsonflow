# jsonflow

A Crawling Framework Based on Data Flow and Decorators([查看中文版](readme-zh.md))

## Before Use

```shell
pip install -r requirements.txt
```

## Get Started

### @src: Fetch Resources

- Fetch a single page

```py
from jsonflow.core import jf

@jf.src('https://en.wikipedia.org/wiki/wiki/python')
def download_page():
    with open('python.html', 'wb') as f:
        f.write(jf.data.encode('utf-8'))  # use get_data to fetch data from jsonflow container

if __name__ == '__main__':
     download_page()
```

- Use parameters

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

### @flow: The Data Flow

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

### @flow: High Level Usage

- list

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

- dict

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

- nesting

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

- use parameters

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

### Template

The template statement writes between the angle brackets, for example `<name>`, which is able to access all parameters of the decorated function and registered external variables, as well as use python expressions directly.

#### Python Expression

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

#### Escape

The less-than and greater-than symbol should be escaped in xml/html style

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

#### Register External Variables

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

### Cookie Inheritence

In this section, you can use `test_server.py` as a test service in order to learn how to use cookie inheritence.

```shell
pip install flask
python test_server.py
```

- The response cookie of the upper layer @src is inherited by the lower ones as their request cookies

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

- Nearby Principle: the @src decorators whose inherit_cookies equals True inherit from the nearest @src whose inherit_cookies equals False

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

- Login Demo

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

### @thread: Multithreading

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
