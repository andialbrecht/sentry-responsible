from django import forms
from django.utils.translation import ugettext_lazy as _


class ResponsibleConfForm(forms.Form):
    send_mail = forms.BooleanField(
        initial=True, label=_('Send mail'), required=False,
        help_text=_('Send mail to assignee.'))
    tag_assignee = forms.BooleanField(
        initial=True, label=_('Tag assigned events'), required=False,
        help_text=_('If checked, assignees will be shown as tags.'))
