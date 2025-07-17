from django import forms
from .models import ESGComplianceReport, Evaluation, ESGCompany, ESGComplianceStandard

class ESGComplianceReportForm(forms.ModelForm):
    # Compliance Framework Choices
    COMPLIANCE_CHOICES = [
        ('GRI', 'GRI (Global Reporting Initiative)'),
        ('TCFD', 'TCFD (Task Force on Climate-related Financial Disclosures)'),
        ('SASB', 'SASB (Sustainability Accounting Standards Board)'),
        ('King IV', 'King IV (South Africa)'),
        ('ISO 26000', 'ISO 26000 (Social Responsibility)'),
        ('ISO 14001', 'ISO 14001 (Environmental Management Systems)'),
        ('ISO 37001', 'ISO 37001 (Anti-bribery Management Systems)'),
        ('PRI', 'PRI (Principles for Responsible Investment)'),
        ('OECD Guidelines', 'OECD Guidelines for Multinational Enterprises'),
        ('NFRD', 'NFRD (Non-Financial Reporting Directive)'),
        ('CDP', 'CDP (Carbon Disclosure Project)'),
        ('SFDR', 'SFDR (Sustainable Finance Disclosure Regulation)'),
        ('EU Taxonomy', 'EU Taxonomy Regulation'),
        ('UN SDGs', 'UN Sustainable Development Goals (SDGs)'),
    ]

    # Sector Choices
    SECTOR_CHOICES = [
        ('Energy', 'Energy'),
        ('Healthcare', 'Healthcare'),
        ('Consumer Goods', 'Consumer Goods'),
        ('Technology', 'Technology'),
        ('Materials', 'Materials'),
        ('Industrials', 'Industrials'),
        ('Utilities', 'Utilities'),
        ('Consumer Services', 'Consumer Services'),
        ('Real Estate', 'Real Estate'),
        ('Telecommunication Services', 'Telecommunications'),
        ('Consumer Discretionary', 'Consumer Discretionary'),
        ('Consumer Staples', 'Consumer Staples'),
        ('Basic Materials', 'Basic Materials'),
        ('Transportation', 'Transportation'),
        ('Financial Services', 'Financial Services'),
        ('Healthcare Services', 'Healthcare Services'),
        ('Leisure & Luxury Goods', 'Leisure & Luxury Goods'),
        ('Pharmaceuticals', 'Pharmaceuticals'),
        ('Renewables', 'Renewables'),
        ('Chemicals', 'Chemicals'),
        ('Mining', 'Mining'),
        ('Forestry & Paper', 'Forestry & Paper'),
        ('Agriculture', 'Agriculture'),
        ('Construction & Engineering', 'Construction & Engineering'),
    ]

    # Organization Choices
    ORGANIZATION_CHOICES = [
        ('GRI', 'Global Reporting Initiative (GRI)'),
        ('SASB', 'Sustainability Accounting Standards Board (SASB)'),
        ('TCFD', 'Task Force on Climate-related Financial Disclosures (TCFD)'),
        ('IFRS', 'International Financial Reporting Standards (IFRS)'),
        ('EU', 'European Union (EU)'),
        ('SEC', 'Securities and Exchange Commission (SEC)'),
        ('SARB', 'South African Reserve Bank (SARB)'),
        ('PRB', 'Principles for Responsible Banking (PRB)'),
        ('ISO', 'International Organization for Standardization (ISO)'),
        ('Fairtrade', 'Fairtrade'),
        ('FSC', 'Forest Stewardship Council (FSC)'),
        ('UNGC', 'United Nations Global Compact (UNGC)'),
    ]

    # Multiselect Fields
    compliance_frameworks = forms.MultipleChoiceField(
        choices=COMPLIANCE_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-control multiselect'}),
        required=True
    )

    report_sector = forms.MultipleChoiceField(
        choices=SECTOR_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-control multiselect'}),
        required=True
    )

    organization_name = forms.MultipleChoiceField(
        choices=ORGANIZATION_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-control multiselect'}),
        required=True
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
            'compliance_frameworks',
            'report_description',
            'report_file',
            'document_status'
        ]


        
        
from .models import TestTable

class TestTableForm(forms.ModelForm):
    class Meta:
        model = TestTable
        fields = ['name', 'description']






class CompanyCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'id': 'csv_file',
        }),
        label="Company List"
    )
    import_mode = forms.ChoiceField(
        choices=[
            ('overwrite', 'Overwrite (truncate and import)'),
            ('merge', 'Merge (update existing or create new)'),
        ],
        required=True,
        label="Import Mode",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'import_mode',
        }),
    )






