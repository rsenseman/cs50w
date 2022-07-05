from django.core import validators
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms



from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    return render(request, "encyclopedia/entry.html", {
        "entry": util.get_entry(title),
        "title": title,
    })

def search(request):
    search_term = request.GET.get('q')

    all_entries = set(util.list_entries())
    all_entries_lower = set([entry.lower() for entry in all_entries])

    if search_term.lower() in all_entries_lower:
        return HttpResponseRedirect(reverse('entry', args=[search_term]))
    else:
        return render(request, "encyclopedia/search.html", {
            "search_term": search_term,
            "entries": all_entries,
        })

def does_entry_already_exist(prospective_entry):
    all_entries = set(entry.lower() for entry in util.list_entries())
    return prospective_entry.lower() in all_entries

class NewEntryTitleField(forms.CharField):
    def validate(self, value):
        """Check if title value already exists."""
        # Use the parent's handling of required fields, etc.
        super().validate(value)
        if does_entry_already_exist(value):
            raise ValidationError(
                f"There is already an entry for {value}"
            )

class NewEntryForm(forms.Form):
    title = NewEntryTitleField(label="Entry Title", min_length=1)
    body = forms.CharField(label="Entry Body", min_length=1)

def create(request):
    if request.method == 'POST':
        form = NewEntryForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            print(title, body)

        else:
            print(form)
            return render(request, "encyclopedia/create.html", {
                'form': form
            })
    return render(request, "encyclopedia/create.html", {
        'form': NewEntryForm
    })
