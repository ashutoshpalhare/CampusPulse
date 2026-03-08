from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Entry

CATEGORIES = ["Core","Operations","Growth","Archive", "extra item"]

def index(request):
    query = request.GET.get('q', '').strip()
    entries = Entry.objects.order_by('-created_at')
    if query:
        entries = entries.filter(title__icontains=query)
    return render(request, 'tracker/index.html', {'entries': entries, 'categories': CATEGORIES, 'query': query})

@require_POST
def create_entry(request):
    title = request.POST.get('title', '').strip()
    category = request.POST.get('category', CATEGORIES[0])
    if title and category in CATEGORIES:
        Entry.objects.create(title=title[:120], category=category)
    return redirect('index')

@require_POST
def delete_entry(request, pk):
    get_object_or_404(Entry, pk=pk).delete()
    return redirect('index')
