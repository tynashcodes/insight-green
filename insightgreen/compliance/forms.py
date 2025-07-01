from django import forms
from .models import ESGComplianceReport

class ESGComplianceReportForm(forms.ModelForm):
    class Meta:
        model = ESGComplianceReport
        fields = [
            'document_title', 
            'organization_name', 
            'reporting_year', 
            'report_type', 
            'document_version', 
            'report_sector', 
            'compliance_frameworks', 
            'geographical_region', 
            'report_description', 
            'report_file', 
            'document_status'
        ]
