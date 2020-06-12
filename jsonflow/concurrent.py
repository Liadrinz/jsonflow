import traceback
import time, threading
import jsonflow.config as config
from concurrent.futures import ThreadPoolExecutor

class _Concurrent:
    def __init__(self):
        self.pool = ThreadPoolExecutor(max_workers=config.max_workers, thread_name_prefix='jsonflow_concurrent_')
    
    def thread(self, callback=None):
        def wrapper(func):
            def inner_wrapper(*args, **kwargs):
                def task():
                    try:
                        data = func(*args, **kwargs)
                        if callback is not None:
                            callback(data)
                    except Exception as e:
                        traceback.print_exc()
                self.pool.submit(task)
            return inner_wrapper
        return wrapper

concurrent = _Concurrent()