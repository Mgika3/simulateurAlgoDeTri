from ._utils import frame


def sort_steps(values):
    items = list(values)
    if not items:
        yield frame(items)
        return

    def lsd(numbers, negative_values=False):
        if not numbers:
            return
        place = 1
        largest = max(numbers)
        while largest // place:
            buckets = [[] for _ in range(10)]
            sign = "négatifs" if negative_values else "positifs"
            for index, number in enumerate(numbers):
                digit = (number // place) % 10
                buckets[digit].append(number)
                distributed = [value for bucket in buckets for value in bucket]
                remaining = numbers[index + 1:]
                ordered = (
                    [-value for value in reversed(distributed)]
                    + [-value for value in remaining]
                    + positive_values
                    if negative_values
                    else [-value for value in reversed(negative_magnitudes)]
                    + distributed
                    + remaining
                )
                yield tuple(ordered), (), {
                    "title": "Répartition par chiffre",
                    "subtitle": f"Position {place} · {sign} · {number} va dans le chiffre {digit}",
                    "buckets": tuple(
                        (
                            f"Chiffre {i}",
                            tuple(-value for value in bucket) if negative_values else tuple(bucket),
                        )
                        for i, bucket in enumerate(buckets)
                    ),
                }
            numbers[:] = [number for bucket in buckets for number in bucket]
            ordered = (
                [-number for number in reversed(numbers)] + positive_values
                if negative_values
                else [-value for value in reversed(negative_magnitudes)] + numbers
            )
            yield tuple(ordered), (), {
                "title": "Assemblage stable",
                "subtitle": f"Passage terminé pour la position {place} ({sign})",
                "buckets": tuple(
                    (
                        f"Chiffre {i}",
                        tuple(-value for value in bucket) if negative_values else tuple(bucket),
                    )
                    for i, bucket in enumerate(buckets)
                ),
            }
            place *= 10

    negative_magnitudes = [-value for value in items if value < 0]
    positive_values = [value for value in items if value >= 0]
    yield from lsd(negative_magnitudes, negative_values=True)
    yield from lsd(positive_values)
    items[:] = [-value for value in reversed(negative_magnitudes)] + positive_values
    yield frame(items)
