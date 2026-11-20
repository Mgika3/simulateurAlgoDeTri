from ._utils import frame


def sort_steps(values):
    items = list(values)
    sum = 0
    for i in range(len(items)):
        yield frame(items, i, i + 1)
        sum += items[i]
    average = sum/len(items)
    for i in range(len(items)):
        items[i] = average
        yield frame(items)