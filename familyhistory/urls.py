from django.urls import path, include
from familyhistory import views

app_name = 'fh'
urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),

    path('person/<int:person_id>', views.PersonView.as_view(), name="person_detail"),
    path('tree', views.TreeView.as_view(), name="tree"),
    path('person/search', views.SearchPageView.as_view(), name="person_search"),
    path('person/<int:person_id>/add-relationship/', views.AddRelationshipView.as_view(), name='add_relationship'),
    path('person/<int:related_person_id>/add-parent/', views.AddParentView.as_view(), name='add_parent'),

    path('surname/<str:surname>', views.SurnameView.as_view(), name="surname_detail"),


]