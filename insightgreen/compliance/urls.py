from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
<<<<<<< HEAD
    path('graph/', views.graph, name='graph'),
=======
    path('compliance/report/upload', views.compliance_report_upload, name='compliance_report_upload'),
>>>>>>> 212f352442d019ff513574271baa895a9ed423f0
]