from django import forms
from .models import ESGReportBatch, ESGCompany

class ESGReportBatchForm(forms.ModelForm):
    class Meta:
        model = ESGReportBatch
        fields = ['organization_name', 'industry_sector', 'country_region', 'organization_type', 'peer_group_name']

    def __init__(self, *args, **kwargs):
        super(ESGReportBatchForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'  # Add Bootstrap form-control class

    def clean_organization_name(self):
        organization_name = self.cleaned_data.get('organization_name')
        if ESGReportBatch.objects.filter(organization_name=organization_name).exists():
            raise forms.ValidationError("This organization already has a batch created.")
        return organization_name






from django import forms
from django.core.exceptions import ValidationError
from .models import CorporateBulkESGReports

class CorporateBulkESGReportsForm(forms.ModelForm):
    COMPLIANCE_CHOICES = [
        ('GRI', 'GRI (Global Reporting Initiative)'),
        ('TCFD', 'TCFD (Task Force on Climate-related Financial Disclosures)'),
        ('SASB', 'SASB (Sustainability Accounting Standards Board)'),
        ('King IV', 'King IV (South Africa)'),
        ('ISO 26000', 'ISO 26000 (Social Responsibility)'),
        ('ISO 14001', 'ISO 14001 (Environmental Management Systems)'),
        ('ISO 37001', 'ISO 37001 (Anti-bribery Management Systems)'),
        ('PRI', 'PRI (Principles for Responsible Investment)'),
        ('OECD Guidelines', 'OECD Guidelines for Multinational Enterprises'),
        ('NFRD', 'NFRD (Non-Financial Reporting Directive)'),
        ('CDP', 'CDP (Carbon Disclosure Project)'),
        ('SFDR', 'SFDR (Sustainable Finance Disclosure Regulation)'),
        ('EU Taxonomy', 'EU Taxonomy Regulation'),
        ('UN SDGs', 'UN Sustainable Development Goals (SDGs)'),
    ]
    
    BOOLEAN_CHOICES = [
        (True, 'Yes'),
        (False, 'No'),
    ]

    # Dynamically created 'standards_applied' as a MultipleChoiceField
    standards_applied = forms.MultipleChoiceField(
        choices=COMPLIANCE_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-control multiselect'}),
        required=True
    )

    # Update to ensure 'is_peer_report' and 'is_confidential' use dropdowns
    is_peer_report = forms.ChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    is_confidential = forms.ChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = CorporateBulkESGReports
        fields = [
            'document_title',
            'report_file',
            'reporting_year',
            'reporting_period',
            'standards_applied',
            'report_type',
            'is_peer_report',
            'peer_group_name',
            'is_confidential',
        ]

    def __init__(self, *args, **kwargs):
        super(CorporateBulkESGReportsForm, self).__init__(*args, **kwargs)
        # Add Bootstrap class to each field except 'standards_applied'
        for field in self.fields:
            if field != 'standards_applied':  # Check field name directly
                self.fields[field].widget.attrs['class'] = 'form-control'

    # Custom validation for unique document title
    def clean_document_title(self):
        document_title = self.cleaned_data['document_title']
        if CorporateBulkESGReports.objects.filter(document_title=document_title).exists():
            raise ValidationError("This document title already exists. Please choose a different title.")
        return document_title


    def clean(self):
        cleaned_data = super().clean()
        is_peer_report = cleaned_data.get('is_peer_report')
        peer_group_name = cleaned_data.get('peer_group_name')

        if is_peer_report == 'Yes' and not peer_group_name:
            self.add_error('peer_group_name', 'Peer Group Name is required when "Is Peer Report" is Yes.')
        
        return cleaned_data



class EvaluationForm(forms.ModelForm):
    company = forms.ModelChoiceField(
        queryset=ESGCompany.objects.all(),
        to_field_name='company_name',
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        empty_label="---Select Company---"
    )
    
    standard = forms.ModelChoiceField(
        queryset=ESGComplianceStandard.objects.all(),
        to_field_name='standard_code',
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        empty_label="---Select Standard---"
    )
    
    class Meta:
        model = Evaluation
        fields = ['company', 'standard']
        widgets = {
            'company': forms.Select(attrs={'class': 'form-select'}),
            'standard': forms.Select(attrs={'class': 'form-select'}),
        }