from ._utils import frame


def sort_steps(values):
    items = list(values)
    for start in range(len(items)):
        minimum = start
        for index in range(start + 1, len(items)):
            yield frame(items, minimum, index)
            if items[index] < items[minimum]:
                minimum = index
        if minimum != start:
            items[start], items[minimum] = items[minimum], items[start]
            yield frame(items, start, minimum)
    yield frame(items)
