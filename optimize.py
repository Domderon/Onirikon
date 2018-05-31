"""
Genetic algorithm optimization.
"""

import queue
import time

from multiprocessing import Event, Process, Queue

from level import Level
from trajectory import Trajectory


def optimize(output_queue, stop_event, width=20, height=30, put_period=10, density=0.2):
    """
    Launch optimization.

    :param output_queue: Queue where the interesting results of the optimization process should be put.
    """
    while True:
        if stop_event.is_set():
            print('Stop event detected - stopping optimization')
            break
        level = Level(width, height)
        trajectory = Trajectory(level)
        level.generate_from_trajectory(trajectory, density=density)
        time.sleep(put_period)
        try:
            output_queue.put_nowait((level, trajectory))
        except queue.Full:
            print('Warning: output queue is full')


if __name__ == '__main__':
    # Test code.
    output_queue = Queue()
    stop_event = Event()
    process = Process(target=optimize, kwargs=dict(output_queue=output_queue, stop_event=stop_event, put_period=1))
    process.start()
    stop_time = time.time() + 10
    while time.time() < stop_time:
        try:
            item = output_queue.get(block=True, timeout=1)
        except queue.Empty:
            pass
        print('Obtained an item from the queue')
        if not process.is_alive():
            print('Our dear child died :(')
            break

    stop_event.set()
