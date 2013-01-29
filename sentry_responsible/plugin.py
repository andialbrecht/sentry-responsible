from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

import sentry
from sentry.conf import settings
from sentry.filters.base import Filter
from sentry.models import TeamMember
from sentry.plugins import Plugin

from sentry_responsible import VERSION
from sentry_responsible.forms import ResponsibleConfForm
from sentry_responsible.models import Responsibility


class ResponsibleFilter(Filter):
    """Filter by responsibility."""
    label = _('Responsible')
    column = 'responsibility__user'

    def get_choices(self):
        choices = [('__unassigned__', u'[%s]' % _('Unassigned'))]
        choices.extend([(u.pk, u.get_full_name() or u.username)
                        for u in User.objects.exclude(responsibility=None)])
        return SortedDict(choices)

    def get_query_set(self, queryset):
        """Handle special values and let default implementation do the rest."""
        value = self.get_value()
        if value == '__unassigned__':
            return queryset.filter(responsibility__user=None)
        else:
            return super(ResponsibleFilter, self).get_query_set(queryset)


class ResponsiblePlugin(Plugin):
    title = _('Responsibilities')
    slug = 'responsible'
    description = _('Assign responsibilities for events.')
    version = VERSION

    conf_title = title
    conf_key = slug
    project_conf_form = ResponsibleConfForm

    author = 'Andi Albrecht'
    author_url = 'https://github.com/andialbrecht/sentry-responsible'

    resource_links = [
        (_('Bug Tracker'), 'https://github.com/andialbrecht/sentry-responsible/issues'),
        (_('Source Code'), 'https://github.com/andialbrecht/sentry-responsible'),
    ]

    def get_filters(self, project, **kwargs):
        return [ResponsibleFilter]

    def widget(self, request, group, **kwargs):
        resp = Responsibility.objects.filter(group=group)
        resp = resp.order_by('user__first_name', 'user__last_name',
        'user__username')
        resp = list(resp)

        available = group.project.team.member_set.exclude(
            user__in=[x.user for x in resp])

        if tuple(map(int, sentry.get_version().split('.')[:2])) >= (5, 3):
            # URL args changed in Sentry 5.3
            args = (group.project.team.slug, group.project.slug,
                    group.id, self.slug)
        else:
            args = (group.project.slug, group.id, self.slug)
        plugin_url = reverse('sentry-group-plugin-action', args=args)

        return self.render('sentry_responsible/widget.html', {
            'responsible': resp,
            'plugin_url': plugin_url,
            'available': list(available),
        })

    def view(self, request, group, **kwargs):
        if request.method == 'POST':
            self._update_responsibility(request, group)
        elif request.GET.get('remove', None):
            Responsibility.objects.remove_id(request.GET.get('remove'))
        return super(ResponsiblePlugin, self).view(request, group, **kwargs)

    def tags(self, request, group, tag_list, **kwargs):
        if not self.get_option('tag_assignee', group.project):
            return tag_list
        for resp in Responsibility.objects.filter(group=group):
            url = '%s?responsibility__user=%s' % (
                reverse('sentry', args=(group.project.slug,)), resp.user.id)
            username = resp.user.get_full_name() or resp.user.username
            tag_list.append(
                mark_safe('<a href="%s">%s</a>' % (url, escape(username))))
        return tag_list

    def _update_responsibility(self, request, group):
        """Updates the responsibility for a group."""
        user = request.POST.get('user', None)
        send_mail = self.get_option('send_mail', group.project)
        if send_mail is None:
            send_mail = True  # the default
        if user == 'full':
            Responsibility.objects.claim_full(group, request.user)
        else:
            try:
                user = group.project.team.member_set.get(user=user).user
            except TeamMember.DoesNotExist:
                return
            Responsibility.objects.add_user(group, user)
            if send_mail and user != request.user:
                self._send_mail(group, user)

    def _send_mail(self, group, user):
        subject_prefix = self.get_option('subject_prefix', group.project) or settings.EMAIL_SUBJECT_PREFIX
        subject = unicode(_('Responsibility assigned'))
        link = '%s/%s/group/%d/' % (settings.URL_PREFIX, group.project.slug, group.id)
        body = render_to_string('sentry_responsible/emails/notification.txt', {
            'link': link,
            'user': user,
        })
        msg = EmailMultiAlternatives(
            '%s%s' % (subject_prefix, subject),
            body,
            settings.SERVER_EMAIL,
            [user.email])
        msg.send()
