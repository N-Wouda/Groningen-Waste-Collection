import logging

import numpy as np
from scipy import optimize

from .Container import Container

logger = logging.getLogger(__name__)


class LogisticRegression:
    """
    A class implementing a self-adjusting logistic regression. Initially,
    default parameters are fitted base on the container capacity, deposit
    volume, and the epsilon parameter. After a number of observations, the
    method switches to fitting parameters based on the observed data, rather
    than the initial values.

    Parameters
    ----------
    container
        Container whose arrival behaviour we're trying to model here.
    deposit_volume
        Estimated volume of a single deposit. Used to determine initial
        parameters.
    obs_until_switch
        Number of observations needed in both categories before switching from
        initial parameters to those based on observed data. Default 10.
    eps
        Epsilon value to use when determining the initial parameters.
    """

    def __init__(
        self,
        container: Container,
        deposit_volume: float,
        obs_until_switch: int = 10,
        eps: float = 1e-3,
    ):
        self.container = container
        self.switch_when = obs_until_switch

        self.data: list[tuple[int, bool]] = []

        # Initially set b0 and b1 such that:
        #   p(0) = eps
        #   p(full_after) = 1 - eps
        full_after = self.container.capacity / deposit_volume
        b0 = -np.log(1 / eps - 1)
        b1 = (-np.log(1 / (1 - eps) - 1) - b0) / full_after
        self.params = np.array([b0, b1])

    def prob(self, num_arrivals: float) -> float:
        return 1 / (1 + np.exp(-self.params @ [1, num_arrivals]))

    def observe(self, x: int, y: bool):
        logger.debug(f"{self.container.name}: observing ({x}, {y}).")
        self.data.append((x, y))

        num_overflows = sum(overflow for _, overflow in self.data)
        sufficient_data = len(self.data) >= 2 * self.switch_when

        if sufficient_data and num_overflows >= self.switch_when:
            self.optimize()

    def optimize(self):
        data = np.ones((len(self.data), 3))
        data[:, 1:] = self.data
        X = data[:, :2]
        y = data[:, 2]

        def loglik(b):  # minus since we want to maximize
            return -np.sum(y * (X @ b) - np.log(1 + np.exp(X @ b)))

        params = self.params
        inf = np.inf

        res = optimize.minimize(loglik, params, bounds=((-inf, inf), (0, 1)))
        self.params = res.x
