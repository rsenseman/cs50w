from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path(r'search', views.search, name='search'),
    path(r'create', views.create, name='create'),
    path('<str:title>', views.entry, name='entry'),
]
