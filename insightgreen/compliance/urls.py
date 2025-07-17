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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)