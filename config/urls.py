from django.urls import path
from tracker import views
urlpatterns = [path('', views.index, name='index'), path('entries/', views.create_entry, name='create'), path('entries/<int:pk>/delete/', views.delete_entry, name='delete')]
