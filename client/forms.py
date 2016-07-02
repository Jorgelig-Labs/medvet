# -*- coding: utf-8 -*-
from django import forms
from django.forms import Select
from client.models import Client

STATES = (('', ''), ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'), ('BA', 'Bahia'),
          ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'),
          ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'), ('PA', 'Pará'),
          ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'),
          ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'),
          ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'))


class ClientAdminForm(forms.ModelForm):

    def __init__(self, data=None, *args, **kwargs):
        super(ClientAdminForm, self).__init__(data, *args, **kwargs)
        self.fields['zipcode'].widget.attrs['onBlur'] = 'pesquisacep(this.value);'

    class Meta:
        model = Client

        fields = ['state']

        widgets = {
            'state': Select(choices=STATES),
        }

    class Media:
        js = ('client/js/cep.js',)
