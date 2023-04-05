from django.shortcuts import render
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Tesouro, User
from django.db.models import F, ExpressionWrapper, DecimalField, Sum
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.core import serializers
import json


class CreateUser(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'create_user.html'
    success_url = reverse_lazy('lista_tesouros')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return HttpResponseRedirect(self.success_url)


class SalvarTesouro(LoginRequiredMixin):
    model = Tesouro
    fields = ['nome', 'quantidade', 'preco', 'img_tesouro']
    template_name = 'salvar_tesouro.html'
    success_url = reverse_lazy('lista_tesouros')


class InserirTesouro(SalvarTesouro, CreateView):
    def form_valid(self, form):
        form.instance.pirata = self.request.user
        return super().form_valid(form)


class AtualizarTesouro(SalvarTesouro, UserPassesTestMixin, UpdateView):
    def test_func(self):
        return self.get_object().pirata == self.request.user

    def handle_no_permission(self):
        return HttpResponseRedirect(reverse_lazy('lista_tesouros'))


class RemoverTesouro(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Tesouro
    success_url = reverse_lazy('lista_tesouros')

    def test_func(self):
        return self.get_object().pirata == self.request.user

    def handle_no_permission(self):
        return HttpResponseRedirect(reverse_lazy('lista_tesouros'))


class ListarTesouros(LoginRequiredMixin, ListView):
    model = Tesouro
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        valor_total = ExpressionWrapper(F('preco') * F('quantidade'),
                                        output_field=DecimalField(max_digits=10, decimal_places=2))
        return user.tesouros.annotate(valor_total=valor_total)

    def get(self, request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponseRedirect(reverse('lista_tesouros'))

        object_qs = self.get_queryset()
        total_geral = object_qs.aggregate(total_geral=Sum('valor_total'))
        total_geral['total_geral'] = float(total_geral['total_geral'])

        object_list = list(object_qs.values('nome', 'quantidade', 'preco', 'img_tesouro', 'valor_total', 'id'))
        object_list.append(total_geral)

        return JsonResponse(object_list, status=200, safe=False)
