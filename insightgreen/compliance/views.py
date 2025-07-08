from django.contrib import messages
from django.shortcuts import redirect, render
from .models import ESGCompany, ESGComplianceReport

import fitz  # PyMuPDF

from .forms import CompanyCSVUploadForm, ESGComplianceReportForm, TestTableForm

# Create your views here.
def index(request):
    """
    Render the index page for the compliance app.
    """
    return render(request, 'compliance/index.html')

def graph(request):
    """
    Render the graph page for the compliance app.
    """
    return render(request, 'graph.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ESGComplianceReportForm

from datetime import datetime

def compliance_report_upload(request):
    if request.method == 'POST':
        form = ESGComplianceReportForm(request.POST, request.FILES)
        if form.is_valid():
            selected_compliance_frameworks = form.cleaned_data['compliance_frameworks']
            selected_organization_names = form.cleaned_data['organization_name']
            selected_report_sector = form.cleaned_data['report_sector']

            compliance_frameworks_str = ",".join(selected_compliance_frameworks)
            organization_names_str = ",".join(selected_organization_names)
            report_sector_str = ",".join(selected_report_sector)

            instance = form.save(commit=False)
            instance.compliance_frameworks = compliance_frameworks_str
            instance.organization_name = organization_names_str
            instance.report_sector = report_sector_str
            instance.save()

            messages.success(request, 'ESG Compliance Report submitted successfully!')
            return redirect('compliance_report_upload')
        else:
            messages.error(request, 'Error submitting the report. Please check the form.')
            print(form.errors)
    else:
        form = ESGComplianceReportForm()

    current_year = datetime.now().year
    years = list(range(2019, current_year + 2))  # e.g., 2019–2026 if current year is 2025

    return render(request, 'compliance/report_upload.html', {'form': form, 'years': years})






# Create new record
def testtable_create(request):
    if request.method == 'POST':
        form = TestTableForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = TestTableForm()
    return render(request, 'test.html', {'form': form})


def compliance_document_list(request):
    """
    List all compliance documents.
    """
    documents = ESGComplianceReport.objects.all()
    return render(request, 'compliance/document_list.html', {'documents': documents})

import os
from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
import re
from django.http import JsonResponse

def clean_pdf_text(text):
    # Split text into lines
    lines = text.splitlines()

    cleaned_lines = []
    buffer = ""

    for line in lines:
        stripped = line.strip()

        if not stripped:
            # Empty line — paragraph break
            if buffer:
                cleaned_lines.append(buffer)
                buffer = ""
            cleaned_lines.append("")
        else:
            if not buffer:
                buffer = stripped
            else:
                # If buffer ends with punctuation, start new line
                if re.search(r'[.,;:?!]$', buffer):
                    cleaned_lines.append(buffer)
                    buffer = stripped
                else:
                    # Otherwise join line with a space
                    buffer += " " + stripped

    # Append leftover buffer
    if buffer:
        cleaned_lines.append(buffer)

    # Join paragraphs by newline
    return "\n".join(cleaned_lines)


def extract_text_from_pdf(request, id):
    doc = get_object_or_404(ESGComplianceReport, id=id)

    try:
        with doc.report_file.open(mode='rb') as f:
            import fitz  # PyMuPDF
            pdf_doc = fitz.open(stream=f.read(), filetype="pdf")
            text = ""
            for page in pdf_doc:
                text += page.get_text()
            pdf_doc.close()

        # Clean the extracted text for better readability
        cleaned_text = clean_pdf_text(text)

        # Render extracted text in a template
        return render(request, 'compliance/view_extracted_text.html', {
            'document': doc,
            'extracted_text': cleaned_text,
            'file_details': doc,
        })

    except Exception as e:
        return render(request, 'compliance/view_extracted_text.html', {
            'document': doc,
            'error': f"Failed to extract text: {e}"
        })
    








import csv
import io
from django.db import connection, transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CompanyCSVUploadForm
from .models import ESGCompany

def upload_companies(request):
    if request.method == 'POST':
        form = CompanyCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            import_mode = form.cleaned_data['import_mode']

            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Uploaded file is not a CSV.')
                return redirect('upload_companies')

            try:
                decoded_file = csv_file.read().decode('utf-8-sig')
                io_string = io.StringIO(decoded_file)

                # Auto-detect delimiter
                sample = decoded_file[:1024]
                dialect = csv.Sniffer().sniff(sample)
                reader = csv.reader(io_string, dialect)

                # Skip header row
                next(reader, None)

                count = 0
                skipped = 0
                seen_names = set()

                with transaction.atomic():
                    if import_mode == 'overwrite':
                        table_name = ESGCompany._meta.db_table
                        with connection.cursor() as cursor:
                            cursor.execute(f'TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE')
                        # Optional fallback
                        ESGCompany.objects.all().delete()

                    for row in reader:
                        if len(row) < 4:
                            continue

                        row = [field.strip() for field in row]
                        name = row[0]

                        if name in seen_names:
                            skipped += 1
                            continue
                        seen_names.add(name)

                        if import_mode == 'overwrite':
                            ESGCompany.objects.create(
                                company_name=name,
                                contact_number=row[1],
                                contact_email=row[2],
                                website_url=row[3]
                            )
                        else:
                            ESGCompany.objects.update_or_create(
                                company_name=name,
                                defaults={
                                    'contact_number': row[1],
                                    'contact_email': row[2],
                                    'website_url': row[3]
                                }
                            )
                        count += 1

                messages.success(
                    request,
                    f"{count} companies imported successfully using '{import_mode}' mode."
                )
                if skipped:
                    messages.warning(
                        request,
                        f"{skipped} duplicate row(s) were skipped from the CSV file."
                    )

            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
    else:
        form = CompanyCSVUploadForm()

    companies = ESGCompany.objects.all().order_by('company_name')
    return render(request, 'compliance/upload_companies.html', {'form': form, 'companies': companies})







