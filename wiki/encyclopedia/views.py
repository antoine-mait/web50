from django.shortcuts import render
from . import util

import random
import markdown

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def convert_md(title):
    content = util.get_entry(title)
    markdowner = markdown.Markdown()
    if content == None:
        return None
    else : 
        return markdowner.convert(content)
    
def entry(request, title):
    content = convert_md(title)
    if content == None:
        return render(request,"encyclopedia/error.html", {
            "message": "Entry doesn't exist"
        })
    else:
        return render(request,"encyclopedia/entry.html", {
            "title": title,
            "content": content,
    })

def search(request):
    if request.method == "POST" :
        entry_search = request.POST["q"]
        html_content = convert_md(entry_search)
        if html_content is not None:
            return render(request, "encyclopedia/entry.html" ,{
            "title":entry_search,
            "content": html_content,
            })
        else:
            allEntries = util.list_entries()
            recommendation = []
            for entry in allEntries:
                if entry_search.lower() in entry.lower():
                    recommendation.append(entry)
            return render(request, "encyclopedia/search.html",{
                "recommendation" : recommendation,
            } )

def new_page(request):
    if request.method == "GET":
        return render(request, "encyclopedia/new_page.html")
    else:
        title = request.POST["title"]
        content = request.POST["content"]
        titleExist = util.get_entry(title)
        if titleExist is not None: 
            return render(request, "encyclopedia/error.html",{
                          "message":"Entry page already exists"
                          })
        else:
            util.save_entry(title, content)
            html_content= convert_md(title)
            return render(request, "encyclopedia/entry.html",{
                "title":title,
                "content":html_content,
            })

def edit(request):
    if request.method == "POST":
        title = request.POST["entry_title"]
        content = util.get_entry(title)
        return render(request,"encyclopedia/edit.html",{
            "title": title,
            "content": content, 
        })
            
def save_edit(request):
    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["content"]
        util.save_entry(title, content)
        html_content = convert_md(title)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": html_content,
        })   

def random_page(request):
    allEntries = util.list_entries()
    title = random.choice(allEntries)
    html_content = convert_md(title)
    return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": html_content,
        })   
