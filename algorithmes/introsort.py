from ._utils import frame


def sort_steps(values):
    items = list(values)

    def heap_range(start, end):
        length = end - start

        def sift(root, limit):
            while 2 * root + 1 < limit:
                child = 2 * root + 1
                if child + 1 < limit and items[start + child] < items[start + child + 1]:
                    child += 1
                if items[start + root] >= items[start + child]:
                    return
                items[start + root], items[start + child] = items[start + child], items[start + root]
                yield frame(items, start + root, start + child)
                root = child

        for root in range(length // 2 - 1, -1, -1):
            yield from sift(root, length)
        for limit in range(length - 1, 0, -1):
            items[start], items[start + limit] = items[start + limit], items[start]
            yield frame(items, start, start + limit)
            yield from sift(0, limit)

    def insertion(start, end):
        for index in range(start + 1, end):
            value = items[index]
            cursor = index
            while cursor > start and items[cursor - 1] > value:
                items[cursor] = items[cursor - 1]
                cursor -= 1
                yield frame(items, cursor, index)
            items[cursor] = value
            yield frame(items, cursor)

    def intro(start, end, depth):
        while end - start > 16:
            if depth == 0:
                yield from heap_range(start, end)
                return
            depth -= 1
            middle = (start + end - 1) // 2
            pivot = sorted((items[start], items[middle], items[end - 1]))[1]
            low, cursor, high = start, start, end
            while cursor < high:
                yield frame(items, cursor)
                if items[cursor] < pivot:
                    items[low], items[cursor] = items[cursor], items[low]
                    low += 1
                    cursor += 1
                elif items[cursor] > pivot:
                    high -= 1
                    items[cursor], items[high] = items[high], items[cursor]
                else:
                    cursor += 1
                yield frame(items, low, cursor)
            if low - start < end - high:
                yield from intro(start, low, depth)
                start = high
            else:
                yield from intro(high, end, depth)
                end = low
        yield from insertion(start, end)

    depth_limit = 2 * (len(items).bit_length() - 1) if items else 0
    yield from intro(0, len(items), depth_limit)
    yield frame(items)
