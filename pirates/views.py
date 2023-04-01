from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Tesouro, User
from django.db.models import F, ExpressionWrapper, DecimalField, Sum
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect


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


class AtualizarTesouro(SalvarTesouro, UpdateView):
    def form_valid(self, form):
        form.instance.pirata = self.request.user
        return super().form_valid(form)


class RemoverTesouro(LoginRequiredMixin, DeleteView):
    model = Tesouro
    success_url = reverse_lazy('lista_tesouros')


class ListarTesouros(LoginRequiredMixin, ListView):
    model = Tesouro
    template_name = 'lista_tesouros.html'

    def get_queryset(self):
        user = self.request.user
        valor_total = ExpressionWrapper(F('preco') * F('quantidade'),
                                        output_field=DecimalField(max_digits=10, decimal_places=2))
        return user.tesouros.annotate(valor_total=valor_total)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(context['object_list'].aggregate(total_geral=Sum('valor_total',
                                                                        output_field=DecimalField(max_digits=10,
                                                                                                  decimal_places=2))))
        return context
