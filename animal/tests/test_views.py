# -*- coding: utf-8 -*-
from datetime import timedelta
from django.contrib.auth.models import User
from django.core.urlresolvers import resolve
from django.test import TestCase

from animal.views import *
from animal.models import *

USER_USERNAME = 'user'
USER_PWD = 'mypassword'
USER_EMAIL = 'user@example.com'


class AnimalTest(TestCase):
    def setUp(self):
        """
        Configure authentication and variables to start each test
        """

        self.user = User.objects.create_user(username=USER_USERNAME, email=USER_EMAIL, password=USER_PWD)
        self.user.is_staff = True
        self.user.save()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

        client = Client.objects.create(name='Fulano de Tal')
        specie = Specie.objects.create(name='Felina')
        breed = Breed.objects.create(specie=specie, name='Maine Coon')
        Animal.objects.create(owner=client, specie=specie, breed=breed, animal_name='Bidu', fur='l')

    def test_animal_new_status_code(self):
        url = reverse('animal_new')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'animal/animal_new.html')

    def test_animal_new_url_resolves_animal_new_view(self):
        view = resolve('/animal/new')
        self.assertEquals(view.func, animal_new)

    def test_animal_view_status_code(self):
        animal = Animal.objects.first()
        url = reverse('animal_view', args=(animal.id,))
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'animal/animal_tabs.html')

    def test_animal_view_url_resolves_anima_view_view(self):
        view = resolve('/animal/view/1/')
        self.assertEquals(view.func, animal_view)

    def test_animal_update_status_code(self):
        animal = Animal.objects.first()
        url = reverse('animal_edit', args=(animal.id,))
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'animal/animal_tabs.html')

    def test_animal_update_url_resolves_animal_update_view(self):
        view = resolve('/animal/edit/1/')
        self.assertEquals(view.func, animal_update)

    def test_create_animal(self):
        client = Client.objects.create(name='John')
        specie = Specie.objects.create(name='Canina')
        breed = Breed.objects.create(specie=specie, name='Golden')
        animal = Animal.objects.create(owner=client, specie=specie, breed=breed, animal_name='Teddy', fur='l')
        self.assertTrue(isinstance(animal, Animal))
        self.assertEqual(animal.__str__(), animal.animal_name)
        self.assertEqual(animal.age(), None)

    def test_create_animal_with_birthdate(self):
        client = Client.objects.create(name='Bill')
        specie = Specie.objects.create(name='Canina')
        breed = Breed.objects.create(specie=specie, name='Golden')
        animal = Animal.objects.create(owner=client, specie=specie, breed=breed, animal_name='Laika', fur='l',
                                       birthdate=datetime.date.today()-timedelta(days=740))
        self.assertTrue(isinstance(animal, Animal))
        self.assertEqual(animal.__str__(), animal.animal_name)
        self.assertEqual(animal.age(), 2)