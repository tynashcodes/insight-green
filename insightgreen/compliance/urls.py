from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('graph/', views.graph, name='graph'),
    path('compliance/report/upload', views.compliance_report_upload, name='compliance_report_upload'),
    path('new/', views.testtable_create, name='testtable_create'),
    path('compliance/documents/list', views.compliance_document_list, name='compliance_document_list'),
    path('compliance/documents/extract/<int:id>/', views.extract_text_from_pdf, name='extract_text'),
    path('corporate/upload', views.upload_companies, name='upload_companies'),
    path('corporate/report/upload', views.upload_corporate_report, name='upload_corporate_report'),
    path('corporate/report/list', views.corporate_report_list, name='corporate_report_list'),
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
]