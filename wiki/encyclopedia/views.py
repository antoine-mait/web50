from django.shortcuts import render
import markdown
from . import util

def markdown_convert(title):
    content = util.get_entry(title)
    markdowner = markdown.Markdown()
    if content == None : 
        return None
    else:
        return markdowner.convert(content)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    html_content = markdown_convert(title)
    if html_content == None:
        return render(request, "encyclopedia/error.html",{
            "message": "This entry doesn't exist"
        })
    else:
        return render(request, "encyclopedia/entry.html" ,{
                      "title":title,
                      "content": html_content,
        })