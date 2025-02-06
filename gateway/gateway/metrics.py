import datetime
import logging
from threading import Thread
import threading
from typing import Callable

interval: datetime.timedelta = datetime.timedelta(seconds=2)

type UpdateMetricFunction = Callable

_logger = logging.getLogger(__name__)

_registered_update_functions: list[UpdateMetricFunction] = []
_lock = threading.Lock()
__metric_thread = None

def register_update_function(function: UpdateMetricFunction | list[UpdateMetricFunction]):
    global _registered_update_functions

    with _lock:
        if callable(function):
            _registered_update_functions.append(function)
        else:
            _registered_update_functions.extend(function)
    

def unregister_update_function(function: UpdateMetricFunction | list[UpdateMetricFunction]):
    global _registered_update_functions

    with _lock:
        if callable(function):
            try:
                _registered_update_functions.remove(function)
            except ValueError:
                pass
        else:
            for func in function:
                try:
                    _registered_update_functions.remove(func)
                except ValueError:
                    pass


def clear_registered_functions():
    global _registered_update_functions
    
    with _lock:
        _registered_update_functions.clear()


class __MetricThread(Thread):
    def __init__(self):
        self._should_stop = threading.Event()

        super().__init__(target=self.threaded_function)

    def threaded_function(self):
        _logger.info('Metric thread has been launched.')

        while not self._should_stop.is_set():
            self._should_stop.wait(interval.total_seconds())
            _logger.info('Updating metrics...')

            with _lock:
                for update_function in _registered_update_functions:
                    update_function()
    
    def stop(self):
        _logger.info("Stopping metric thread.")
        self._should_stop.set()

        self.join()

def launch_thread():
    global __metric_thread
    
    if __metric_thread is None:
        __metric_thread = __MetricThread()
        __metric_thread.start()

def stop_thread():
    global __metric_thread
    
    if __metric_thread is not None:
        __metric_thread.stop()
        __metric_thread = None

def is_thread_running() -> bool:
    return __metric_thread is not None
