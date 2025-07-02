from django.db import models

# Create your models here.
from django.db import models

class ESGComplianceReport(models.Model):
    # Organization Name Choices
    ORGANIZATION_CHOICES = [
        ('GRI Standards', 'GRI Standards'),
        ('TCFD', 'TCFD (Task Force on Climate-related Financial Disclosures)'),
        ('SASB', 'SASB (Sustainability Accounting Standards Board)'),
        ('King IV', 'King IV (South Africa)'),
        ('CDP', 'CDP (Carbon Disclosure Project)'),
        ('UNGC', 'UNGC (United Nations Global Compact)'),
    ]
    
    # Report Sector Choices
    SECTOR_CHOICES = [
        ('Energy', 'Energy'),
        ('Manufacturing', 'Manufacturing'),
        ('Technology', 'Technology'),
        ('Financial Services', 'Financial Services'),
        ('Healthcare', 'Healthcare'),
        ('Retail', 'Retail'),
        ('Telecommunications', 'Telecommunications'),
        ('Transportation', 'Transportation'),
        ('Consumer Goods', 'Consumer Goods'),
        ('Real Estate', 'Real Estate'),
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
    ]
    
    # Fields for the model (with auto-generated `id`)
    document_title = models.CharField(max_length=255)
    organization_name = models.CharField(max_length=100, choices=ORGANIZATION_CHOICES)
    reporting_year = models.IntegerField(choices=[(year, year) for year in range(2019, 2026)], default=2025)
    report_type = models.CharField(max_length=50, choices=[('Annual', 'Annual Report'), ('Quarterly', 'Quarterly Report'), ('Interim', 'Interim Report')])
    document_version = models.CharField(max_length=50, blank=True)
    report_sector = models.CharField(max_length=100, choices=SECTOR_CHOICES)
    compliance_frameworks = models.TextField()  # Changed to TextField to allow multiple selections
    geographical_region = models.CharField(max_length=50, choices=REGION_CHOICES)
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