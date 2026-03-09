from django.urls import path
from tracker import views
urlpatterns = [path('', views.index, name='index'), path('entries/', views.create_entry, name='create'), path('entries/<int:pk>/delete/', views.delete_entry, name='delete')]
# helper: small utility for StudentManagement System
def _placeholder_util():
    return True

def get_status():
    """Return simple status dict."""
    return {"ok": True, "service": "StudentManagement System"}
