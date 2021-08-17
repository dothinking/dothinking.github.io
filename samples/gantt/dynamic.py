import random
import time
from collections import namedtuple
from threading import Thread
import matplotlib.pyplot as plt
from matplotlib.container import BarContainer
from matplotlib.animation import FuncAnimation


class Problem:
    def __init__(self, num_job:int, num_machine:int, solution) -> None:
        '''Initialize problem with the count of job and machine.'''
        self.num_job = num_job
        self.num_machine = num_machine

        # a solution is a collection of tasks with determined start time
        self.__solution = solution # type: Solution

        # implement dynamic gantt chart by animation
        self.__animation = None

    
    def solve(self):
        '''Solve problem and update Gantt chart dynamically.'''
        # solve problem in child thread
        thread = Thread(target=self.__solution.update, \
                        args=(self.num_job, self.num_machine))
        thread.start()

        # show gantt chart and listen to the solution update in main thread
        self.__dynamic_gantt(interval=1000)
        plt.show()


    def __dynamic_gantt(self, interval:int=1000):
        '''Create plot and define animation to update data dynamically.'''
        # create two subplots: job view and machine view
        fig, (gnt_job, gnt_machine) = plt.subplots(2,1, sharex=True)

        # title
        fig.suptitle('Gantt Chart', fontweight='bold')

        # axis style for job subplot
        job_ids = range(self.num_job)
        gnt_job.set(ylabel='Job', \
            yticks=job_ids, \
            yticklabels=[f'Job-{i}' for i in job_ids])
        gnt_job.grid(which='major', axis='x', linestyle='--')

        # axis style for machine subplot
        machine_ids = range(self.num_machine)
        gnt_machine.set(xlabel='Time', ylabel='Machine',\
            yticks=machine_ids, \
            yticklabels=[f'M-{i}' for i in machine_ids])
        gnt_machine.grid(which='major', axis='x', linestyle='--')

        # animation
        self.__animation = FuncAnimation(fig, \
            func=lambda i: self.__solution.plot(axes=(gnt_job, gnt_machine)), \
            interval=interval, \
            repeat=False)


class Solution:

    Task = namedtuple('Task',['jid','mid', 'start', 'duration'])
    
    def __init__(self) -> None:
        self.__tasks = [] # list[Task]
        self.__update_plot = False

    def update(self, num_job:int, num_machine:int):
        '''Simulate a real solving process to update solution iteratively.'''
        for i in range(num_job):
            time.sleep(1.5)
            self.__add_random_tasks(i, num_machine)
            self.__update_plot = True # signal to update plot
            
    
    def plot(self, axes:tuple):
        '''Plot Gantt chart data area.'''
        # update plot only if the solution is updated
        if not self.__update_plot:
            return
        else:
            self.__update_plot = False
        
        # clear plotted bars
        for axis in axes:
            bars = [bar for bar in axis.containers if isinstance(bar, BarContainer)]
            for bar in bars: bar.remove()
        
        # plot new bars
        gnt_job, gnt_machine = axes
        for task in self.__tasks:
            gnt_job.barh(task.jid, task.duration, left=task.start, height=0.5)
            gnt_machine.barh(task.mid, task.duration, left=task.start, height=0.5)
            
        # reset x-limit
        for axis in axes:
            axis.relim()
            axis.autoscale(axis='x')

    
    def __add_random_tasks(self, job_id:int, num_machine:int):
        '''Create random tasks belonging to a job.'''
        # random machine id
        machines = list(range(num_machine))
        random.shuffle(machines)

        # random tasks
        lower, upper = 10, 50
        start = 0
        for mid in machines:
            duration = random.randint(lower, upper)
            task = Solution.Task(jid=job_id, mid=mid, start=start, duration=duration)
            start += duration + random.randint(5, 10)
            self.__tasks.append(task)


if __name__=='__main__':
    s = Solution()
    p = Problem(num_job=5, num_machine=4, solution=s)
    p.solve()