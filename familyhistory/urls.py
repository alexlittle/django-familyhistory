from django.urls import path, include
from familyhistory import views as fh_views

app_name = 'fh'
urlpatterns = [
    path('', fh_views.HomeView.as_view(), name="home"),
    path('person/<int:person_id>', fh_views.HomeView.as_view(), name="person_detail"),
]