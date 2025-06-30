from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('compliance/report/upload', views.compliance_report_upload, name='compliance_report_upload'),
]