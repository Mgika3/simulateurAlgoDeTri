from ._utils import frame


def sort_steps(values):
    items = list(values)
    size = len(items)
    min_run = 16
    runs = []
    start = 0
    while start < size:
        end = start + 1
        if end < size:
            descending = items[end] < items[start]
            end += 1
            while end < size and ((items[end] < items[end - 1]) if descending else (items[end] >= items[end - 1])):
                end += 1
            if descending:
                items[start:end] = reversed(items[start:end])
                yield frame(items, start, end - 1)
        target = min(size, max(end, start + min_run))
        for index in range(end, target):
            value = items[index]
            cursor = index
            while cursor > start and items[cursor - 1] > value:
                yield frame(items, cursor - 1, cursor)
                items[cursor] = items[cursor - 1]
                cursor -= 1
            items[cursor] = value
            yield frame(items, cursor)
        runs.append((start, target - start))
        start = target

    def merge_at(run_index):
        left, left_size = runs[run_index]
        right, right_size = runs[run_index + 1]
        left_values = items[left:left + left_size]
        right_values = items[right:right + right_size]
        i = j = 0
        cursor = left
        while i < left_size and j < right_size:
            yield frame(items, left + i, right + j)
            if left_values[i] <= right_values[j]:
                items[cursor] = left_values[i]
                i += 1
            else:
                items[cursor] = right_values[j]
                j += 1
            yield frame(items, cursor)
            cursor += 1
        while i < left_size:
            items[cursor] = left_values[i]
            i += 1
            cursor += 1
            yield frame(items, cursor - 1)
        while j < right_size:
            items[cursor] = right_values[j]
            j += 1
            cursor += 1
            yield frame(items, cursor - 1)
        runs[run_index] = (left, left_size + right_size)
        del runs[run_index + 1]

    while len(runs) > 1:
        index = len(runs) - 2
        if index > 0 and runs[index - 1][1] <= runs[index][1] + runs[index + 1][1]:
            if runs[index - 1][1] < runs[index + 1][1]:
                index -= 1
        yield from merge_at(index)
    yield frame(items)
