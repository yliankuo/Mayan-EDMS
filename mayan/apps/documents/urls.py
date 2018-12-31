from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIDeletedDocumentListView, APIDeletedDocumentRestoreView,
    APIDeletedDocumentView, APIDocumentDownloadView, APIDocumentListView,
    APIDocumentPageImageView, APIDocumentPageView,
    APIDocumentTypeDocumentListView, APIDocumentTypeListView,
    APIDocumentTypeView, APIDocumentVersionDownloadView,
    APIDocumentVersionPageListView, APIDocumentVersionsListView,
    APIDocumentVersionView, APIDocumentView, APIRecentDocumentListView
)
from .views import (
    ClearImageCacheView, DeletedDocumentDeleteManyView,
    DeletedDocumentDeleteView, DeletedDocumentListView,
    DocumentDocumentTypeEditView, DocumentDownloadFormView,
    DocumentDownloadView, DocumentDuplicatesListView, DocumentEditView,
    DocumentListView, DocumentPageListView, DocumentPageNavigationFirst,
    DocumentPageNavigationLast, DocumentPageNavigationNext,
    DocumentPageNavigationPrevious, DocumentPageRotateLeftView,
    DocumentPageRotateRightView, DocumentPageView, DocumentPageViewResetView,
    DocumentPageZoomInView, DocumentPageZoomOutView, DocumentPreviewView,
    DocumentPrint, DocumentRestoreManyView, DocumentRestoreView,
    DocumentTransformationsClearView, DocumentTransformationsCloneView,
    DocumentTrashManyView, DocumentTrashView, DocumentTypeCreateView,
    DocumentTypeDeleteView, DocumentTypeDocumentListView, DocumentTypeEditView,
    DocumentTypeFilenameCreateView, DocumentTypeFilenameDeleteView,
    DocumentTypeFilenameEditView, DocumentTypeFilenameListView,
    DocumentTypeListView, DocumentUpdatePageCountView,
    DocumentVersionDownloadFormView, DocumentVersionDownloadView,
    DocumentVersionListView, DocumentVersionRevertView, DocumentVersionView,
    DocumentView, DuplicatedDocumentListView, EmptyTrashCanView,
    FavoriteAddView, FavoriteDocumentListView, FavoriteRemoveView,
    RecentAccessDocumentListView, RecentAddedDocumentListView,
    ScanDuplicatedDocuments
)

