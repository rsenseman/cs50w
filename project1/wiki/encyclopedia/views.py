from django.core import validators
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms

from . import util

import markdown2
from random import choice


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    return render(request, "encyclopedia/entry.html", {
        "entry": markdown2.markdown(util.get_entry(title)),
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
                f"There is already an entry for {value}. Duplicates "
                "and/or overwrites not permitted from create UI"
            )

class NewEntryForm(forms.Form):
    title = NewEntryTitleField(label="Entry Title", min_length=1)
    body = forms.CharField(label="Entry Body", min_length=1)

def create(request):
    if request.method == 'POST':
        form = NewEntryForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():
            title, body = form.cleaned_data['title'], form.cleaned_data['body']
            util.save_entry(
                title,
                body
            )
            return HttpResponseRedirect(reverse('entry', args=[title]))
        else:
            print(form)
            return render(request, "encyclopedia/create.html", {
                'form': form
            })
    return render(request, "encyclopedia/create.html", {
        'form': NewEntryForm
    })


def make_edit_form(entry_title, entry_content):
    class EditEntryForm(forms.Form):
        title = forms.CharField(
            label="Entry Title",
            initial=entry_title,
            widget=forms.TextInput(attrs={
                'value':entry_title,
                'disabled':None,
            })
        )

        body = forms.CharField(
            label="Entry Body",
            min_length=1,
            widget=forms.TextInput(attrs={
                'value':entry_content,
            })
        )
    return EditEntryForm

def is_content_valid():
    return True

def edit(request):
    if request.method == 'POST':
        print(request.POST)
        title = request.POST.get('title')
        content = request.POST.get('body')

        print(title, content)
        # Check if form data is valid (server-side)
        if is_content_valid():
            util.save_entry(
                title,
                content
            )
            return HttpResponseRedirect(reverse('entry', args=[title]))
        else:
            form = make_edit_form(title, content)
            return render(request, "encyclopedia/edit.html", {
                'form': form
            })
    else:
        title = request.GET.get('title')
        content = util.get_entry(title)

        edit_form = make_edit_form(title, content)

        return render(request, "encyclopedia/edit.html", {
            'form': edit_form,
            'title': title,
            'content': content,
        })

def random(request):
    all_entries = util.list_entries()
    random_entry = choice(all_entries)
    return HttpResponseRedirect(reverse('entry', args=[random_entry]))
