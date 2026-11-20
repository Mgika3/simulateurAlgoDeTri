from ._utils import frame


def sort_steps(values):
    items = list(values)
    if not items:
        yield frame(items)
        return
    low, high = min(items), max(items)
    if low == high:
        yield frame(items)
        return
    bucket_count = max(1, int(len(items) ** 0.5))
    buckets = [[] for _ in range(bucket_count)]
    for index, value in enumerate(items):
        slot = min(bucket_count - 1, int((value - low) * bucket_count / (high - low + 1)))
        buckets[slot].append(value)
        yield frame(items, index, details={
            "title": "Répartition dans les paquets",
            "subtitle": f"Valeur {value} → paquet {slot + 1}",
            "buckets": tuple((f"Paquet {i + 1}", tuple(bucket)) for i, bucket in enumerate(buckets)),
        })
    output = []
    for bucket_index, bucket in enumerate(buckets):
        for index, value in enumerate(bucket):
            cursor = index
            while cursor > 0 and bucket[cursor - 1] > value:
                bucket[cursor] = bucket[cursor - 1]
                cursor -= 1
            bucket[cursor] = value
            yield frame(items, cursor, details={
                "title": "Tri local des paquets",
                "subtitle": f"Paquet {bucket_index + 1} — insertion de {value}",
                "buckets": tuple((f"Paquet {i + 1}", tuple(values)) for i, values in enumerate(buckets)),
            })
        output.extend(bucket)
    items[:] = output
    for index, value in enumerate(items):
        yield frame(items, index, details={
            "title": "Reconstruction du tableau",
            "subtitle": f"Valeur {value} placée à l’index {index}",
            "buckets": tuple((f"Paquet {i + 1}", tuple(values)) for i, values in enumerate(buckets)),
        })
    yield frame(items)
