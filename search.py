"""
Search algorithms.

A lot of code copied from:
    https://www.redblobgames.com/pathfinding/a-star/implementation.html
"""

import heapq
import sys


from world import Action


class PriorityQueue:

    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class Graph(object):

    """
    Abstract class for graphs.
    """

    def __init__(self, **kw):
        assert not kw, f'no additional argument expected, but found: {kw}'

    def cost(self, from_node, to_node):
        """
        Cost from moving from `from_node` to `to_node`.
        """
        return 1

    def neighbors(self, node):
        """
        Obtain neighbors of `node`.
        """
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

        # Try all actions and keep only valid neighbors.
        for action in Action:
            next_state = self.world.perform(state, action)
            if next_state is not None:
                neighbors.append(next_state)

        return neighbors


def heuristic(from_node_def, to_node_def):
    """
    The A* heuristic function.

    It operates on node definitions (typically representing positions)
    """
    # L1 distance.
    return sum(abs(a - b) for a, b in zip(from_node_def, to_node_def))


def a_star_search(graph, start, exit_definition, extract_definition):
    """
    A* algorithm.

    :param graph: The graph to work on.
    :param start: The start node.
    :param exit_definition: How the exit node is defined (it should be an iterable of values, typically integers
        representing a position).
    :param extract_definition: A function that, when applied on a node, extracts its definition, to be compared to
        `exit_definition` in order to compute the heuristic and check if the exit is reached. Typically this function
        just extracts the position corresponding to the node.
    """
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {start: None}
    cost_so_far = {start: 0}
    processed = set()

    current = None
    found = False
    n_steps = 0
    while not frontier.empty():
        n_steps += 1
        current = frontier.get()

        if extract_definition(current) == exit_definition:
            # Reached the exit!
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
                priority = new_cost + heuristic(extract_definition(next_), exit_definition)
                frontier.put(next_, priority)
                came_from[next_] = current

    assert found, 'A* failed'
    # print(f'A* succeeded in {n_steps} steps')
    return came_from, cost_so_far, current


def main():
    # Test code, if needed.
    return 0


if __name__ == '__main__':
    sys.exit(main())
