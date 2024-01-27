from ProcessController import ProcessController

import time
import pytest
import multiprocess

def short_sleep():
    time.sleep(0.25)

def long_sleep():
    time.sleep(1)

def write_in_file(i):
    with open('test', 'a') as file:
        file.write(str(i))

@pytest.fixture
def controller():
    return ProcessController(max_exec_time=0.5)

@pytest.fixture
def start_time():
    return time.monotonic()

def test_a_lot_of_short(controller, start_time):
    tasks = [(short_sleep, (),) for i in range(15)]
    controller.start(tasks)
    assert controller.wait_count() + controller.alive_count() == 15
    time.sleep(0.1)
    assert controller.alive_count() == 4
    assert controller.wait_count() == 11
    controller.wait()
    assert controller.alive_count() == 0
    assert controller.wait_count() == 0
    end_time = time.monotonic()
    assert end_time - start_time >= 1 and end_time - start_time <= 1.1

def test_one_long(controller, start_time):
    tasks = ((long_sleep, ()),)
    controller.start(tasks)
    controller.wait()
    assert time.monotonic() - start_time <= 0.6

def test_a_lot_of_long(controller, start_time):
    tasks = [(long_sleep, (),) for i in range(15)]
    controller.start(tasks)
    assert controller.wait_count() + controller.alive_count() == 15
    time.sleep(0.1)
    assert controller.alive_count() == 4
    assert controller.wait_count() == 11
    controller.wait()
    assert controller.alive_count() == 0
    assert controller.wait_count() == 0
    end_time = time.monotonic()
    assert end_time - start_time >= 2 and end_time - start_time <= 2.1

def test_changing_max_proc(controller):
    tasks = [(short_sleep, (),) for i in range(12)]
    controller.start(tasks)
    time.sleep(0.1)
    assert controller.alive_count() == 4
    controller.set_max_proc(6)
    time.sleep(0.1)
    assert controller.alive_count() == 6
    assert controller.wait_count() == 6

def test_order_of_executing(controller):
    with open('test', 'w+') as file:
        file.write('')
        controller.set_max_proc(1)
        tasks = [(write_in_file, (i,),) for i in range(5)]
        controller.start(tasks)
        controller.wait()
        s = file.read()
        assert s == '01234'