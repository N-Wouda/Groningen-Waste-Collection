from datetime import date, datetime, time, timedelta

import pandas as pd
from numpy.random import default_rng
from numpy.testing import assert_equal

from tests.helpers import NullStrategy
from waste.classes import (
    ArrivalEvent,
    Database,
    Simulator,
)
from waste.measures import num_arrivals_per_hour


def test_num_arrivals_per_hour():
    src_db = "tests/test.db"
    res_db = ":memory:"
    db = Database(src_db, res_db)

    sim = Simulator(
        default_rng(0),
        db.distances(),
        db.durations(),
        db.containers(),
        db.vehicles(),
    )

    strategy = NullStrategy()

    today = date.today()
    start = datetime.combine(today, time.min)
    end = datetime.combine(today, time.max) + timedelta(days=1)
    period = 2  # hours between two deposits

    tot_hours = (end - start).total_seconds() / 3600
    tot_hours / period

    events = []
    for container in db.containers():
        deposit_times = pd.date_range(
            start, end, freq=f"{period}H"
        ).to_pydatetime()
        volumes = [10] * len(deposit_times)
        for t, volume in zip(deposit_times, volumes):
            events.append(ArrivalEvent(t, container=container, volume=volume))

    sim(db.store, strategy, events)

    assert_equal(len(events), sum(db.compute(num_arrivals_per_hour)))
