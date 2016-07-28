# -*- coding: UTF-8 -*-
import re

from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template import loader
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils.http import int_to_base36

from models import User, UserProfile
from views import update_user

USER_EDIT = 'user_edit'
USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'
USER_NEW = 'user_new'


class FormUserValidation(TestCase):

    user = ''

    def setUp(self):
        """ Authentication and variables to start each test """

        self.user = User.objects.create_superuser(username=USER_USERNAME, email='jenkins.neuromat@gmail.com',
                                                  password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.force_password_change = False
        profile.save()

        self.group = Group.objects.create(name='group')
        self.group.save()

        self.factory = RequestFactory()

        self.data = {'username': ['username'],
                     'first_name': ['General'],
                     'last_name': ['Test'],
                     'password': ['Adm!123'],
                     'password2': ['Adm!123'],
                     'groups': [self.group.id],
                     'email': ['email@test.com'],
                     'action': 'save'}

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

    def reset(self, user_added=None, request=None, domain_override=None,
              email_template_name='registration/password_reset_email.html',
              use_https=False, token_generator=default_token_generator):

        """Reset users password"""
        if not user_added.email:
            raise ValueError('Email address is required to send an email')

        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override

        loader.get_template(email_template_name)

        context = {
            'email': user_added.email,
            'domain': domain,
            'site_name': site_name,
            'uid': int_to_base36(user_added.id),
            'user': user_added,
            'token': token_generator.make_token(user_added),
            'protocol': use_https and 'https' or 'http',
        }

        subject_template_name = 'registration/password_reset_subject.txt'
        subject = loader.render_to_string(subject_template_name, context)

        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        plain_text_content = loader.render_to_string(email_template_name.replace('with_html', 'plaintext'), context)
        html_content = loader.render_to_string(email_template_name, context)

        from django.core.mail import EmailMultiAlternatives

        msg = EmailMultiAlternatives(subject, plain_text_content, 'jenkins.neuromat@gmail.com', [user_added.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def test_user_password_pattern(self):
        """Test of the pattern """
        # Pattern details
        # (			# Start of group
        # (?=.*\d)		#   must contains one digit from 0-9
        # (?=.*[a-z])		#   must contains one lowercase characters
        # (?=.*[A-Z])		#   must contains one uppercase characters
        # (?=.*[@#$%])		#   must contains one special symbols in the list "@#$%"
        # .		#     match anything with previous condition checking
        # {6,20}	#        length at least 6 characters and maximum of 20
        # )
        pattern = '((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%]).{6,20})'
        password = "abcC2@!$"

        self.assertTrue(self.confirm_password(pattern, password), True)

    def confirm_password(self, pattern, password):
        return re.compile(pattern).match(password)

    def test_user_invalid_username(self):
        """
        Invalid username test
        """

        self.data['username'] = ''

        response = self.client.post(reverse(USER_NEW), self.data, follow=True)

        self.assertFormError(response, "form", "username", 'Este campo é obrigatório.')
        self.assertEqual(User.objects.filter(username='').count(), 0)

    def test_user_invalid_email(self):
        """
        Invalid email test
        """

        self.data['email'] = 'email@invalid.'

        response = self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertFormError(response, "form", "email", 'Informe um endereço de email válido.')
        self.assertEqual(User.objects.filter(username='').count(), 0)

    def test_user_passwords_doesnt_match(self):
        """
        Passwords do not match test
        """
        user_pwd = 'test_pwd'
        self.data['username'] = user_pwd
        self.data['password'] = 'abc123'
        self.data['password2'] = 'acc123'

        self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertEqual(User.objects.filter(username=user_pwd).count(), 1)

    def test_user_password_check_valid_pattern(self):
        """
        Valid password test
        """
        user_pwd = 'test_pwd_1'
        pattern = '((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%]).{6,20})'
        password = 'Abc$123'
        self.assertTrue(self.confirm_password(pattern=pattern, password=password), True)

        self.data['username'] = user_pwd
        self.data['password'] = password

        self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertEqual(User.objects.filter(username=user_pwd).count(), 1)

    def test_user_password_check_invalid_pattern_abc(self):
        """
        Invalid password
        """
        user_pwd = 'test_pwd_1'
        self.data['username'] = user_pwd
        self.data['password'] = 'abc'

        self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertEqual(User.objects.filter(username=user_pwd).count(), 1)

    def test_user_password_check_invalid_pattern_123(self):
        """
        Invalid password
        """
        user_pwd = 'test_pwd_1'
        self.data['username'] = user_pwd
        self.data['password'] = '123'

        self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertEqual(User.objects.filter(username=user_pwd).count(), 1)

    def test_user_empty_password(self):
        """
        Empty password test
        """
        user_pwd = 'test_pwd_2'
        self.data['username'] = user_pwd
        self.data['password'] = ''

        response = self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "password", 'Este campo é obrigatório.')
        self.assertEqual(User.objects.filter(username=user_pwd).count(), 0)

    def test_user_create(self):
        """
        Add new user test
        """
        username = 'test_username'
        self.data['username'] = username

        response = self.client.post(reverse(USER_NEW), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.filter(username=username).count(), 1)

    def test_user_create_mail_password_define(self):
        """
        Add new user test
        """
        username = 'test_username'
        self.data['email'] = 'romulojosefranco@gmail.com'
        self.data['username'] = username

        # Create an instance of a GET request.
        request = self.factory.get(reverse(USER_EDIT, args=[self.user.pk]))
        request.user = self.user

        response = self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username=username).count(), 1)

        user_added = User.objects.filter(username=username).first()
        self.reset(user_added, request)

    def test_user_read(self):
        """
        View user test
        """

        # Create an instance of a GET request.
        request = self.factory.get(reverse(USER_EDIT, args=[self.user.pk]))
        request.user = self.user

        # Test view() as if it were deployed at /quiz/patient/%id
        response = update_user(request, user_id=self.user.pk)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse(USER_EDIT, args=[self.user.pk]), self.data)
        self.assertEqual(response.status_code, 302)

    def test_update_user_get(self):
        """
        Update user - Using GET
        """

        # Create an instance of a GET request.
        request = self.factory.get(reverse(USER_EDIT, args=[self.user.pk]))
        request.user = self.user

        # Test view() as if it were deployed at /quiz/patient/%id
        response = update_user(request, user_id=self.user.pk)
        self.assertEqual(response.status_code, 200)

    def test_update_user_post(self):
        """
        Update user - using POST
        """

        first_name = 'test_username'
        self.data['first_name'] = first_name

        response = self.client.post(reverse(USER_EDIT, args=(self.user.pk,)), self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(id=self.user.pk).count(), 1)

        user_first_name = User.objects.filter(id=self.user.pk).first()

        self.assertEqual(user_first_name.first_name, first_name)

    def test_user_remove(self):
        """
        Delete user
        """
        user_str = 'user_remove'
        user_to_delete = User.objects.create_user(username=user_str, email='test@delete.com',
                                                  password='Del!123')
        user_to_delete.is_staff = True
        user_to_delete.is_superuser = True
        user_to_delete.is_active = True
        user_to_delete.save()
        self.assertEqual(User.objects.filter(username=user_str).count(), 1)

        self.data['action'] = 'remove'

        response = self.client.post(reverse(USER_EDIT, args=(user_to_delete.pk,)), self.data, follow=True)

        self.assertEqual(response.status_code, 200)
        user_to_delete = get_object_or_404(User, pk=user_to_delete.pk)
        self.assertEqual(user_to_delete.is_active, False)

        # Create an instance of a GET request.
        request = self.factory.get(reverse(USER_EDIT, args=[user_to_delete.pk, ]))
        request.user = self.user

        response = update_user(request, user_id=user_to_delete.pk)
        self.assertEqual(response, None)