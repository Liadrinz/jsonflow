import re
import requests
import jsonflow.config as config

from xml.sax.saxutils import unescape


class _Container:
    def __init__(self):
        self.data = None
        self._cookies = None
        self._session = requests.Session()
    
    def register(self, func):
        exec(f'self.{func.__name__} = func', globals(), locals())

    def src(self, url, data=None, method='get', mode='t', coding='utf-8', inherit_cookies=False, new_session=False):
        def wrapper(func):
            def inner_wrapper(*args, **kwargs):
                if new_session:
                    self._session = requests.Session()
                _url, _coding, _data = self._replace_all_params(kwargs, url, coding, data)
                if method.lower() == 'post':
                    resp = self._session.post(_url, headers=config.headers, data=_data, cookies=self._cookies if inherit_cookies else None)
                elif method.lower() == 'get':
                    resp = self._session.get(
                        _url + (f'?{"&".join([k + "=" + _data[k] for k in _data])}' if _data is not None else ''),
                        headers=config.headers, cookies=self._cookies if inherit_cookies else None)
                if not inherit_cookies:
                    self._cookies = resp.cookies
                self.data = resp.content
                if mode == 't':
                    self.data = self.data.decode(_coding)
                return func(*args, **kwargs)
            inner_wrapper.__name__ = func.__name__
            return inner_wrapper

        return wrapper

    def flow(self, *handlers):
        def wrapper(func):
            def inner_wrapper(*args, **kwargs):
                self.data = self._handle(self.data, *handlers, **kwargs)
                return func(*args, **kwargs)
            inner_wrapper.__name__ = func.__name__
            return inner_wrapper

        return wrapper

    def _handle(self, data, *handlers, **kwargs):
        for handler in handlers:
            if type(handler) == list:
                result = []
                for single in handler:
                    result.append(self._handle(data, single))
                data = result
            elif type(handler) == dict:
                result = {}
                for key in handler:
                    single = handler[key]
                    result_key, = self._replace_all_params(kwargs, self._handle(data, key))
                    result[result_key] = self._handle(
                        data, single)
                data = result
            elif callable(handler):
                data = handler(data)
            else:
                return handler
        return data

    def _replace_param(self, s, **kwargs):
        if type(s) == str:
            non_match = True
            command = s
            for key in kwargs:
                match = re.match(f'.*?<(.*?{key}.*?)>.*', command)
                if match is None: continue
                non_match = False
                command = match.groups()[0]
                command = command.replace(key, f'kwargs["{key}"]')
                command = unescape(command)
                command = f'<{command}>'
            if not non_match:
                command = command[1:-1]
                repl = str(eval(command, globals(), locals()))
                s = re.sub(f'<.*?>', repl, s)
            return s
        elif type(s) == list:
            result = []
            for item in s:
                result.append(self._replace_param(item, **kwargs))
            return result
        elif type(s) == dict:
            result = {}
            for key in s:
                result[self._replace_param(key, **kwargs)] = self._replace_param(s[key], **kwargs)
            return result
                

    def _replace_all_params(self, to_repl, *args):
        new_args = []
        for arg in args:
            new_args.append(self._replace_param(arg, **to_repl))
        return new_args

jflow = _Container()
