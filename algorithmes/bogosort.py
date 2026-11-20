import random

from ._utils import frame, is_sorted


def sort_steps(values):
    items = list(values)
    while not is_sorted(items):
        random.shuffle(items)
        yield frame(items, *range(len(items)))
    yield frame(items)
