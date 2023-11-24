from django import forms
from django.shortcuts import render
from django.http import HttpResponse
from markdown2 import Markdown
from django.shortcuts import redirect
from random import choice

from . import util


# the function below is an umbrella function to convert md to html. it's calling content passed through util.py (content) and asking if there's anything there to convert.
def convert_md_to_html(title):
    content = util.get_entry(title) 
    markdowner = Markdown()
    if content == None:
        return None
    else:
        return markdowner.convert(content)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    html_content = convert_md_to_html(title)
    if html_content == None:
        return render(request, "encyclopedia/error.html", {
            "message": "This entry does not exist."
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": html_content
        }) 

# defining search function
def search(request):
    entries = util.list_entries()
    # list is a sequence of values that can be changed
    find_entries = list()
    
    # label q for the variable in layout.html
    entry_search = request.GET.get("q")

    if entry_search in entries:
        return redirect(entry, entry_search)
    results = [entry for entry in entries if entry_search.lower() in entry.lower()]
    return render(request, "encyclopedia/index.html", {
        "entries": results,
    })

 
class AddPageForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea(
        attrs={
            "class": "form-control",
        }))

def add_page(request):
    form = AddPageForm() # <- called at GET request
    if request.method == "POST":
        form = AddPageForm(request.POST) # <- called at POST request
    
    if form.is_valid():
        title = form.cleaned_data['title']
        content = form.cleaned_data['content']
        entries = util.list_entries()
        for entry in entries:
            if title.upper() == entry.upper():
                return render(request, "encyclopedia/error.html")
        util.save_entry(title, content)
        return redirect('entry', title=title) 
    else:
        return render(request, "encyclopedia/addpage.html", {
            "form": AddPageForm()
        })

class AddPageForm(forms.Form):
    title = forms.CharField(max_length=20)
    content = forms.CharField(widget=forms.Textarea(
        attrs={
            "class": "form-control",
            "placeholder": "Tell us more!"
        }))

def edit_page(request, title):
    if request.method == "GET":
        content = util.get_entry(title)
        form = AddPageForm(initial={"title": title, "content": content})
    
    else:
        form = AddPageForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            util.save_entry(title, content)
            return redirect('encyclopedia:entry', title)
    return render(request, 'encyclopedia/editpage.html', {'form': form})


def random_page(request):
    return redirect('encyclopedia:entry', choice(util.list_entries())            
        )

#  redirect to entry view rather than use the random.html