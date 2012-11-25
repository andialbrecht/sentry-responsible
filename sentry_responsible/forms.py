from django import forms
from django.utils.translation import ugettext_lazy as _


class ResponsibleConfForm(forms.Form):
    send_mail = forms.BooleanField(
        initial=True, label=_('Send mail'), required=False,
        help_text=_('Send mail to assignee'))
