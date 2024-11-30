from django.shortcuts import render
from . import util


# Create your views here.
def home(request):
    return render(request, "roadmap/home.html")

def builds(request):
    return render(request, "roadmap/builds.html")

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

def spreadsheet(request):
    return render(request, "roadmap/spreadsheet.html")