from numpy.random import Generator

from waste.classes import Route, ShiftPlanEvent, Simulator


class GreedyStrategy:
    """
    A simple, greedy strategy that visits the containers with the largest
    number of arrivals since the last visit time.
    """

    def __init__(self, gen: Generator):
        self.gen = gen

    def __call__(self, sim: Simulator, event: ShiftPlanEvent) -> list[Route]:
        # TODO
        return []
