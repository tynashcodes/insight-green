import uuid
from django.db import models

# Create your models here.

class ESGComplianceReport(models.Model):
    # Organization Name Choices
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


    # Report Sector Choices
    SECTOR_CHOICES = [
    ('Energy', 'Energy'),
    ('Financials', 'Financial Services'),
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

    
    # Geographical Region Choices
    REGION_CHOICES = [
        ('Africa', 'Africa'),
        ('Asia', 'Asia'),
        ('Europe', 'Europe'),
        ('North America', 'North America'),
        ('South America', 'South America'),
        ('Oceania', 'Oceania'),
    ]
    
    # Compliance Frameworks
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

    
    # Fields for the model (with auto-generated `id`)
    document_title = models.CharField(max_length=255)
    organization_name = models.TextField()
    reporting_year = models.IntegerField(choices=[(year, year) for year in range(2019, 2026)], default=2025)
    report_type = models.CharField(max_length=50, choices=[('Annual', 'Annual Report'), ('Quarterly', 'Quarterly Report'), ('Periodic', 'Periodic Updates')])
    document_version = models.CharField(max_length=50, blank=True)
    report_sector = models.TextField()
    compliance_frameworks = models.TextField()  # Changed to TextField to allow multiple selections
    geographical_region = models.CharField(max_length=50, choices=REGION_CHOICES, default='Not Necessary')
    report_description = models.TextField(blank=True)
    report_file = models.FileField(upload_to='esg_reports/')
    document_status = models.CharField(max_length=10, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_title} - {self.organization_name} ({self.reporting_year})"

    class Meta:
        ordering = ['-submitted_at']


class TestTable(models.Model):
    # Example test table for testing purposes
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']






class ESGCompany(models.Model):
    company_name = models.CharField(max_length=255, unique=True)
    contact_number = models.CharField(max_length=50)
    contact_email = models.EmailField()
    website_url = models.URLField()
    esg_compliant = models.BooleanField(default=False)  # Optional

    def __str__(self):
        return self.company_name
        
        
class ESGComplianceFramework(models.Model):
    document = models.ForeignKey(ESGComplianceReport, on_delete=models.CASCADE, related_name='disclosures')
    standard_area = models.CharField(max_length=255, null=True, blank=True)
    sub_standard_area = models.TextField(null=True, blank=True)  # Optional, for more detailed categorization
    disclosure_title = models.CharField(max_length=255, null=True, blank=True)  # e.g., "Disclosure 3-3 Management of material topics"
    requirements = models.TextField()  # Store the requirements section as text
    recommendations = models.TextField()  # Store the recommendations section as text, if applicable
    page_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.disclosure_title
    

class ESGComplianceFrameworkTest(models.Model):
    document = models.ForeignKey(ESGComplianceReport, on_delete=models.CASCADE, related_name='disclosures_test')
    standard_area = models.CharField(max_length=255, null=True, blank=True)
    sub_standard_area = models.TextField(null=True, blank=True)  # Optional, for more detailed categorization
    disclosure_title = models.CharField(max_length=255, null=True, blank=True)  # e.g., "Disclosure 3-3 Management of material topics"
    requirements = models.TextField()  # Store the requirements section as text
    recommendations = models.TextField()  # Store the recommendations section as text, if applicable
    page_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.disclosure_title









from django.db import models
from .models import ESGCompany  # assuming ESGCompany is in the same app

class ESGReportBatch(models.Model):
    # Industry Sectors Choices
    SECTOR_CHOICES = [
        ('Energy', 'Energy'),
        ('Financials', 'Financial Services'),
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

    # Geographical Region Choices
    REGION_CHOICES = [
        ('Africa', 'Africa'),
        ('Asia', 'Asia'),
        ('Europe', 'Europe'),
        ('North America', 'North America'),
        ('South America', 'South America'),
        ('Oceania', 'Oceania'),
    ]

    # Organization Type Choices
    ORGANIZATION_TYPE_CHOICES = [
        ('Public Company', 'Public Company'),
        ('Private Company', 'Private Company'),
        ('Government Entity', 'Government Entity'),
        ('Non-Profit', 'Non-Profit'),
        ('Financial Institution', 'Financial Institution'),
        ('State-Owned Enterprise', 'State-Owned Enterprise'),
        ('Multinational Corporation', 'Multinational Corporation'),
        ('Startup', 'Startup'),
        ('SME', 'Small & Medium Enterprise'),
        ('Other', 'Other'),
    ]

    # Shared fields for all reports in this batch
    organization_name = models.ForeignKey(ESGCompany, on_delete=models.CASCADE)
    industry_sector = models.CharField(max_length=255, choices=SECTOR_CHOICES)
    country_region = models.CharField(max_length=50, choices=REGION_CHOICES)
    organization_type = models.CharField(max_length=255, choices=ORGANIZATION_TYPE_CHOICES)
    peer_group_name = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Batch for {self.organization_name} - {self.peer_group_name}"





from django.db import models
from .models import ESGReportBatch

class CorporateBulkESGReports(models.Model):
    # Report Type Choices
    REPORT_TYPE_CHOICES = [
        ('Sustainability', 'Sustainability Report'),
        ('Integrated', 'Integrated Report'),
        ('Climate', 'Climate Report'),
        ('Annual', 'Annual Report'),
        ('Financial and ESG', 'Financial and ESG Report'),
        ('Other', 'Other'),
    ]

    # Fields for the dynamic attributes of each report in the batch
    report_file = models.FileField(upload_to='corporate_reports/')
    document_title = models.CharField(max_length=255, unique=True)
    
    # Dynamic fields for each report
    reporting_year = models.IntegerField(choices=[(year, year) for year in range(2019, 2026)], default=2025)
    reporting_period = models.CharField(max_length=50, choices=[('Annual', 'Annual Report'), 
                                                                ('Quarterly', 'Quarterly Report'), 
                                                                ('Periodic', 'Periodic Updates')])
    standards_applied = models.TextField()  # Can be a list or free text about which ESG standards are applied
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES, default='Annual')

    # Peer Group and Confidentiality
    is_peer_report = models.BooleanField(default=False)
    peer_group_name = models.CharField(max_length=255, blank=True, null=True)
    is_confidential = models.BooleanField(default=False)
    
    # Relationship to the ESGReportBatch for shared fields
    batch = models.ForeignKey(ESGReportBatch, on_delete=models.CASCADE, related_name="reports")
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_title} - {self.reporting_year} ({self.report_type})"

    class Meta:
        unique_together = ('batch', 'document_title', 'reporting_year', 'report_type')






