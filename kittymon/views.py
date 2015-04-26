from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views import generic

from .models import Kitty

class IndexView(generic.ListView):
    model = Kitty
    template_name = 'kitties/index.html'
    context_object_name = 'kitties'

    def get_queryset(self):
        return Kitty.objects.all()

class DetailView(generic.DetailView):
    model = Kitty
    template_name = 'kitties/detail.html'

class CatchView(generic.ListView):
    model = Kitty
    template_name = 'kitties/catch.html'
    context_object_name = 'kitties'

    def get_queryset(self):
        return Kitty.objects.order_by('?')[:4]

def caught(request):
    kitty = get_object_or_404(Kitty, pk=request.POST['kitty'])
    return render(request, 'kitties/detail.html', {'kitty': kitty})
    return HttpResponseRedirect(reverse('kittymon:detail', args=(kitty.id,)))
