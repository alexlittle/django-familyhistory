from django.urls import path
from . import views as data_views

app_name = 'fh_data'
urlpatterns = [
    path('tree/<int:start_person_id>', data_views.FamilyTreeDataView.as_view(), name="person_tree"),
    path('tree', data_views.FamilyTreeDataView.as_view(), name="tree"),
    path('person/search', data_views.search_people, name="person_search"),

]