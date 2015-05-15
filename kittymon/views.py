from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.utils.decorators import method_decorator
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.signals import user_logged_out
from django.contrib import messages
from django.db.models import Count
from .models import Kitty, UserKitty, User

import newrelic.agent
import requests

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
        kitties = UserKitty.objects.filter(user_id=self.request.user.id)
        paginator = Paginator(kitties, 20)
        page = self.request.GET.get('page')

        try:
          kitties = paginator.page(page)
        except PageNotAnInteger:
          kitties = paginator.page(1)
        except EmptyPage:
          kitties = paginator.page(paginator.num_pages)
        return kitties

class BattleKitties(generic.DetailView):
    def get_context_data(self, **kwargs):
        context = super(BattleKitties, self).get_context_data(**kwargs)

        hero = self.request.user
        hero_userkitty = hero.userkitty_set.filter(kitty_id=context['kitty'].id).order_by('?')[0]
        hero_kitty_url = hero_userkitty.kitty.url

        villain = User.objects.exclude(id=hero.id).order_by('?')[0]
        villain_userkitty = villain.userkitty_set.order_by('?')[0]
        villain_kitty_url = villain_userkitty.kitty.url

        context['hero_name'] = hero.username
        context['hero_userkitty_id'] = hero_userkitty.id
        context['hero_kitty_url'] = hero_kitty_url

        context['villain_name'] = villain.username
        context['villain_userkitty_id'] = villain_userkitty.id
        context['villain_kitty_url'] = villain_kitty_url

        return context

class DetailView(LoggedInMixin, BattleKitties):
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
    newrelic.agent.add_custom_parameter("caught_kitty", new_kitty.url)
    newrelic.agent.add_custom_parameter("catching_user", request.user.username)
    UserKitty.objects.create(user=request.user, kitty=new_kitty)
    return HttpResponseRedirect(reverse('kittymon:index'))

def fight(request, hero_userkitty_id, villain_userkitty_id):
    hero_userkitty = UserKitty.objects.get(id=hero_userkitty_id)
    hero_kitty = hero_userkitty.kitty

    villain_userkitty = UserKitty.objects.get(id=villain_userkitty_id)
    villain_kitty = villain_userkitty.kitty

    payload = { 'contenders' : [hero_kitty.url, villain_kitty.url] }

    kfaas = settings.FAAS_URL
    newrelic.agent.add_custom_parameter('kfaas', kfaas)

    response = requests.post("{faas_url}/fight".format(faas_url=kfaas), data=payload)

    if response.text == hero_kitty.url:
        newrelic.agent.add_custom_parameter("battle_winner", hero_userkitty.user.username)
        newrelic.agent.add_custom_parameter("battle_loser", villain_userkitty.user.username)
        messages.success(request, "You defeated {villain} and stole their kitty!".format(villain=villain_userkitty.user.username))
        villain_userkitty.user_id = hero_userkitty.user_id
        villain_userkitty.save()
    else:
        newrelic.agent.add_custom_parameter("battle_winner", villain_userkitty.user.username)
        newrelic.agent.add_custom_parameter("battle_loser", hero_userkitty.user.username)
        messages.warning(request, "You were defeated by {villain} and lost your kitty!".format(villain=villain_userkitty.user.username))
        hero_userkitty.user_id = villain_userkitty.user_id
        hero_userkitty.save()

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
