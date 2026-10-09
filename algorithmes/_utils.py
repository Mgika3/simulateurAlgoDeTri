def frame(values, *active, details=None):
    state = (tuple(values), tuple(active))
    return state if details is None else (*state, details)


def is_sorted(values):
    return all(values[i] <= values[i + 1] for i in range(len(values) - 1))
