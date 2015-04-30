from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.signals import user_logged_out
from django.contrib import messages
from django.db.models import Count
from .models import Kitty, UserKitty, User
import newrelic.agent

class LoggedInMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)

class KittyList(generic.ListView):
    def get_context_data(self, **kwargs):
            context = super(KittyList, self).get_context_data(**kwargs)
            top10 = User.objects.annotate(kitty_count=Count('userkitty')).order_by('-kitty_count')[:10]
            context['leaders'] = top10
            return context

class HomeView(generic.TemplateView):
    template_name = 'kitties/home.html'

class IndexView(LoggedInMixin, KittyList):
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
    newrelic.agent.add_custom_parameter("caught_kitty", new_kitty.id)
    newrelic.agent.add_custom_parameter("catching_user", request.user.id)
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

def logged_in_message(sender, user, request, **kwargs):
    messages.success(request, "Logged in successfully!")
user_logged_in.connect(logged_in_message)

def logged_out_message(sender, user, request, **kwargs):
    messages.warning(request, "Logged out!")
user_logged_in.connect(logged_in_message)
user_logged_out.connect(logged_out_message)
