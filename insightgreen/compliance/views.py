import json
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import ESGComplianceFramework, ESGComplianceReport, ESGReport

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
import re
import fitz  # PyMuPDF
import google.generativeai as genai
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ESGComplianceReport

# Configure Gemini with your API key
genai.configure(api_key="AIzaSyA5hzMuaEzsJC_mE5L4IorTi_RWcu6PSpQ")

def clean_pdf_text(text):
    lines = text.splitlines()
    cleaned_lines = []
    buffer = ""

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if buffer:
                cleaned_lines.append(buffer)
                buffer = ""
            cleaned_lines.append("")
        else:
            if not buffer:
                buffer = stripped
            else:
                if re.search(r'[.,;:?!]$', buffer):
                    cleaned_lines.append(buffer)
                    buffer = stripped
                else:
                    buffer += " " + stripped

    if buffer:
        cleaned_lines.append(buffer)

    return "\n".join(cleaned_lines)

def extract_text_from_pdf(request, id):
    doc = get_object_or_404(ESGComplianceReport, id=id)

    try:
        with doc.report_file.open(mode='rb') as f:
            pdf = fitz.open(stream=f.read(), filetype="pdf")
            page_texts = []
            for i, page in enumerate(pdf, start=1):
                raw_text = page.get_text()
                cleaned = clean_pdf_text(raw_text)
                page_texts.append(f"[Page {i}]\n{cleaned}")
            pdf.close()

        full_text = "\n\n".join(page_texts)
        truncated_text = full_text[:1000000]

        # Determine which prompt to use
        if "GRI" in doc.compliance_frameworks:
            prompt = f"""
You are analyzing a text extracted from a sustainability PDF based on GRI Standards.

Please extract all sections that:
1. Start with a heading like "Disclosure X-X Title"
2. Are followed by a REQUIREMENTS section — extract this fully
3. If a RECOMMENDATIONS section comes after REQUIREMENTS, include it as well
4. Ignore any GUIDANCE sections
5. Preserve bullet points, roman numerals, and numbers exactly as they appear
6. Include the page number where each disclosure begins

Format:
[
  {{
    "disclosure": "Disclosure 3-1 Title",
    "requirements": ["..."],
    "recommendations": ["..."],  # optional
    "page": 3
  }},
  ...
]

Text:
\"\"\"
{truncated_text}
\"\"\"
"""
        elif "IFRS S2" in doc.document_title:
            prompt = f"""
You are analyzing a text extracted from an IFRS S2 PDF focused on climate-related disclosures.

Please extract sections that:
1. Cover the following four pillars as standard areas or disclosures: Governance, Strategy, Risk Management, Metrics and Targets
2. Sub Standard Area is a sub heading under each standard area e.g. Climate-related risks and opportunities, Business model and value chain etc. under Strategy and disclosure title is the main heading e.g. Strategy
3. Requirements are the specific requirements under each sub standard area and sometimes a standard area has requirements as well, take everything under the sub standard area or standard area as requirements even bold paragraphs
4. There are no RECOMMENDATIONS in IFRS S2.
5. Preserve section titles and bullet point structure (numbers, roman numerals, bullets) exactly as they appear
6. For each section, include the page number where it was found

Format:
[
  {{
    "disclosure": "Strategy",
    "requirements": ["..."],
    "sub_standard_area": "",
    "page": 4
  }},
  ...
]

Text:
\"\"\"
{truncated_text}
\"\"\"
"""
        else:
            return JsonResponse({'error': 'Unknown compliance framework. GRI or IFRS S2 expected.'}, status=400)

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt.strip())
        result = response.text.strip()

        json_str = result.strip('```json').strip('```')
        data = json.loads(json_str)

        # Save to DB
        for item in data:
            ESGComplianceFramework.objects.create(
                document=doc,
                disclosure_title=item.get("disclosure"),
                page_number=item.get("page", 0),
                requirements="\n".join(item.get("requirements", [])),
                recommendations="\n".join(item.get("recommendations", [])) if "recommendations" in item else "",
                sub_standard_area=item.get("sub_standard_area", "") if "sub_standard_area" in item else "",
                standard_area=doc.document_title
            )

        return JsonResponse({"message": "Disclosures saved", "count": len(data)})

    except Exception as e:
        return render(request, 'compliance/view_extracted_text.html', {
            'document': doc,
            'error': f"Failed to extract text: {e}"
        })

    






from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ESGReportForm

def upload_corporate_report(request):
    if request.method == 'POST':
        form = ESGReportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "ESG Corporate Report uploaded successfully.")
            return redirect('upload_corporate_report')  # Or wherever you want
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ESGReportForm()

    return render(request, 'compliance/upload_corporate_report.html', {
        'form': form
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



def corporate_report_list(request):
    reports = ESGReport.objects.all()
    return render(request, 'compliance/corporate_report_list.html', {'reports': reports})





    