from ._utils import frame


def sort_steps(values):
    items = list(values)
    index = 1
    while index < len(items):
        yield frame(items, index - 1, index)
        if items[index - 1] <= items[index]:
            index += 1
        else:
            items[index - 1], items[index] = items[index], items[index - 1]
            yield frame(items, index - 1, index)
            index = max(1, index - 1)
    yield frame(items)
