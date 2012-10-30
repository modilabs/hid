# encoding=utf-8
# maintainer: katembu

from django.forms import ModelForm
from hid.models import *


class IdentifierForm(ModelForm):

    class Meta:
        model = IdentifierRequest
