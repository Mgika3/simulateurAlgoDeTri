from ._utils import frame


def sort_steps(values):
    items = list(values)
    size = len(items)

    def sift_down(root, end):
        while (child := 2 * root + 1) <= end:
            if child + 1 <= end and items[child] < items[child + 1]:
                child += 1
            yield frame(items, root, child)
            if items[root] >= items[child]:
                return
            items[root], items[child] = items[child], items[root]
            yield frame(items, root, child)
            root = child

    for root in range(size // 2 - 1, -1, -1):
        yield from sift_down(root, size - 1)
    for end in range(size - 1, 0, -1):
        items[0], items[end] = items[end], items[0]
        yield frame(items, 0, end)
        yield from sift_down(0, end - 1)
    yield frame(items)
