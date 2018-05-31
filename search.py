"""
Search algorithms.

A lot of code copied from:
    https://www.redblobgames.com/pathfinding/a-star/implementation.html
"""

import collections
import heapq
import sys


# from level import Level
from world import Action  # , World


class PriorityQueue:

    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class Queue:
    def __init__(self):
        self.elements = collections.deque()

    def empty(self):
        return len(self.elements) == 0

    def put(self, x):
        self.elements.append(x)

    def get(self):
        return self.elements.popleft()


class Graph(object):

    """
    Abstract class for graphs.
    """

    def __init__(self, **kw):
        assert not kw, f'no additional argument expected, but found: {kw}'

    def neighbors(self, node):
        raise NotImplementedError(self.__class__.__name__)


class WorldGraph(Graph):

    """
    Graph based on a `World`.
    """

    def __init__(self, world, **kw):
        """
        Constructor.

        :param world: The world this graph is based on.
        :param kw: Additional arguments forwarded to parent class.
        """
        super().__init__(**kw)
        self.world = world

    def cost(self, a, b):
        return 1
    
    def neighbors(self, node):
        state = node

        neighbors = []
        for action in Action:
            next_state = self.world.perform(state, action)
            if next_state is not None:
                neighbors.append(next_state)
        return neighbors


class SimpleGraph:

    def __init__(self):
        self.edges = {}

    def neighbors(self, id_):
        return self.edges[id_]


class SquareGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = []

    def in_bounds(self, id_):
        (x, y) = id_
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, id_):
        return id_ not in self.walls

    def neighbors(self, id_):
        (x, y) = id_
        results = [(x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)]
        if (x + y) % 2 == 0:
            results.reverse()  # aesthetics
        results = filter(self.in_bounds, results)
        results = filter(self.passable, results)
        return results


class GridWithWeights(SquareGrid):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.weights = {}

    # noinspection PyUnusedLocal
    def cost(self, from_node, to_node):
        return self.weights.get(to_node, 1)


def breadth_first_search_1(graph, start):
    # print out what we find
    frontier = Queue()
    frontier.put(start)
    visited = {start: True}

    while not frontier.empty():
        current = frontier.get()
        print("Visiting %r" % current)
        for next_ in graph.neighbors(current):
            if next_ not in visited:
                frontier.put(next_)
                visited[next_] = True


def breadth_first_search_2(graph, start):
    # return "came_from"
    frontier = Queue()
    frontier.put(start)
    came_from = {start: None}

    while not frontier.empty():
        current = frontier.get()
        for next_ in graph.neighbors(current):
            if next_ not in came_from:
                frontier.put(next_)
                came_from[next_] = current

    return came_from


def breadth_first_search_3(graph, start, goal):
    frontier = Queue()
    frontier.put(start)
    came_from = {start: None}

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next_ in graph.neighbors(current):
            if next_ not in came_from:
                frontier.put(next_)
                came_from[next_] = current

    return came_from


# utility functions for dealing with square grids
def from_id_width(id_, width):
    return id_ % width, id_ // width


def dijkstra_search(graph, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {start: None}
    cost_so_far = {start: 0}

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next_ in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next_)
            if next_ not in cost_so_far or new_cost < cost_so_far[next_]:
                cost_so_far[next_] = new_cost
                priority = new_cost
                frontier.put(next_, priority)
                came_from[next_] = current

    return came_from, cost_so_far


def draw_grid(graph, width=2, **style):
    for y in range(graph.height):
        for x in range(graph.width):
            print("%%-%ds" % width % draw_tile(graph, (x, y), style, width), end="")
        print()


def draw_tile(graph, id_, style, width):
    r = "."
    if 'number' in style and id_ in style['number']:
        r = "%d" % style['number'][id_]
    if 'point_to' in style and style['point_to'].get(id_, None) is not None:
        (x1, y1) = id_
        (x2, y2) = style['point_to'][id_]
        if x2 == x1 + 1:
            r = ">"
        if x2 == x1 - 1:
            r = "<"
        if y2 == y1 + 1:
            r = "v"
        if y2 == y1 - 1:
            r = "^"
    if 'start' in style and id_ == style['start']:
        r = "A"
    if 'goal' in style and id_ == style['goal']:
        r = "Z"
    if 'path' in style and id_ in style['path']:
        r = "@"
    if id_ in graph.walls:
        r = "#" * width
    return r


def heuristic(exit_check, state):
    return 0


def a_star_search(graph, start, exit_check):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {start: None}
    cost_so_far = {start: 0}
    processed = set()

    current = None
    found = False
    while not frontier.empty():
        current = frontier.get()

        if exit_check(current):
            found = True
            break

        if current in processed:
            print(f'Ignoring {current}')
            continue

        processed.add(current)

        for next_ in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next_)
            if next_ not in cost_so_far or new_cost < cost_so_far[next_]:
                cost_so_far[next_] = new_cost
                priority = new_cost + heuristic(exit_check, next_)
                frontier.put(next_, priority)
                came_from[next_] = current

    assert found, 'A* failed'
    return came_from, cost_so_far, current


def reconstruct_path(came_from, start, goal):
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)  # optional
    path.reverse()  # optional
    return path


DIAGRAM1_WALLS = [from_id_width(id_, width=30) for id_ in [21, 22, 51, 52, 81, 82, 93, 94, 111, 112, 123, 124, 133, 134, 141, 142, 153, 154, 163, 164, 171, 172, 173, 174, 175, 183, 184, 193, 194, 201, 202, 203, 204, 205, 213, 214, 223, 224, 243, 244, 253, 254, 273, 274, 283, 284, 303, 304, 313, 314, 333, 334, 343, 344, 373, 374, 403, 404, 433, 434]]


def main():
    """
    level = Level(width=10, height=10)
    world = World(level=level)
    world_graph = WorldGraph(world=world)
    exit_position, _ = level.get_exit()
    came_from, cost_so_far = a_star_search(graph=world_graph, start=world.init_state,
                                           exit_check=lambda state: world.get_player_position(state) == exit_position)
    """
    return 0


if __name__ == '__main__':
    sys.exit(main())
