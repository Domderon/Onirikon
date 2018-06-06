"""
Genetic algorithm optimization.
"""

import queue
import time

from multiprocessing import Event, Process, Queue

from algorithm import Algorithm
from level import Level
from level import LEVEL_WIDTH, LEVEL_HEIGHT
from trajectory import RandomWalkTrajectory


def optimize(output_queue, stop_event, trajectory, width=LEVEL_WIDTH, height=LEVEL_HEIGHT, put_period=10, density=0.2):
    """
    Launch optimization.

    :param output_queue: Queue where the interesting results of the optimization process should be put.
    :param stop_event: Event that should be set when this function must return.
    """
    algorithm = Algorithm(trajectory=trajectory, width=trajectory.level_width, height=trajectory.level_height,
                          population_size=10,
                          tournament_size=5,
                          mutation_probability=0.01,
                          generations=1000, chromosome_size=100)

    for best_level, fitness in algorithm.run():
        try:
            output_queue.put_nowait((best_level, trajectory, fitness))
        except queue.Full:
            print('Warning: output queue is full')
        if stop_event.is_set():
            print('Stop event detected - stopping optimization')
            break


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