urlpatterns = [
    url(
        regex=r'^documents/all/$', name='document_list',
        view=DocumentListView.as_view()
    ),
    url(
        regex=r'^documents/recent_access/$',
        name='document_list_recent_access',
        view=RecentAccessDocumentListView.as_view()
    ),
    url(
        regex=r'^documents/recent_added/$', name='document_list_recent_added',
        view=RecentAddedDocumentListView.as_view()
    ),
    url(
        regex=r'^documents/deleted/$', name='document_list_deleted',
        view=DeletedDocumentListView.as_view()
    ),
    url(
        regex=r'^documents/duplicated/$', name='duplicated_document_list',
        view=DuplicatedDocumentListView.as_view()
    ),
    url(
        regex=r'^documents/favorites/$', name='document_list_favorites',
        view=FavoriteDocumentListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/preview/$',
        name='document_preview', view=DocumentPreviewView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/properties/$',
        name='document_properties', view=DocumentView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/duplicates/$',
        name='document_duplicates_list',
        view=DocumentDuplicatesListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/add_to_favorites/$',
        name='document_add_to_favorites', view=FavoriteAddView.as_view()
    ),
    url(
        regex=r'^documents/multiple/add_to_favorites/$',
        name='document_multiple_add_to_favorites',
        view=FavoriteAddView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/remove_from_favorites/$',
        name='document_remove_from_favorites',
        view=FavoriteRemoveView.as_view()
    ),
    url(
        regex=r'^documents/multiple/remove_from_favorites/$',
        name='document_multiple_remove_from_favorites',
        view=FavoriteRemoveView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/restore/$',
        name='document_restore', view=DocumentRestoreView.as_view()
    ),
    url(
        regex=r'^documents/multiple/restore/$',
        name='document_multiple_restore',
        view=DocumentRestoreManyView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/delete/$',
        name='document_delete', view=DeletedDocumentDeleteView.as_view()
    ),
    url(
        regex=r'^documents/multiple/delete/$', name='document_multiple_delete',
        view=DeletedDocumentDeleteManyView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/type/$',
        name='document_document_type_edit',
        view=DocumentDocumentTypeEditView.as_view()
    ),
    url(
        regex=r'^documents/multiple/type/$',
        name='document_multiple_document_type_edit',
        view=DocumentDocumentTypeEditView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/trash/$',
        name='document_trash', view=DocumentTrashView.as_view()
    ),
    url(
        regex=r'^documents/multiple/trash/$', name='document_multiple_trash',
        view=DocumentTrashManyView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/edit/$', name='document_edit',
        view=DocumentEditView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/print/$',
        name='document_print', view=DocumentPrint.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/reset_page_count/$',
        name='document_update_page_count',
        view=DocumentUpdatePageCountView.as_view()
    ),
    url(
        regex=r'^documents/multiple/reset_page_count/$',
        name='document_multiple_update_page_count',
        view=DocumentUpdatePageCountView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/download/form/$',
        name='document_download_form', view=DocumentDownloadFormView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/download/$',
        name='document_download', view=DocumentDownloadView.as_view()
    ),
    url(
        regex=r'^documents/multiple/download/form/$',
        name='document_multiple_download_form',
        view=DocumentDownloadFormView.as_view()
    ),
    url(
        regex=r'^documents/multiple/download/$',
        name='document_multiple_download', view=DocumentDownloadView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/clear_transformations/$',
        name='document_clear_transformations',
        view=DocumentTransformationsClearView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/clone_transformations/$',
        name='document_clone_transformations',
        view=DocumentTransformationsCloneView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/version/all/$',
        name='document_version_list',
        view=DocumentVersionListView.as_view()
    ),
    url(
        regex=r'^documents/versions/(?P<document_version_pk>\d+)/download/form/$',
        name='document_version_download_form',
        view=DocumentVersionDownloadFormView.as_view()
    ),
    url(
        regex=r'^documents/versions/(?P<document_version_pk>\d+)/$',
        name='document_version_view', view=DocumentVersionView.as_view()
    ),
    url(
        regex=r'^documents/versions/(?P<document_version_pk>\d+)/download/$',
        name='document_version_download',
        view=DocumentVersionDownloadView.as_view()
    ),
    url(
        regex=r'^documents/versions/(?P<document_version_pk>\d+)/revert/$',
        name='document_version_revert',
        view=DocumentVersionRevertView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/pages/$',
        name='document_pages',
        view=DocumentPageListView.as_view()
    ),
    url(
        regex=r'^documents/multiple/clear_transformations/$',
        name='document_multiple_clear_transformations',
        view=DocumentTransformationsClearView.as_view()
    ),
    url(
        regex=r'^documents/cache/clear/$', name='document_clear_image_cache',
        view=ClearImageCacheView.as_view()
    ),
    url(
        regex=r'^trash_can/empty/$', name='trash_can_empty',
        view=EmptyTrashCanView.as_view()
    ),
    url(
        regex=r'^pages/(?P<document_page_pk>\d+)/$',
        name='document_page_view', view=DocumentPageView.as_view()
    ),
    url(
        regex=r'^pages/(?P<document_page_pk>\d+)/navigation/next/$',
        name='document_page_navigation_next',
        view=DocumentPageNavigationNext.as_view()
    ),
    url(
        regex=r'^pages/(?P<document_page_pk>\d+)/navigation/previous/$',
        name='document_page_navigation_previous',
        view=DocumentPageNavigationPrevious.as_view()
    ),
    url(
        regex=r'^pages/(?P<document_page_pk>\d+)/navigation/first/$',
        name='document_page_navigation_first',
        view=DocumentPageNavigationFirst.as_view()
    ),
    url(
        regex=r'^pages/(?P<document_page_pk>\d+)/navigation/last/$',
        name='document_page_navigation_last',
        view=DocumentPageNavigationLast.as_view()
    ),
    url(
        regex=r'^pages/(?P<document_page_pk>\d+)/zoom/in/$',
        name='document_page_zoom_in', view=DocumentPageZoomInView.as_view()
    ),
    url(
        regex=r'^pages/(?P<document_page_pk>\d+)/zoom/out/$',
        name='document_page_zoom_out', view=DocumentPageZoomOutView.as_view()
    ),
    url(
        regex=r'^pages/(?P<document_page_pk>\d+)/rotate/left/$',
        name='document_page_rotate_left',
        view=DocumentPageRotateLeftView.as_view()
    ),
    url(
        regex=r'^pages/(?P<document_page_pk>\d+)/rotate/right/$',
        name='document_page_rotate_right',
        view=DocumentPageRotateRightView.as_view()
    ),
    url(
        regex=r'^pages/(?P<document_page_pk>\d+)/reset/$',
        name='document_page_view_reset',
        view=DocumentPageViewResetView.as_view()
    ),

    # Admin views
    url(
        regex=r'^types/$', name='document_type_list',
        view=DocumentTypeListView.as_view()
    ),
    url(
        regex=r'^types/create/$', name='document_type_create',
        view=DocumentTypeCreateView.as_view()
    ),
    url(
        regex=r'^types/(?P<document_type_pk>\d+)/edit/$', name='document_type_edit',
        view=DocumentTypeEditView.as_view()
    ),
    url(
        regex=r'^types/(?P<document_type_pk>\d+)/delete/$', name='document_type_delete',
        view=DocumentTypeDeleteView.as_view()
    ),
    url(
        regex=r'^types/(?P<document_type_pk>\d+)/documents/$',
        name='document_type_document_list',
        view=DocumentTypeDocumentListView.as_view()
    ),
    url(
        regex=r'^types/(?P<document_type_pk>\d+)/filenames/create/$',
        name='document_type_filename_create',
        view=DocumentTypeFilenameCreateView.as_view()
    ),
    url(
        regex=r'^types/(?P<document_type_pk>\d+)/filenames/$',
        name='document_type_filename_list',
        view=DocumentTypeFilenameListView.as_view()
    ),
    url(
        regex=r'^types/filenames/(?P<filename_pk>\d+)/edit/$',
        name='document_type_filename_edit',
        view=DocumentTypeFilenameEditView.as_view()
    ),
    url(
        regex=r'^types/filenames/(?P<filename_pk>\d+)/delete/$',
        name='document_type_filename_delete',
        view=DocumentTypeFilenameDeleteView.as_view()
    ),

    # Tools

    url(
        regex=r'^tools/documents/duplicated/scan/$',
        name='duplicated_document_scan',
        view=ScanDuplicatedDocuments.as_view()
    ),
]

