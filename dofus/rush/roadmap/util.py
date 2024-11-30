import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of step entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.html$", "", filename)
                for filename in filenames if filename.endswith(".html")))


def save_entry(title, content):
    """
    Saves an step entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.html"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an step entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.html")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None
