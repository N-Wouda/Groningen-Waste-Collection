from numpy.random import Generator

from waste.classes import Route, ShiftPlanEvent, Simulator


class BaselineStrategy:
    """
    A fairly faithful implementation of what the municipality is currently
    doing.
    """

    def __init__(self, gen: Generator):
        self.gen = gen

    def __call__(self, sim: Simulator, event: ShiftPlanEvent) -> list[Route]:
        # TODO
        return []