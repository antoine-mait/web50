import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# road page

def list_entries():
    """
    Returns a list of all names of step entries.
    """
    _, filenames = default_storage.listdir("entries/road")
    return list(sorted(re.sub(r"\.html$", "", filename)
                for filename in filenames if filename.endswith(".html")))

def get_entry(title):
    """
    Retrieves an step entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/road/{title}.html")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None

# Stuffs pages 

def list_stuffs():
    """
    Returns a list of all names of step entries.
    """
    _, filenames = default_storage.listdir("entries/stuffs")
    return list(sorted(re.sub(r"\.html$", "", filename)
                for filename in filenames if filename.endswith(".html")))

def get_stuffs(title):
    """
    Retrieves an step entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/stuffs/{title}.html")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None

