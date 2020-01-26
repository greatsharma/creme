"""Learning rate schedulers."""
import abc
import math


__all__ = [
    'Constant',
    'Cyclic',
    'InverseScaling',
    'Optimal'
]


class Scheduler(abc.ABC):

    @abc.abstractmethod
    def get(self, t: int) -> float:
        """Returns the learning rate at a given iteration."""

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return f'{self.__class__.__name__}({self.__dict__})'


class Constant(Scheduler):
    """Always uses the same learning rate."""

    def __init__(self, learning_rate):
        self.learning_rate = learning_rate

    def get(self, t):
        return self.learning_rate


class Cyclic(Scheduler):
    """Cyclic learning schedule, in each cycle we linearly decrease the
    learning rate from lr1 to lr2.

    Parameters:
        lr1 (float): Starting learning rate.
        lr2 (float): Ending learning rate.
        c (int): Cycle length.

    References:
        1. `Averaging Weights Leads to Wider Optima and Better Generalization
            <https://arxiv.org/abs/1803.05407>`_

    """

    def __init__(self, lr1, lr2, c):
        assert lr1 >= lr2, "lr1 should be greater than or equal to lr2"
        assert c > 0 and isinstance(
            c, int), "c should be an integer greater than 0"

        self.lr1 = lr1
        self.lr2 = lr2
        self.c = c

    def get(self, t):
        ti = ((t-1) % self.c + 1) / self.c
        return (1 - ti) * self.lr1 + ti * self.lr2


class InverseScaling(Scheduler):
    """Reduces the learning rate using a power schedule.

    Assuming an iteration counter $t$ starting from 0, the learning rate will be:

    .. math:: \\frac{1}{(t+1)^p}

    where $p$ is a user-defined parameter.

    """

    def __init__(self, learning_rate, power=0.5):
        self.learning_rate = learning_rate
        self.power = power

    def get(self, t):
        return self.learning_rate / pow(t + 1, self.power)


class Optimal(Scheduler):
    """Optimal learning schedule as proposed by Léon Bottou.

    Parameters:
        loss (optim.losses.Loss)
        alpha (float)

    References:
        1. `Stochastic Gradient Descent <https://leon.bottou.org/projects/sgd>`_
        2. `Stochastic Gradient Descent Tricks <https://cilvr.cs.nyu.edu/diglib/lsml/bottou-sgd-tricks-2012.pdf>`_

    """

    def __init__(self, loss, alpha=1e-4):
        self.loss = loss
        self.alpha = alpha

        typw = math.sqrt(1. / math.sqrt(self.alpha))
        initial_eta0 = typw / max(1.0, self.loss.gradient(-typw, 1.0))
        self.t0 = 1. / (initial_eta0 * self.alpha)

    def get(self, t):
        return 1. / (self.alpha * (self.t0 + t))
