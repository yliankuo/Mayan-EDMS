from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIDocumentTypeWorkflowListView, APIWorkflowDocumentTypeList,
    APIWorkflowDocumentTypeView, APIWorkflowImageView,
    APIWorkflowInstanceListView, APIWorkflowInstanceLogEntryListView,
    APIWorkflowInstanceView, APIWorkflowListView, APIWorkflowStateListView,
    APIWorkflowStateView, APIWorkflowTransitionListView,
    APIWorkflowTransitionView, APIWorkflowView
)
from .views import (
    DocumentWorkflowInstanceListView, SetupWorkflowCreateView,
    SetupWorkflowDeleteView, SetupWorkflowDocumentTypesView,
    SetupWorkflowEditView, SetupWorkflowListView,
    SetupWorkflowStateActionCreateView, SetupWorkflowStateActionDeleteView,
    SetupWorkflowStateActionEditView, SetupWorkflowStateActionListView,
    SetupWorkflowStateActionSelectionView, SetupWorkflowStateCreateView,
    SetupWorkflowStateDeleteView, SetupWorkflowStateEditView,
    SetupWorkflowStateListView, SetupWorkflowTransitionCreateView,
    SetupWorkflowTransitionDeleteView, SetupWorkflowTransitionEditView,
    SetupWorkflowTransitionListView,
    SetupWorkflowTransitionTriggerEventListView, ToolLaunchAllWorkflows,
    WorkflowDocumentListView, WorkflowInstanceDetailView,
    WorkflowInstanceTransitionView, WorkflowListView, WorkflowPreviewView,
    WorkflowStateDocumentListView, WorkflowStateListView
)

