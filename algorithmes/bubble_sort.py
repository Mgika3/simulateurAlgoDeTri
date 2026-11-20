from ._utils import frame


def sort_steps(values):
    items = list(values)
    for end in range(len(items) - 1, 0, -1):
        changed = False
        for index in range(end):
            yield frame(items, index, index + 1)
            if items[index] > items[index + 1]:
                items[index], items[index + 1] = items[index + 1], items[index]
                changed = True
                yield frame(items, index, index + 1)
        if not changed:
            break
    yield frame(items)
