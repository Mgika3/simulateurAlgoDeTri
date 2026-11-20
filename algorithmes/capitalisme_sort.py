from ._utils import frame


def sort_steps(values):
    items = list(values)
    somme = 0
    for i in range(len(items)):
        somme += items[i]
        yield frame(items, i)
    for j in range(len(items) - 3):
        items[j] = 0
    items[-3] = somme//3
    items[-2] = somme//3
    items[-1] = somme//3
    yield frame(items)
