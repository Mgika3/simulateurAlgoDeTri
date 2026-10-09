from ._utils import frame


def sort_steps(values):
    items = list(values)

    def quick(left, right):
        if left >= right:
            return
        pivot = items[right]
        boundary = left
        for index in range(left, right):
            yield frame(items, index, right)
            if items[index] <= pivot:
                items[boundary], items[index] = items[index], items[boundary]
                yield frame(items, boundary, index)
                boundary += 1
        items[boundary], items[right] = items[right], items[boundary]
        yield frame(items, boundary, right)
        yield from quick(left, boundary - 1)
        yield from quick(boundary + 1, right)

    yield from quick(0, len(items) - 1)
    yield frame(items)
