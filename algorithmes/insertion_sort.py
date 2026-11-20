from ._utils import frame


def sort_steps(values):
    items = list(values)
    for index in range(1, len(items)):
        value = items[index]
        cursor = index
        while cursor > 0:
            yield frame(items, cursor - 1, cursor)
            if items[cursor - 1] <= value:
                break
            items[cursor] = items[cursor - 1]
            cursor -= 1
        items[cursor] = value
        yield frame(items, cursor)
    yield frame(items)
