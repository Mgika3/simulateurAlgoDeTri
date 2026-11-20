from ._utils import frame


def sort_steps(values):
    items = list(values)
    low, high = 0, len(items) - 1
    while low < high:
        changed = False
        for index in range(low, high):
            yield frame(items, index, index + 1)
            if items[index] > items[index + 1]:
                items[index], items[index + 1] = items[index + 1], items[index]
                changed = True
                yield frame(items, index, index + 1)
        high -= 1
        if not changed:
            break
        changed = False
        for index in range(high, low, -1):
            yield frame(items, index - 1, index)
            if items[index - 1] > items[index]:
                items[index - 1], items[index] = items[index], items[index - 1]
                changed = True
                yield frame(items, index - 1, index)
        low += 1
        if not changed:
            break
    yield frame(items)