api_urls = [
    url(
        regex=r'^document_types/$', name='documenttype-list',
        view=APIDocumentTypeListView.as_view()
    ),
    url(
        regex=r'^document_types/(?P<document_type_pk>\d+)/$',
        name='documenttype-detail', view=APIDocumentTypeView.as_view()
    ),
    url(
        regex=r'^document_types/(?P<document_type_pk>\d+)/documents/$',
        name='documenttype-document-list',
        view=APIDocumentTypeDocumentListView.as_view()
    ),
    url(
        regex=r'^documents/$', name='document-list',
        view=APIDocumentListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/$', name='document-detail',
        view=APIDocumentView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/download/$',
        name='document-download', view=APIDocumentDownloadView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/versions/$',
        name='document-version-list',
        view=APIDocumentVersionsListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/versions/(?P<document_version_pk>\d+)/$',
        name='documentversion-detail',
        view=APIDocumentVersionView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/versions/(?P<document_version_pk>\d+)/pages/$',
        name='documentversion-page-list',
        view=APIDocumentVersionPageListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/versions/(?P<document_version_pk>\d+)/download/$',
        name='documentversion-download',
        view=APIDocumentVersionDownloadView.as_view()
    ),
    url(
        regex=r'^documents/recent/$', name='document-recent-list',
        view=APIRecentDocumentListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/versions/(?P<document_version_pk>\d+)/pages/(?P<document_page_pk>\d+)$',
        name='documentpage-detail', view=APIDocumentPageView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/versions/(?P<document_version_pk>\d+)/pages/(?P<document_page_pk>\d+)/image/$',
        name='documentpage-image', view=APIDocumentPageImageView.as_view()
    ),
    url(
        regex=r'^trashed_documents/$', name='trasheddocument-list',
        view=APIDeletedDocumentListView.as_view()
    ),
    url(
        regex=r'^trashed_documents/(?P<document_pk>\d+)/$',
        name='trasheddocument-detail', view=APIDeletedDocumentView.as_view()
    ),
    url(
        regex=r'^trashed_documents/(?P<document_pk>\d+)/restore/$',
        name='trasheddocument-restore',
        view=APIDeletedDocumentRestoreView.as_view()
    ),
]
