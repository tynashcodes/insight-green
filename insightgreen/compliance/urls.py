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
]