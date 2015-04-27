from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views import generic

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.signals import user_logged_out

from .models import Kitty, UserKitty

def logged_in_message(sender, user, request, **kwargs):
    messages.info(request, "Welcome!")
user_logged_in.connect(logged_in_message)

def logged_out_message(sender, user, request, **kwargs):
    messages.info(request, "Goodbye!")
user_logged_in.connect(logged_in_message)
user_logged_out.connect(logged_out_message)

class LoggedInMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)

class IndexView(LoggedInMixin, generic.ListView):
    model = UserKitty
    template_name = 'kitties/index.html'
    context_object_name = 'user_kitties'

    def get_queryset(self):
        return UserKitty.objects.filter(user_id=self.request.user.id)

class DetailView(LoggedInMixin, generic.DetailView):
    model = Kitty
    template_name = 'kitties/detail.html'

class CatchView(LoggedInMixin, generic.ListView):
    model = Kitty
    template_name = 'kitties/catch.html'
    context_object_name = 'kitties'

    def get_queryset(self):
        return Kitty.objects.order_by('?')[:4]

def caught(request):
    new_kitty = get_object_or_404(Kitty, pk=request.POST['kitty'])
    UserKitty.objects.create(user=request.user, kitty=new_kitty)
    return HttpResponseRedirect(reverse('kittymon:index'))

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            messages.success(request, 'Signed up! Please login.')
            return HttpResponseRedirect(reverse('kittymon:index'))
        else:
            return render(request, "registration/register.html", {
                'form': form,
            })
    else:
        form = UserCreationForm()
        return render(request, "registration/register.html", {
            'form': form,
        })
