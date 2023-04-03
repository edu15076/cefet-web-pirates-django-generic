from django.test import TestCase
from .views import *
from .models import *
from django.urls import reverse
from django.test.client import Client
from django.contrib import auth
from django.core.exceptions import ValidationError
import shutil
import os
from io import BytesIO


class TestModels(TestCase):
    pass


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()

        self.test_user = User.objects.create_user(username='test')
        self.test_user.set_password('asdfpoin')
        self.test_user.save()
        self.test_user1 = User.objects.create_user(username='test1')
        self.test_user1.set_password('asdfpoin')
        self.test_user1.save()

        self.image = BytesIO(
            b"GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00"
            b"\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x00\x00"
        )
        self.image.name = "myimage.gif"

        self.tesouros = [
            Tesouro.objects.create(nome='a', quantidade=12, preco=9.9, img_tesouro=self.image.name, pirata=self.test_user),
            Tesouro.objects.create(nome='b', quantidade=13, preco=7, img_tesouro=self.image.name, pirata=self.test_user),
            Tesouro.objects.create(nome='a1', quantidade=24, preco=19.8, img_tesouro=self.image.name, pirata=self.test_user1),
            Tesouro.objects.create(nome='b1', quantidade=26, preco=14, img_tesouro=self.image.name, pirata=self.test_user1)
        ]

    def tearDown(self):
        shutil.rmtree(os.getcwd() + '/media/imgs')
        os.mkdir(os.getcwd() + '/media/imgs')

    def test_create_user(self):
        self.client.post(reverse('logon'), {'username': 'user', 'password1': 'asdfpokm', 'password2': 'asdfpokm'})
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated, 'User is not being authenticated after logon.')

    def test_inserir_tesouro(self):
        self.client.login(username='test', password='asdfpoin')
        self.client.post(reverse('inserir'), {'nome': 'tesouro', 'quantidade': 10,
                                              'preco': 1, 'img_tesouro': self.image})
        self.assertEqual(self.test_user.tesouros.last(), Tesouro.objects.last(), 'Treasure not inserted.')

    def test_atualizar_tesouro(self):
        self.client.login(username='test', password='asdfpoin')
        edit_url = reverse('editar', kwargs={'pk': self.tesouros[0].id})
        self.client.post(edit_url, {'nome': 'u', 'quantidade': 12, 'preco': 9.9, 'img_tesouro': self.image})
        self.assertTrue(self.test_user.tesouros.filter(nome='u').exists(), 'Treasure could not be edited.')

    def test_remover_tesouro(self):
        self.client.login(username='test', password='asdfpoin')
        self.client.post(reverse('excluir', kwargs={'pk': self.tesouros[0].id}))
        self.assertEqual(len(self.test_user.tesouros.all()), 1, 'Treasure was not deleted.')

        self.client.post(reverse('excluir', kwargs={'pk': self.tesouros[3].id}))
        self.assertEqual(len(self.test_user1.tesouros.all()), 2, 'Treasure of other user should not be deleted.')

    def test_lista_tesouros(self):
        self.client.login(username='test', password='asdfpoin')
        response = self.client.get(reverse('lista_tesouros'))
        tesouros = response.context['object_list']

        self.assertEqual(len(tesouros), len(self.test_user.tesouros.all()), 'There isn\'t the same number of '
                                                                            'treasures being displayed and saved in '
                                                                            'the data base.')

        for tesouro in self.test_user.tesouros.all():
            if tesouro not in tesouros:
                self.fail('There is one or more treasures not being shown.')
