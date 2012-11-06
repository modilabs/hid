# encoding=utf-8
# maintainer: katembu

from django.forms import ModelForm
from django import forms
from django.forms.widgets import CheckboxInput
from django.contrib.auth.models import User
from hid.models import *


class IdentifierForm(ModelForm):

    class Meta:
        model = IdentifierRequest


class SiteChoice(forms.Form):
    for_site = forms.ChoiceField(widget=forms.Select,
                                 label="Select Site",
                                 required=True)

    def __init__(self, username):
        self.username = username
        super(SiteChoice, self).__init__()
        user = User.objects.get(username=username)
        choices = [(u.site, u.site.name) for u in SitesUser.objects
                   .filter(user=user)]
        self.fields['for_site'].choices = choices
