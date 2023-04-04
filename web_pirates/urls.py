"""web_pirates URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from pirates import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='lista_tesouros.html'), name="lista_tesouros"),
    path('listar/', views.ListarTesouros.as_view(), name='listar'),
    path('inserir/', views.InserirTesouro.as_view(), name="inserir"),
    path('editar/<int:pk>/', views.AtualizarTesouro.as_view(), name="editar"),
    path('remover/<int:pk>/', views.RemoverTesouro.as_view(), name="excluir"),
    path('login/', views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logon/', views.CreateUser.as_view(), name='logon'),
    path('logout/', views.LogoutView.as_view(next_page=views.reverse_lazy('login')), name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
