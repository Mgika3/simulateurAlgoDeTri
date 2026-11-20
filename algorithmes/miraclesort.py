from ._utils import frame


def sort_steps(values):
    items = list(values)   
    while True:
        for i in range(len(items)):
            yield frame(items, i, i + 1)
        yield frame(items)
