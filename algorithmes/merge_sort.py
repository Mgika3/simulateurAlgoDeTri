from ._utils import frame


def sort_steps(values):
    items = list(values)

    def split(left, right):
        if right - left < 2:
            return
        middle = (left + right) // 2
        yield from split(left, middle)
        yield from split(middle, right)
        merged = []
        i, j = left, middle
        while i < middle and j < right:
            yield frame(items, i, j)
            if items[i] <= items[j]:
                merged.append(items[i])
                i += 1
            else:
                merged.append(items[j])
                j += 1
        merged.extend(items[i:middle])
        merged.extend(items[j:right])
        for offset, value in enumerate(merged):
            items[left + offset] = value
            yield frame(items, left + offset)

    yield from split(0, len(items))
    yield frame(items)