urlpatterns = [
    url(
        regex=r'^workflows/$', name='setup_workflow_list',
        view=SetupWorkflowListView.as_view()
    ),
    url(
        regex=r'^workflows/create/$', name='setup_workflow_create',
        view=SetupWorkflowCreateView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/delete/$',
        name='setup_workflow_delete', view=SetupWorkflowDeleteView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/edit/$',
        name='setup_workflow_edit', view=SetupWorkflowEditView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/preview/$',
        name='workflow_preview', view=WorkflowPreviewView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/document_types/$',
        name='setup_workflow_document_types',
        view=SetupWorkflowDocumentTypesView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/states/$',
        name='setup_workflow_state_list',
        view=SetupWorkflowStateListView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/states/create/$',
        name='setup_workflow_state_create',
        view=SetupWorkflowStateCreateView.as_view()
    ),
    url(
        regex=r'^workflows/states/(?P<workflow_state_id>\d+)/delete/$',
        name='setup_workflow_state_delete',
        view=SetupWorkflowStateDeleteView.as_view()
    ),
    url(
        regex=r'^workflows/states/(?P<workflow_state_id>\d+)/edit/$',
        name='setup_workflow_state_edit',
        view=SetupWorkflowStateEditView.as_view()
    ),

    url(
        regex=r'^workflows/states/(?P<workflow_state_id>\d+)/actions/$',
        name='setup_workflow_state_action_list',
        view=SetupWorkflowStateActionListView.as_view()
    ),
    url(
        regex=r'^workflows/states/(?P<workflow_state_id>\d+)/actions/selection/$',
        name='setup_workflow_state_action_selection',
        view=SetupWorkflowStateActionSelectionView.as_view(),
    ),
    url(
        regex=r'^workflows/states/(?P<workflow_state_id>\d+)/actions/(?P<class_path>[a-zA-Z0-9_.]+)/create/$',
        name='setup_workflow_state_action_create',
        view=SetupWorkflowStateActionCreateView.as_view()
    ),
    url(
        regex=r'^workflows/states/actions/(?P<workflow_state_action_id>\d+)/delete/$',
        view=SetupWorkflowStateActionDeleteView.as_view(),
        name='setup_workflow_state_action_delete'
    ),
    url(
        regex=r'^workflows/states/actions/(?P<workflow_state_action_id>\d+)/edit/$',
        name='setup_workflow_state_action_edit',
        view=SetupWorkflowStateActionEditView.as_view()
    ),

    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/transitions/$',
        name='setup_workflow_transition_list',
        view=SetupWorkflowTransitionListView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/transitions/create/$',
        name='setup_workflow_transition_create',
        view=SetupWorkflowTransitionCreateView.as_view()
    ),
    url(
        regex=r'^workflows/transitions/(?P<workflow_transitions_id>\d+)/delete/$',
        name='setup_workflow_transition_delete',
        view=SetupWorkflowTransitionDeleteView.as_view()
    ),
    url(
        regex=r'^workflows/transitions/(?P<workflow_transitions_id>\d+)/edit/$',
        name='setup_workflow_transition_edit',
        view=SetupWorkflowTransitionEditView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/transitions/events/$',
        name='setup_workflow_transition_events',
        view=SetupWorkflowTransitionTriggerEventListView.as_view()
    ),

    url(
        regex=r'^workflow_instances/$', name='workflow_list',
        view=WorkflowListView.as_view()
    ),
    url(
        regex=r'^workflow_instances/(?P<workflow_id>\d+)/documents/$',
        name='setup_workflow_document_list',
        view=WorkflowDocumentListView.as_view()
    ),
    url(
        regex=r'^workflow_instances/(?P<workflow_id>\d+)/documents/$',
        name='workflow_document_list',
        view=WorkflowDocumentListView.as_view()
    ),
    url(
        regex=r'^workflow_instances/(?P<workflow_id>\d+)/states/$',
        name='workflow_state_list', view=WorkflowStateListView.as_view()
    ),
    url(
        regex=r'^workflow_instances/states/(?P<workflow_state_id>\d+)/documents/$',
        name='workflow_state_document_list',
        view=WorkflowStateDocumentListView.as_view()
    ),

    url(
        regex=r'^documents/(?P<document_id>\d+)/workflows/$',
        name='document_workflow_instance_list',
        view=DocumentWorkflowInstanceListView.as_view()
    ),
    url(
        regex=r'^documents/workflows/(?P<workflow_instance_id>\d+)/$',
        name='workflow_instance_detail',
        view=WorkflowInstanceDetailView.as_view()
    ),
    url(
        regex=r'^documents/workflows/(?P<workflow_instance_id>\d+)/transition/$',
        name='workflow_instance_transition',
        view=WorkflowInstanceTransitionView.as_view()
    ),
    url(
        regex=r'^tools/workflows/all/launch/$',
        name='tool_launch_all_workflows',
        view=ToolLaunchAllWorkflows.as_view()
    )
]

api_urls = [
    url(
        regex=r'^workflows/$', name='workflow-list',
        view=APIWorkflowListView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/$',
        name='workflow-detail', view=APIWorkflowView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/image/$',
        name='workflow-image', view=APIWorkflowImageView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/document_types/$',
        name='workflow-document-type-list',
        view=APIWorkflowDocumentTypeList.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/document_types/(?P<document_type_id>\d+)/$',
        name='workflow-document-type-detail',
        view=APIWorkflowDocumentTypeView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/states/$',
        name='workflowstate-list',
        view=APIWorkflowStateListView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/states/(?P<state_id>\d+)/$',
        name='workflowstate-detail', view=APIWorkflowStateView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/transitions/$',
        name='workflowtransition-list',
        view=APIWorkflowTransitionListView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/transitions/(?P<transition_id>\d+)/$',
        name='workflowtransition-detail',
        view=APIWorkflowTransitionView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/workflows/$',
        name='workflowinstance-list',
        view=APIWorkflowInstanceListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/workflows/(?P<workflow_id>\d+)/$',
        name='workflowinstance-detail',
        view=APIWorkflowInstanceView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/workflows/(?P<workflow_id>\d+)/log_entries/$',
        name='workflowinstancelogentry-list',
        view=APIWorkflowInstanceLogEntryListView.as_view()
    ),
    url(
        regex=r'^document_types/(?P<document_type_id>\d+)/workflows/$',
        name='documenttype-workflow-list',
        view=APIDocumentTypeWorkflowListView.as_view()
    )
]
