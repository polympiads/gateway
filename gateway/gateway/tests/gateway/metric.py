import datetime
import threading
import time
from django.test import TestCase

from gateway import metrics


def metrics_reset_and_stop_thread():
    metrics.stop_thread()
    metrics.clear_registered_functions()


class MetricThreadTestCase(TestCase):
    def setUp(self):
        metrics.interval = datetime.timedelta(seconds=0.25)

    def test_function_registered_is_actually_run(self):
        metrics_reset_and_stop_thread()
        metrics.launch_thread()
        
        ran = threading.Event()
        
        def test_function():
            nonlocal ran
            ran.set()

        metrics.register_update_function(test_function)

        self.assertTrue(ran.wait(metrics.interval.total_seconds() * 1.5))

    def test_function_register_multiple_functions(self):
        metrics_reset_and_stop_thread()
        metrics.launch_thread()
        
        ran1 = threading.Event()
        def test_function1():
            nonlocal ran1
            ran1.set()

        ran2 = threading.Event()
        def test_function2():
            nonlocal ran2
            ran2.set()

        metrics.register_update_function([test_function1, test_function2])

        self.assertTrue(ran1.wait(metrics.interval.total_seconds() * 1.5))
        self.assertTrue(ran2.wait(metrics.interval.total_seconds() * 1.5))

    def test_function_unregister(self):
        metrics_reset_and_stop_thread()
        metrics.launch_thread()
        
        count = 1
        def test_function():
            nonlocal count
            count += 1

        metrics.register_update_function(test_function)
        time.sleep(metrics.interval.total_seconds() * 1.5)

        metrics.unregister_update_function(test_function)
        time.sleep(metrics.interval.total_seconds() * 1.5)

        self.assertEqual(count, 2)

    def test_function_unregister_multiple_functions(self):
        metrics_reset_and_stop_thread()
        metrics.launch_thread()
        
        count_1 = 1
        def test_function_1():
            nonlocal count_1
            count_1 += 1
        
        count_2 = 1
        def test_function_2():
            nonlocal count_2
            count_2 += 1

        metrics.register_update_function([test_function_1, test_function_2])
        time.sleep(metrics.interval.total_seconds() * 1.5)

        metrics.unregister_update_function([test_function_1, test_function_2])
        time.sleep(metrics.interval.total_seconds() * 1.5)

        self.assertEqual(count_1, 2)
        self.assertEqual(count_2, 2)


    def test_is_thread_running_detect_thread_launched(self):
        metrics_reset_and_stop_thread()

        self.assertFalse(metrics.is_thread_running())
        metrics.launch_thread()

        self.assertTrue(metrics.is_thread_running())

    def test_stop_thread_detect_thread_stop(self):
        metrics_reset_and_stop_thread()
        metrics.launch_thread()

        self.assertTrue(metrics.is_thread_running())
        metrics.stop_thread()

        self.assertFalse(metrics.is_thread_running())

    def test_launch_thread(self):
        metrics_reset_and_stop_thread()

        self.assertFalse(metrics.is_thread_running())
        metrics.launch_thread()

        metrics.launch_thread() # should do nothing
        self.assertTrue(metrics.is_thread_running())

    def test_unregister_unknown_function_should_not_fail(self):
        metrics_reset_and_stop_thread()

        def dummy():
            pass

        metrics.unregister_update_function(dummy)
        metrics.unregister_update_function([dummy])

    