from ._utils import frame


def sort_steps(values):
    items = list(values)
    gap = len(items)
    swapped = True
    while gap > 1 or swapped:
        gap = max(1, int(gap / 1.3))
        swapped = False
        for index in range(len(items) - gap):
            yield frame(items, index, index + gap)
            if items[index] > items[index + gap]:
                items[index], items[index + gap] = items[index + gap], items[index]
                swapped = True
                yield frame(items, index, index + gap)
    yield frame(items)
