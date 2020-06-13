import re
import requests
import jsonflow.config as config

from xml.sax.saxutils import unescape


class _Container:
    def __init__(self):
        self.data = None
        self._cookies = None
    
    def src(self, url, data=None, method='get', mode='t', coding='utf-8', inherit_cookies=False):
        def wrapper(func):
            def inner_wrapper(*args, **kwargs):
                _url, _coding = self._replace_all_params(kwargs, url, coding)
                if method.lower() == 'post':
                    resp = requests.post(_url, headers=config.headers, data=data, cookies=self._cookies if inherit_cookies else None)
                elif method.lower() == 'get':
                    resp = requests.get(
                        _url + (f'?{"&".join([k + "=" + data[k] for k in data])}' if data is not None else ''),
                        headers=config.headers, cookies=self._cookies if inherit_cookies else None)
                if not inherit_cookies:
                    self._cookies = resp.cookies
                self.data = resp.content
                if mode == 't':
                    self.data = self.data.decode(_coding)
                return func(*args, **kwargs)
            # inner_wrapper.__name__ = func.__name__
            return inner_wrapper

        return wrapper

    def flow(self, *handlers):
        def wrapper(func):
            def inner_wrapper(*args, **kwargs):
                self.data = self._handle(self.data, *handlers, **kwargs)
                return func(*args, **kwargs)
            # inner_wrapper.__name__ = func.__name__
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
        for key in kwargs:
            match = re.match(f'.*?<(.*?{key}.*?)>.*', s)
            if match is None: continue
            command = match.groups()[0]
            command = command.replace(key, f'kwargs["{key}"]')
            command = unescape(command)
            repl = str(eval(command, globals(), locals()))
            s = re.sub(f'<.*?{key}.*?>', repl, s)
        return s

    def _replace_all_params(self, to_repl, *args):
        new_args = []
        for arg in args:
            if type(arg) == str:
                new_args.append(self._replace_param(arg, **to_repl))
        return new_args

jflow = _Container()
