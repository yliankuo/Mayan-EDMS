from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from acls.models import AccessEntry
from common import menu_facet
from common.models import SharedUploadedFile
from common.utils import encapsulate
from common.views import MultiFormView, ParentChildListView
from documents.models import DocumentType, Document
from documents.permissions import (
    permission_document_create, permission_document_new_version
)
from documents.tasks import task_upload_new_version
from metadata.api import decode_metadata_from_url
from navigation import Link
from permissions import Permission

from .forms import (
    NewDocumentForm, NewVersionForm
)
from .literals import (
    SOURCE_CHOICE_STAGING, SOURCE_CHOICE_WEB_FORM, SOURCE_UNCOMPRESS_CHOICE_ASK,
    SOURCE_UNCOMPRESS_CHOICE_Y
)
from .models import (
    InteractiveSource, Source, StagingFolderSource, WebFormSource
)
from .permissions import (
    permission_sources_setup_create, permission_sources_setup_delete,
    permission_sources_setup_edit, permission_sources_setup_view
)
from .tasks import task_source_upload_document
from .utils import get_class, get_form_class, get_upload_form_class


class SourceLogListView(ParentChildListView):
    object_permission = permission_sources_setup_view
    parent_queryset = Source.objects.select_subclasses()

    def get_queryset(self):
        return self.get_object().logs.all()

    def get_context_data(self, **kwargs):
        context = super(SourceLogListView, self).get_context_data(**kwargs)

        context.update(
            {
                'title': _('Log entries for source: %s') % self.get_object(),
                'hide_object': True,
                'extra_columns': [
                    {
                        'name': _('Date time'),
                        'attribute': encapsulate(lambda entry: entry.datetime)
                    },
                    {
                        'name': _('Message'),
                        'attribute': encapsulate(lambda entry: entry.message)
                    },
                ]
            }
        )

        return context


def document_create_siblings(request, document_id):
    Permission.check_permissions(request.user, [permission_document_create])

    document = get_object_or_404(Document, pk=document_id)
    query_dict = {}
    for pk, metadata in enumerate(document.metadata.all()):
        query_dict['metadata%s_id' % pk] = metadata.metadata_type_id
        query_dict['metadata%s_value' % pk] = metadata.value

    query_dict['document_type_id'] = document.document_type_id

    url = reverse('sources:upload_interactive')
    return HttpResponseRedirect('%s?%s' % (url, urlencode(query_dict)))


def get_tab_link_for_source(source, document=None):
    if document:
        view = 'sources:upload_version'
        args = ['"{}"'.format(document.pk), '"{}"'.format(source.pk)]
    else:
        view = 'sources:upload_interactive'
        args = ['"{}"'.format(source.pk)]

    return Link(
        text=source.title,
        view=view,
        args=args,
        keep_query=True,
        remove_from_query=['page'],
        icon='fa fa-upload',
    )


def get_active_tab_links(document=None):
    tab_links = []

    web_forms = WebFormSource.objects.filter(enabled=True)
    for web_form in web_forms:
        tab_links.append(get_tab_link_for_source(web_form, document))

    staging_folders = StagingFolderSource.objects.filter(enabled=True)
    for staging_folder in staging_folders:
        tab_links.append(get_tab_link_for_source(staging_folder, document))

    return {
        'tab_links': tab_links,
        SOURCE_CHOICE_WEB_FORM: web_forms,
        SOURCE_CHOICE_STAGING: staging_folders,
    }


class UploadBaseView(MultiFormView):
    template_name = 'appearance/generic_form.html'
    prefixes = {'source_form': 'source', 'document_form': 'document'}

    def dispatch(self, request, *args, **kwargs):
        if 'source_id' in kwargs:
            self.source = get_object_or_404(Source.objects.filter(enabled=True).select_subclasses(), pk=kwargs['source_id'])
        else:
            self.source = InteractiveSource.objects.filter(enabled=True).select_subclasses().first()

        if InteractiveSource.objects.filter(enabled=True).count() == 0:
            messages.error(request, _('No interactive document sources have been defined or none have been enabled, create one before proceeding.'))
            return HttpResponseRedirect(reverse('sources:setup_source_list'))

        return super(UploadBaseView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UploadBaseView, self).get_context_data(**kwargs)
        subtemplates_list = []

        context['source'] = self.source

        if isinstance(self.source, StagingFolderSource):
            try:
                staging_filelist = list(self.source.get_files())
            except Exception as exception:
                messages.error(self.request, exception)
                staging_filelist = []
            finally:
                subtemplates_list = [
                    {
                        'name': 'appearance/generic_multiform_subtemplate.html',
                        'context': {
                            'forms': context['forms'],
                            'title': _('Document properties'),
                        }
                    },
                    {
                        'name': 'appearance/generic_list_subtemplate.html',
                        'context': {
                            'hide_link': True,
                            'object_list': staging_filelist,
                            'title': _('Files in staging path'),
                        }
                    },
                ]
        else:
            subtemplates_list.append({
                'name': 'appearance/generic_multiform_subtemplate.html',
                'context': {
                    'forms': context['forms'],
                    'is_multipart': True,
                    'title': _('Document properties'),
                },
            })

        menu_facet.bound_links['sources:upload_interactive'] = self.tab_links['tab_links']
        menu_facet.bound_links['sources:upload_version'] = self.tab_links['tab_links']

        context.update({
            'subtemplates_list': subtemplates_list,
        })

        return context


