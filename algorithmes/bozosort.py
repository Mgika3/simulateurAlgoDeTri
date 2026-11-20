import random

from ._utils import frame, is_sorted


def sort_steps(values):
    items = list(values)
    while not is_sorted(items):
        i = random.randint(0, len(items)-1)
        j = random.randint(0, len(items)-1)
        yield frame(items, i, j)
        if (i < j and items[i] > items[j]) or (i > j and items[i] < items[j]):
            items[i], items[j] = items[j], items[i]
        
    yield frame(items)
