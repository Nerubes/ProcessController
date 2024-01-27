from collections import deque
import multiprocess
import time
import threading

class ProcessController:
    class ProcessManager(threading.Thread):
        def __init__(self, controller, lag):
            self.controller_ = controller
            self.lag_ = lag
            self.ending_ = False
            super().__init__(daemon=True)

        def set_end(self):
            self.ending_ = True

        def create_new_process_(self):
            lock = threading.Lock()
            # Тут можно вынести из лока реальное создание процесса, если не нужно 100 процентно знать создался ли он
            with lock:
                func, args = self.controller_.tasks_.pop()
                self.controller_.alive_ += 1
                proc = multiprocess.Process(target=func, args=args, daemon=True)
                self.controller_.procs_.add((proc, time.monotonic_ns()))
                try :
                    proc.start()
                except Exception:
                    self.controller_.alive_ -= 1
                    proc = (None, 0)

        def run(self):
            while True:
                ended_procs = set()
                for proc in self.controller_.procs_:
                    if time.monotonic_ns() - proc[1] >= self.controller_.max_exec_time_:
                        proc[0].kill()
                    if proc[0] and not proc[0].is_alive():
                        ended_procs.add(proc)
                        self.controller_.alive_ -= 1
                self.controller_.procs_ -= ended_procs
                while len(self.controller_.tasks_) and len(self.controller_.procs_) < self.controller_.max_proc_:
                    self.create_new_process_()
                if self.ending_ and not self.controller_.procs_ and not len(self.controller_.tasks_):
                    break
                time.sleep(self.lag_)

    def __init__(self, max_proc = 4, max_exec_time = 1, manager_lag = 0.001):
        self.max_proc_ = max_proc
        self.max_exec_time_ = max_exec_time * 10 ** 9
        self.tasks_ = deque()
        self.procs_ = set()
        self.procsess_manager_ = self.ProcessManager(self, manager_lag)
        self.alive_ = 0


    def set_max_proc(self, n):
        self.max_proc_ = n

    def start(self, tasks):
        for i in tasks:
            self.tasks_.appendleft(i)

        if not self.procsess_manager_.is_alive():
            self.procsess_manager_.start()

    def wait(self):
        self.procsess_manager_.set_end()
        self.procsess_manager_.join()

    def wait_count(self):
        return len(self.tasks_)
    
    def alive_count(self):
        return self.alive_
    