class UploadInteractiveView(UploadBaseView):

    def dispatch(self, request, *args, **kwargs):
        self.subtemplates_list = []

        Permission.check_permissions(request.user, [permission_document_create])

        self.document_type = get_object_or_404(DocumentType, pk=self.request.GET.get('document_type_id', self.request.POST.get('document_type_id')))

        self.tab_links = get_active_tab_links()

        return super(UploadInteractiveView, self).dispatch(request, *args, **kwargs)

    def forms_valid(self, forms):
        if self.source.uncompress == SOURCE_UNCOMPRESS_CHOICE_ASK:
            expand = forms['source_form'].cleaned_data.get('expand')
        else:
            if self.source.uncompress == SOURCE_UNCOMPRESS_CHOICE_Y:
                expand = True
            else:
                expand = False

        uploaded_file = self.source.get_upload_file_object(forms['source_form'].cleaned_data)

        shared_uploaded_file = SharedUploadedFile.objects.create(file=uploaded_file.file)

        label = shared_uploaded_file.filename
        if 'document_type_available_filenames' in forms['document_form'].cleaned_data:
            if forms['document_form'].cleaned_data['document_type_available_filenames']:
                label = forms['document_form'].cleaned_data['document_type_available_filenames'].filename

        if not self.request.user.is_anonymous():
            user_id = self.request.user.pk
        else:
            user_id = None

        try:
            self.source.clean_up_upload_file(uploaded_file)
        except Exception as exception:
            messages.error(self.request, exception)

        task_source_upload_document.apply_async(kwargs=dict(
            description=forms['document_form'].cleaned_data.get('description'),
            document_type_id=self.document_type.pk,
            expand=expand,
            label=label,
            language=forms['document_form'].cleaned_data.get('language'),
            metadata_dict_list=decode_metadata_from_url(self.request.GET),
            shared_uploaded_file_id=shared_uploaded_file.pk,
            source_id=self.source.pk,
            user_id=user_id,
        ), queue='uploads')
        messages.success(self.request, _('New document queued for uploaded and will be available shortly.'))
        return HttpResponseRedirect(self.request.get_full_path())

    def create_source_form_form(self, **kwargs):
        return self.get_form_classes()['source_form'](
            prefix=kwargs['prefix'],
            source=self.source,
            show_expand=(self.source.uncompress == SOURCE_UNCOMPRESS_CHOICE_ASK),
            data=kwargs.get('data', None),
            files=kwargs.get('files', None),
        )

    def create_document_form_form(self, **kwargs):
        return self.get_form_classes()['document_form'](
            prefix=kwargs['prefix'],
            document_type=self.document_type,
            data=kwargs.get('data', None),
            files=kwargs.get('files', None),
        )

    def get_form_classes(self):
        return {'document_form': NewDocumentForm, 'source_form': get_upload_form_class(self.source.source_type)}

    def get_context_data(self, **kwargs):
        context = super(UploadInteractiveView, self).get_context_data(**kwargs)
        context['title'] = _('Upload a local document from source: %s') % self.source.title
        return context


class UploadInteractiveVersionView(UploadBaseView):
    def dispatch(self, request, *args, **kwargs):

        self.subtemplates_list = []

        self.document = get_object_or_404(Document, pk=kwargs['document_pk'])
        try:
            Permission.check_permissions(self.request.user, [permission_document_new_version])
        except PermissionDenied:
            AccessEntry.objects.check_access(permission_document_new_version, self.request.user, self.document)

        self.tab_links = get_active_tab_links(self.document)

        return super(UploadInteractiveVersionView, self).dispatch(request, *args, **kwargs)

    def forms_valid(self, forms):
        uploaded_file = self.source.get_upload_file_object(forms['source_form'].cleaned_data)

        shared_uploaded_file = SharedUploadedFile.objects.create(file=uploaded_file.file)

        try:
            self.source.clean_up_upload_file(uploaded_file)
        except Exception as exception:
            messages.error(self.request, exception)

        if not self.request.user.is_anonymous():
            user_id = self.request.user.pk
        else:
            user_id = None

        task_upload_new_version.apply_async(kwargs=dict(
            shared_uploaded_file_id=shared_uploaded_file.pk,
            document_id=self.document.pk,
            user_id=user_id,
            comment=forms['document_form'].cleaned_data.get('comment')
        ), queue='uploads')

        messages.success(self.request, _('New document version queued for uploaded and will be available shortly.'))
        return HttpResponseRedirect(reverse('documents:document_version_list', args=[self.document.pk]))

    def create_source_form_form(self, **kwargs):
        return self.get_form_classes()['source_form'](
            prefix=kwargs['prefix'],
            source=self.source,
            show_expand=False,
            data=kwargs.get('data', None),
            files=kwargs.get('files', None),
        )

    def create_document_form_form(self, **kwargs):
        return self.get_form_classes()['document_form'](
            prefix=kwargs['prefix'],
            data=kwargs.get('data', None),
            files=kwargs.get('files', None),
        )

    def get_form_classes(self):
        return {'document_form': NewVersionForm, 'source_form': get_upload_form_class(self.source.source_type)}

    def get_context_data(self, **kwargs):
        context = super(UploadInteractiveVersionView, self).get_context_data(**kwargs)
        context['object'] = self.document
        context['title'] = _('Upload a new version from source: %s') % self.source.title

        return context


