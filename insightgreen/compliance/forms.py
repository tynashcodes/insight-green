from django import forms
from .models import ESGComplianceReport

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
from .models import ESGCompany, ESGReport  # ✅ Make sure ESGReport is imported!

class ESGReportForm(forms.ModelForm):

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


    organization_name = forms.ModelChoiceField(
        queryset=ESGCompany.objects.all(),
        to_field_name='company_name',
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        empty_label="Select a company"
    )

    # Multiselect Fields
    standards_applied = forms.MultipleChoiceField(
        choices=COMPLIANCE_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-control multiselect'}),
        required=True
    )

    class Meta:
        model = ESGReport
        fields = [
            'report_file',
            'document_title',
            'organization_name',
            'industry_sector',
            'organization_type',
            'country_region',
            'reporting_year',
            'reporting_period',
            'report_type',
            'standards_applied',
            'is_peer_report',
            'peer_group_name',
            'is_confidential',
        ]


