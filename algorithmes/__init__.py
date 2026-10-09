from . import (
    bogosort,
    bubble_sort,
    bucket_sort,
    cocktail_sort,
    comb_sort,
    counting_sort,
    gnome_sort,
    heap_sort,
    insertion_sort,
    introsort,
    merge_sort,
    quick_sort,
    radix_sort,
    selection_sort,
    shell_sort,
    timsort,
)

ALGORITHMS = [
    ("Tri fusion", "Stable . O(n log n)", merge_sort),
    ("Tri rapide", "Partition . O(n log n)", quick_sort),
    ("Tri par tas", "Arbre binaire . O(n log n)", heap_sort),
    ("Tri Shell", "Intervalles . O(n log² n)", shell_sort),
    ("Tri par insertion", "In situ . O(n²)", insertion_sort),
    ("Tri par sélection", "Simple . O(n²)", selection_sort),
    ("Tri à bulles", "Échanges . O(n²)", bubble_sort),
    ("Tri shaker", "Bidirectionnel . O(n²)", cocktail_sort),
    ("Tri peigne", "Écart décroissant . O(n²)", comb_sort),
    ("Tri gnome", "Adjacent . O(n²)", gnome_sort),
    ("Tri comptage", "Entiers . O(n + k)", counting_sort),
    ("Tri par base", "Chiffres . O(d · n)", radix_sort),
    ("Tri par paquets", "Distribution . O(n + k)", bucket_sort),
    ("Timsort", "Runs + fusion . O(n log n)", timsort),
    ("Introsort", "Hybride . O(n log n)", introsort),
    ("Bogosort", "Aléatoire . O(n · n!)", bogosort),
]

__all__ = ["ALGORITHMS"]
