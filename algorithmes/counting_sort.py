from ._utils import frame


def sort_steps(values):
    items = list(values)
    if not items:
        yield frame(items)
        return
    minimum, maximum = min(items), max(items)
    counts = [0] * (maximum - minimum + 1)
    for index, value in enumerate(items):
        counts[value - minimum] += 1
        yield frame(items, index, details={
            "title": "Comptage des occurrences",
            "subtitle": f"Valeur {value} : {counts[value - minimum]} occurrence(s)",
            "counts": tuple((minimum + offset, count) for offset, count in enumerate(counts)),
            "current_value": value,
        })
    position = 0
    for offset, count in enumerate(counts):
        for _ in range(count):
            value = offset + minimum
            items[position] = value
            position += 1
            counts[offset] -= 1
            yield frame(items, position - 1, details={
                "title": "Reconstruction du tableau",
                "subtitle": f"Valeur {value} placée à l’index {position - 1}",
                "counts": tuple((minimum + i, remaining) for i, remaining in enumerate(counts)),
                "current_value": value,
            })
    yield frame(items, details={
        "title": "Comptage terminé",
        "subtitle": "Toutes les occurrences ont été replacées.",
        "counts": tuple((minimum + offset, count) for offset, count in enumerate(counts)),
        "current_value": None,
    })
