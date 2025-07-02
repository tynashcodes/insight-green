from django import forms
from .models import ESGComplianceReport

from django import forms
from .models import ESGComplianceReport

class ESGComplianceReportForm(forms.ModelForm):
    # Define the choices for the compliance frameworks
    COMPLIANCE_CHOICES = [
        ('GRI', 'GRI'),
        ('TCFD', 'TCFD'),
        ('SASB', 'SASB'),
        ('King IV', 'King IV'),
    ]

    compliance_frameworks = forms.MultipleChoiceField(
        choices=COMPLIANCE_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-control multiselect'}),
        required=True  # You can set this to False if this field is optional
    )

    class Meta:
        model = ESGComplianceReport
        fields = [
            'document_title', 
            'organization_name', 
            'reporting_year', 
            'report_type', 
            'document_version', 
            'report_sector', 
            'compliance_frameworks',  # This is the multiple choice field
            'geographical_region', 
            'report_description', 
            'report_file', 
            'document_status'
        ]

        
        
from .models import TestTable

class TestTableForm(forms.ModelForm):
    class Meta:
        model = TestTable
        fields = ['name', 'description']
