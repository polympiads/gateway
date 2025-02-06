import datetime
import logging
from threading import Thread
import threading
from typing import Callable

type UpdateMetricFunction = Callable

_logger = logging.getLogger(__name__)


class MetricThreadContext:
    def __init__(self, name: str, interval = datetime.timedelta(seconds=1)):
        self._registered_update_functions: list[UpdateMetricFunction] = []
        self._lock = threading.Lock()
        self._metric_thread = None
        self.interval: datetime.timedelta = interval
        self.name = name
    
    def register_update_function(self, function: UpdateMetricFunction | list[UpdateMetricFunction]):
        with self._lock:
            if callable(function):
                self._registered_update_functions.append(function)
            else:
                self._registered_update_functions.extend(function)

    def unregister_update_function(self, function: UpdateMetricFunction | list[UpdateMetricFunction]):
        with self._lock:
            if callable(function):
                try:
                    self._registered_update_functions.remove(function)
                except ValueError:
                    pass
            else:
                for func in function:
                    try:
                        self._registered_update_functions.remove(func)
                    except ValueError:
                        pass

    def clear_registered_functions(self):
        with self._lock:
            self._registered_update_functions.clear()

    def launch_thread(self):
        if self._metric_thread is None:
            self._metric_thread = _MetricThread(self)
            self._metric_thread.start()

    def stop_thread(self):
        if self._metric_thread is not None:
            self._metric_thread.stop()
            self._metric_thread = None

    def is_thread_running(self) -> bool:
        return self._metric_thread is not None


__default_context = MetricThreadContext("Default context")


def register_update_function(function: UpdateMetricFunction | list[UpdateMetricFunction]):
    __default_context.register_update_function(function)

def unregister_update_function(function: UpdateMetricFunction | list[UpdateMetricFunction]):
    __default_context.unregister_update_function(function)

def clear_registered_functions():
    __default_context.clear_registered_functions()

def launch_thread():
    __default_context.launch_thread()

def stop_thread():
    __default_context.stop_thread()

def is_thread_running() -> bool:
    return __default_context.is_thread_running()

def default_interval() -> datetime.timedelta:
    return __default_context.interval

class _MetricThread(Thread):
    def __init__(self, context: MetricThreadContext):
        self.context = context
        self.should_stop = threading.Event()

        super().__init__(target=self.threaded_function, daemon=True)

    def threaded_function(self):
        _logger.info('Metric thread has been launched.')

        while not self.should_stop.is_set():
            self.should_stop.wait(self.context.interval.total_seconds())
            _logger.info('Updating metrics...')

            with self.context._lock:
                for update_function in self.context._registered_update_functions:
                    update_function()
    
    def stop(self):
        _logger.info("Stopping metric thread.")
        self.should_stop.set()

        self.join()
