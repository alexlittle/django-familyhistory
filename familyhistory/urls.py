from django.urls import path, include
from familyhistory import views

app_name = 'fh'
urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),

    path('person/<int:person_id>', views.PersonView.as_view(), name="person_detail"),
    path('person/<int:person_id>/tree', views.TreeView.as_view(), name="person_tree"),

    path('surname/<str:surname>', views.SurnameView.as_view(), name="surname_detail"),

    path('api/', include('familyhistory.api.urls'))
]