class ExtractedReportPage(models.Model):
    report = models.ForeignKey(CorporateBulkESGReports, on_delete=models.CASCADE, related_name='extracted_pages')
    page_number = models.PositiveIntegerField()
    page_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('report', 'page_number')  # Prevent duplicate pages

    def __str__(self):
        return f"Page {self.page_number} of {self.report.document_title}"

class ESGComplianceStandard(models.Model):
    standard_code = models.CharField(max_length=50, unique=True)
    standard_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.standard_name
    

class Evaluation(models.Model):
    company = models.ForeignKey(ESGCompany, on_delete=models.CASCADE, related_name='evaluations')
    standard = models.ForeignKey(ESGComplianceStandard, on_delete=models.CASCADE, related_name='standard_evaluation')
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluation for {self.company.name} - {self.standard.name}"
    


class ESGComplianceScore(models.Model):
    compliance_item = models.ForeignKey('ESGComplianceFramework', on_delete=models.CASCADE, related_name='scores')
    page = models.ForeignKey('ExtractedReportPage', on_delete=models.SET_NULL, null=True, blank=True)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='scores', null=True, blank=True)
    score = models.DecimalField(max_digits=2, decimal_places=1)
    feedback = models.TextField()
    recommendation = models.TextField(null=True, blank=True)
    paragraph = models.TextField(null=True, blank=True)
    matched_text_excerpt = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Score {self.score} for {self.compliance_item} on {self.report}"


class ESGComplianceSummary(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='summary_scores', null=True, blank=True)
    total_score = models.DecimalField(max_digits=5, decimal_places=2)
    total_possible = models.IntegerField()
    compliance_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report.document_title} – {self.compliance_percentage}%"

    
    
    


    
    