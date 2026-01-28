from django.urls import path, include
from . import views as data_views

app_name = 'fh_data'
urlpatterns = [
    path('tree/<int:person_id>', data_views.FamilyTreeDataView.as_view(), name="person_tree"),

]