def staging_file_delete(request, staging_folder_pk, encoded_filename):
    Permission.check_permissions(request.user, [permission_document_create, permission_document_new_version])
    staging_folder = get_object_or_404(StagingFolderSource, pk=staging_folder_pk)

    staging_file = staging_folder.get_file(encoded_filename=encoded_filename)
    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', reverse(settings.LOGIN_REDIRECT_URL))))
    previous = request.POST.get('previous', request.GET.get('previous', request.META.get('HTTP_REFERER', reverse(settings.LOGIN_REDIRECT_URL))))

    if request.method == 'POST':
        try:
            staging_file.delete()
            messages.success(request, _('Staging file delete successfully.'))
        except Exception as exception:
            messages.error(request, _('Staging file delete error; %s.') % exception)
        return HttpResponseRedirect(next)

    results = get_active_tab_links()

    return render_to_response('appearance/generic_confirm.html', {
        'source': staging_folder,
        'delete_view': True,
        'object': staging_file,
        'next': next,
        'previous': previous,
        'extra_navigation_links': {'form_header': {'staging_file_delete': {'links': results['tab_links']}}},
    }, context_instance=RequestContext(request))


# Setup views
def setup_source_list(request):
    Permission.check_permissions(request.user, [permission_sources_setup_view])

    context = {
        'object_list': Source.objects.select_subclasses(),
        'title': _('Sources'),
        'hide_link': True,
        'extra_columns': [
            {
                'name': _('Type'),
                'attribute': encapsulate(lambda x: x.class_fullname())
            },
            {
                'name': _('Enabled'),
                'attribute': encapsulate(lambda x: _('Yes') if x.enabled else _('No'))
            },
        ]
    }

    return render_to_response('appearance/generic_list.html', context,
                              context_instance=RequestContext(request))


def setup_source_edit(request, source_id):
    Permission.check_permissions(request.user, [permission_sources_setup_edit])

    source = get_object_or_404(Source.objects.select_subclasses(), pk=source_id)
    form_class = get_form_class(source.source_type)

    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', reverse(settings.LOGIN_REDIRECT_URL))))

    if request.method == 'POST':
        form = form_class(instance=source, data=request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, _('Source edited successfully'))
                return HttpResponseRedirect(next)
            except Exception as exception:
                messages.error(request, _('Error editing source; %s') % exception)
    else:
        form = form_class(instance=source)

    return render_to_response('appearance/generic_form.html', {
        'form': form,
        'navigation_object_list': ['source'],
        'next': next,
        'source': source,
        'source_type': source.source_type,
        'title': _('Edit source: %s') % source,
    }, context_instance=RequestContext(request))


def setup_source_delete(request, source_id):
    Permission.check_permissions(request.user, [permission_sources_setup_delete])
    source = get_object_or_404(Source.objects.select_subclasses(), pk=source_id)
    redirect_view = reverse('sources:setup_source_list')

    previous = request.POST.get('previous', request.GET.get('previous', request.META.get('HTTP_REFERER', redirect_view)))

    if request.method == 'POST':
        try:
            source.delete()
            messages.success(request, _('Source "%s" deleted successfully.') % source)
        except Exception as exception:
            messages.error(request, _('Error deleting source "%(source)s": %(error)s') % {
                'source': source, 'error': exception
            })
        return HttpResponseRedirect(redirect_view)

    context = {
        'delete_view': True,
        'navigation_object_list': ['source'],
        'previous': previous,
        'source': source,
        'source_type': source.source_type,
        'title': _('Are you sure you wish to delete the source: %s?') % source,
    }

    return render_to_response('appearance/generic_confirm.html', context,
                              context_instance=RequestContext(request))


def setup_source_create(request, source_type):
    Permission.check_permissions(request.user, [permission_sources_setup_create])

    cls = get_class(source_type)
    form_class = get_form_class(source_type)

    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, _('Source created successfully'))
                return HttpResponseRedirect(reverse('sources:setup_source_list'))
            except Exception as exception:
                messages.error(request, _('Error creating source; %s') % exception)
    else:
        form = form_class()

    return render_to_response('appearance/generic_form.html', {
        'form': form,
        'navigation_object_list': ['source'],
        'source_type': source_type,
        'title': _('Create new source of type: %s') % cls.class_fullname(),
    }, context_instance=RequestContext(request))
