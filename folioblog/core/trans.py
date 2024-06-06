"""
Ugly way to translate collection names manually because native wagtail
Collection model isn't translatable out of the box.
A better alternative could be to use an another model (like a snippet) which
mimic native Collection model and of course, which would be translatable and
custom Image model will use it instead...
But to be honest, I don't have enough time to do it!
"""

from django.utils.translation import pgettext


def export_trans():
    """
    At least, should load untracked files...
    """
    pgettext("collection", "Bogota")
    pgettext("collection", "Bordeaux")
    pgettext("collection", "Cali")
    pgettext("collection", "Carcassonne")
    pgettext("collection", "Carthagène des Indes")
    pgettext("collection", "Chicago")
    pgettext("collection", "Los Angeles")
    pgettext("collection", "Lyon")
    pgettext("collection", "Marseille")
    pgettext("collection", "Medellin")
    pgettext("collection", "Miami")
    pgettext("collection", "New York")
    pgettext("collection", "Paris")
    pgettext("collection", "Philadelphie")
    pgettext("collection", "San Andrés")
    pgettext("collection", "San Francisco")
    pgettext("collection", "Seattle")
    pgettext("collection", "Strasbourg")
    pgettext("collection", "Washington")
