from __future__ import annotations

import logging
from datetime import datetime
from heapq import heappop, heappush
from itertools import count
from typing import TYPE_CHECKING, Callable, Optional

from waste.constants import TIME_PER_CONTAINER

from .Event import ArrivalEvent, Event, ServiceEvent, ShiftPlanEvent

if TYPE_CHECKING:
    import numpy as np
    from numpy.random import Generator

    from waste.strategies import Strategy

    from .Container import Container
    from .Route import Route
    from .Vehicle import Vehicle

logger = logging.getLogger(__name__)


class _EventQueue:
    """
    Simple internal event queue that efficiently manages events in order of
    time.
    """

    def __init__(self):
        self._events = []
        self._counter = count(0)

    def __len__(self) -> int:
        return len(self._events)

    def push(self, event: Event):
        tiebreaker = next(self._counter)
        heappush(self._events, (event.time, tiebreaker, event))

    def pop(self) -> Event:
        *_, event = heappop(self._events)
        return event


class Simulator:
    """
    The simulator class. This class is responsible for running the main
    simulation event queue, and has a few attributes that describe the
    simulation environment.
    """

    def __init__(
        self,
        generator: Generator,
        distances: np.array,
        durations: np.array,
        containers: list[Container],
        vehicles: list[Vehicle],
    ):
        self.generator = generator
        self.distances = distances
        self.durations = durations
        self.containers = containers
        self.vehicles = vehicles

    def __call__(
        self,
        store: Callable[[Event | Route], Optional[int]],
        strategy: Strategy,
        initial_events: list[Event],
    ):
        """
        Applies a strategy for a simulation starting with the given initial
        events.        .
        """
        events = _EventQueue()

        for event in initial_events:
            events.push(event)

        now = datetime.min

        while events:
            event = events.pop()

            if event.time < now:
                msg = f"{event} time is before current time {now}!"
                logger.error(msg)
                raise ValueError(msg)

            now = event.time

            # First seal the event. This ensures all data that was previously
            # linked to changing objects is made static at their current
            # values ("sealed"). After sealing, an event's state has become
            # independent from that of the objects it references.
            event.seal()
            store(event)

            match event:
                case ArrivalEvent(time=time, container=c, volume=vol):
                    c.arrive(vol)
                    logger.debug(f"Arrival at {c.name} at t = {time}.")
                case ServiceEvent(time=time, container=c):
                    c.service()
                    logger.debug(f"Service at {c.name} at t = {time}.")
                case ShiftPlanEvent(time=time):
                    logger.info(f"Generating shift plan at t = {time}.")

                    for route in strategy(self, event):
                        id_route = store(route)
                        assert id_route is not None

                        service_time = now
                        prev = 0

                        for curr in route.plan:
                            service_time += self.durations[prev, curr].item()

                            events.push(
                                ServiceEvent(
                                    service_time,
                                    id_route=id_route,
                                    container=self.containers[curr],
                                    vehicle=route.vehicle,
                                )
                            )

                            service_time += TIME_PER_CONTAINER
                            prev = curr
                case _:
                    msg = f"Unhandled event of type {type(event)}."
                    logger.error(msg)
                    raise ValueError(msg)
