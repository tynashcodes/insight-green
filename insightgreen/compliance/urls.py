from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('graph/', views.graph, name='graph'),
    path('compliance/report/upload', views.compliance_report_upload, name='compliance_report_upload'),
    path('new/', views.testtable_create, name='testtable_create'),
    path('compliance/documents/list', views.compliance_document_list, name='compliance_document_list'),
    path('compliance/documents/extract/<int:id>/', views.extract_text_from_pdf, name='extract_text'),
    path('corporate/upload', views.upload_companies, name='upload_companies'),
    path('create-esg-report-batch/', views.create_esg_report_batch, name='create_esg_report_batch'),
    path('list-esg-report-batch/', views.list_esg_report_batch, name='list_esg_report_batch'),
    path('upload-bulk-reports/<int:batch_id>/', views.upload_bulk_reports, name='upload_bulk_reports'),
    path('list-corporate-report-batch/', views.list_corporate_report_batch, name='list_corporate_report_batch'),
    path('report-batch-list/', views.report_batch_list, name='report_batch_list'),
    # Peer Benchmarking
    path('peer-benchmarking-overview/', views.peer_benchmarking_overview, name='peer_benchmarking_overview'),
    path('reports/<int:report_id>/extract-pages/', views.extract_full_text_using_gemini_flash, name='extract_report_by_pages'),
    path('compliance/', views.compliance_analysis_view, name='compliance_analysis'),
    path('compliance/ajax/run/<int:evaluation_id>/', views.ajax_run_compliance, name='ajax_run_compliance'),
    path('evaluation/list/', views.evaluation_list, name='evaluation_list'),
    path('loading/', views.loading, name='loading'),
    path('compliance/summary/<int:summary_id>/', views.compliance_summary_detail, name='compliance_summary_detail'),
    path('evaluation/scoring/findings/<int:evaluation_id>/', views.evaluation_scoring_findings, name='evaluation_scoring_findings'),
    path('scoring/history/', views.scoring_history, name='scoring_history'),
    # Extracted report pages overview
    path('framework/extracted/', views.extracted_framework_list, name='extracted_framework_list'),
    path('compliance/standards/', views.compliance_standards, name='compliance_standards'),
    

    path('compliance/standards/findings/', views.compliance_standards_findings, name='compliance_standards_findings'),
    path('compliance/standards/findings/overview/', views.compliance_standards_findings_overview, name='compliance_standards_findings_overview'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)