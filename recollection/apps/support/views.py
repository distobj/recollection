from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext

from django_redmine.utils import RedmineClient, RedmineIssue
from django_redmine.consts import *

from recollection.utils.views import get_akara_version
from freemix.transform.conf import AKARA_URL_PREFIX
from freemix import __version__ as freemix_version
from freemix.utils import get_user, get_site_url
from freemix.dataprofile.models import create_dataset

from recollection import __version__ as recollection_version
from recollection.apps.support import forms
from recollection.apps.support import models

def redmine_create_issue(project_id, subject, description, tracker, author,
                         status = None,
                         priority = None,
                         assigned_to = None,
                         fixed_version = None,
                         parent = None,
                         start_date = None,
                         due_date = None,
                         done_ratio = None,
                         estimated_hours = None):
    """
    Generic method for creating an issue in an associated Redmine
    installation.  Unlikely to be directly useful.  No provision
    for custom fields for the time being.
    """
    c = RedmineClient(settings.REDMINE_URL,
                      settings.REDMINE_USER,
                      settings.REDMINE_PASSWORD,
                      settings.REDMINE_KEY)

    issue = RedmineIssue(None)
    issue.set_project(project_id)
    issue.add_element('subject', value = subject)
    issue.add_element('description', value = description)
    issue.add_element('tracker', tracker)
    issue.add_element('author', author)
    if status is not None:
        issue.add_element('status', status)
    if priority is not None:
        issue.add_element('priority', priority)
    if assigned_to is not None:
        issue.add_element('assigned_to', assigned_to)
    if fixed_version is not None:
        issue.add_element('fixed_version', fixed_version)
    if parent is not None:
        issue.add_element('parent', parent)
    if start_date is not None:
        issue.add_element('start_date', value = start_date)
    if due_date is not None:
        issue.add_element('due_date', value = due_date)
    if done_ratio is not None:
        issue.add_element('done_ratio', value = done_ratio)
    if estimated_hours is not None:
        issue.add_element('estimated_hours', value = estimated_hours)

    return c.create_issue(issue)

class RedmineIssueView(object):
    """
    A generic view for generating a redmine issue based on submitted form contents

        `template`: the presentation of the issue form
        `issue_template`: used to generate the description for the new issue
        `form_class`: a subclass of `forms.SupportIssueForm`
    """

    create_template="support/create_issue.html"
    issue_template="support/description.html"
    response_template="support/issue_response.html"

    form_class=forms.SupportIssueForm

    def __init__(self, *args, **kwargs):
        self.form_class = kwargs.get("form_class", self.form_class)
        self.issue_template = kwargs.get("issue_template", self.issue_template)
        self.create_template = kwargs.get("create_template", self.create_template)
        self.response_template = kwargs.get("response_template", self.response_template)

    def __call__(self, request, *args, **kwargs):
        if request.method == "POST":
            form = self.form_class(request.POST)
            if form.is_valid():
                return self.create_issue(request, form,  *args, **kwargs)
        else:
            initial = {}
            if request.user.email:
                initial["contact_email"] = request.user.email
                initial["contact_type"] = "email"
            form = self.form_class(initial=initial)
        return render_to_response(self.create_template, {'form': form},
                                  context_instance=RequestContext(request))

    def generate_context(self, request, form):
        return dict(form.cleaned_data, **{
            'submitting_user_name': request.user.get_profile().name or request.user.username,
            'submitting_user_profile': get_site_url(reverse('profile_detail',
                                                            kwargs={'username':
                                                                    request.user.username})),
            'system_name': '%s %s' % (settings.SITE_NAME, settings.SITE_NAME_STATUS),
            'system_link': get_site_url(),
            'system_info': '%s %s - Freemix %s - Akara %s - Akara Root %s' %
            (settings.SITE_NAME,
             recollection_version,
             freemix_version,
             get_akara_version(),
             AKARA_URL_PREFIX,)
        })

    def issue_subject(self, context):
        return "New Issue"

    def create_issue(self, request, form, *args, **kwargs):
        t = loader.get_template(self.issue_template)

        c = RequestContext(request, self.generate_context(request, form))
        subject = self.issue_subject(c)
        description = t.render(c)
        issue_id = redmine_create_issue(settings.REDMINE_PROJECT_ID,
                                  subject,
                                  description,
                                  REDMINE_CONSTS['TRACKER']['SUPPORT'],
                                  settings.REDMINE_USER_ID)
        return render_to_response(self.response_template,
                                  {'issue_id': issue_id,
                                   'issue_link':  '%s/issues/%s' % (settings.REDMINE_URL, issue_id) },
                                 context_instance=RequestContext(request))

class AugmentationIssueView(RedmineIssueView):
    create_template="support/create_augmentation_issue.html"
    issue_template="support/augmentation_description.html"
    form_class=forms.AugmentationIssueForm

    def issue_subject(self, context):
        return "%s requests augmentation diagnosis for %s"%(
            context.get("submitting_user_name"),
            context.get("dataset")
        )

    def generate_context(self, request, form):
        support = get_user(settings.SUPPORT_USER)
        profile = create_dataset(support, form.cleaned_data.get("profile_json"))
        c = super(AugmentationIssueView, self).generate_context(request, form)
        return dict(c, **{"dataset": profile.get_site_url()})

class DataLoadIssueView(RedmineIssueView):

    def __init__(self, *args, **kwargs):
        super(DataLoadIssueView, self).__init__(*args, **kwargs)
        self.source_type = kwargs.get("source_type", "url")


    def generate_context(self, request, form):
        support = get_user(settings.SUPPORT_USER)
        if self.source_type == "url":
            url = form.cleaned_data.get("url")
        else:
            ds = models.SupportFileDataSource(user = request.user, file=request.FILES['file'])
            ds.save()
            url = get_site_url(ds.file.url)

        c = super(DataLoadIssueView, self).generate_context(request, form)
        return dict(c, **{"url": url})


class DataLoadIgnoredFieldsIssueView(DataLoadIssueView):

    def __init__(self, *args, **kwargs):
        super(DataLoadIgnoredFieldsIssueView, self).__init__(*args, **kwargs)


    create_template="support/ignored_field_issue.html"
    issue_template = "support/ignored_field_description.html"

    def issue_subject(self, context):
        return "%s requests data transformation support"%(context.get("submitting_user_name"),)

url_ignored_fields_issue_view = DataLoadIgnoredFieldsIssueView(source_type="url", form_class=forms.URLDataLoadIgnoredFieldsIssueForm)
file_ignored_fields_issue_view = DataLoadIgnoredFieldsIssueView(source_type="file", form_class=forms.FileDataLoadIgnoredFieldsIssueForm)


class DataLoadUploadIssueView(DataLoadIssueView):

    def __init__(self, *args, **kwargs):
        super(DataLoadUploadIssueView, self).__init__(*args, **kwargs)

    create_template="support/upload_issue.html"
    issue_template="support/upload_description.html"

    def issue_subject(self, context):
        return "%s requests data upload support"%(context.get("submitting_user_name"),)
url_upload_issue_view = DataLoadUploadIssueView(source_type="url", form_class=forms.URLDataLoadUploadIssueForm)
file_upload_issue_view = DataLoadUploadIssueView(source_type="file", form_class=forms.FileDataLoadUploadIssueForm)
