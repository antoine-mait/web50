from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, "roadmap/home.html")

def builds(request):
    return render(request, "roadmap/builds.html")

def roadmap(request):
    return render(request, "roadmap/roadmap.html")

def spreadsheet(request):
    return render(request, "roadmap/spreadsheet.html")