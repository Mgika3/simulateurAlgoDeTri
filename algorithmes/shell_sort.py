from ._utils import frame


def sort_steps(values):
    items = list(values)
    gaps = [701, 301, 132, 57, 23, 10, 4, 1]
    gaps = [gap for gap in gaps if gap < len(items)] or [1]
    for gap in gaps:
        for index in range(gap, len(items)):
            value = items[index]
            cursor = index
            while cursor >= gap:
                yield frame(items, cursor - gap, cursor)
                if items[cursor - gap] <= value:
                    break
                items[cursor] = items[cursor - gap]
                cursor -= gap
            items[cursor] = value
            yield frame(items, cursor)
    yield frame(items)
