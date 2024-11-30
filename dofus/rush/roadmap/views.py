from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup

from . import util

import os

# Create your views here.
def home(request):
    return render(request, "roadmap/home.html")

def spreadsheet(request):
    return render(request, "roadmap/spreadsheet.html")

def roadmap(request):
    entries = util.list_entries()
    entry_content = {}

    # Create a dictionary with entry titles as keys and their contents as values
    for entry in entries:
        title = entry
        entry_content[title] = util.get_entry(title)

    return render(request, "roadmap/roadmap.html", {
        "entries": entries,
        "entry_content": entry_content,  # Pass the dictionary of contents
    })

def builds(request):
    entries = util.list_stuffs()
    entry_content = {}

    # Create a dictionary with entry titles as keys and their contents as values
    for entry in entries:
        title = entry
        entry_content[title] = util.get_stuffs(title)

    # Path to your images folder
    image_folder = 'roadmap/static/images/stuffs'
    image_files = os.listdir(image_folder)
    image_files = [f for f in image_files if f.endswith(('.jpg', '.png', '.gif'))]  # Filter for image files

    return render(request, "roadmap/stuffs.html", {
        "entries": entries,
        "entry_content": entry_content,  # Pass the dictionary of contents
        'image_files': image_files,
    })
