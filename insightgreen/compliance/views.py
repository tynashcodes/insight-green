import json
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import ESGComplianceFramework, ESGComplianceReport, ExtractedReportPage, Evaluation, ESGComplianceStandard

import fitz  # PyMuPDF

from .forms import CompanyCSVUploadForm, ESGComplianceReportForm, TestTableForm, EvaluationForm

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
        if "GRI" in doc.document_title:
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
        elif "IFRS S1" in doc.document_title:
            prompt = f"""
You are analyzing text extracted from an IFRS S2 PDF focused on climate-related disclosures.
Your task is to extract ESG compliance framework elements using the following instructions:

1.  Identify and extract disclosures related to these four main pillars (standard areas): Governance, Strategy, Risk Management, Metrics and Targets.
2.  Sub-standard areas are subheadings or thematic groupings under each standard area. For example: “Climate-related risks and opportunities” or “Business model and value chain” under Strategy.
3.  The disclosure title should reflect the overarching section title (e.g., Strategy, Risk Management).
4.  Requirements:
    - Extract each requirement as a separate entry.
    - Any item under a disclosure or sub-standard area that is marked with a bullet (•), number (1., 2.), letter (a), (b), or roman numeral (i), (ii) must be treated as a separate and standalone requirement row.
    - Do not combine multiple subpoints into a single requirement, even if they belong to the same paragraph or section.
    - Include bold text and numbered/bulleted text beneath headings as part of the requirement content.
    - There are no “Recommendations” in IFRS S2, so omit any mention of them.
5.  Maintain the structure and phrasing of the original content — do not paraphrase. Preserve any formatting such as bullets or indentation exactly.
6.  For each requirement, record the page number where it appears.

Output format (note: each requirement should be a separate object)
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
            return JsonResponse({'error': 'Unknown compliance framework. GRI or IFRS S1 expected.'}, status=400)

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









from django.contrib import messages
from django.shortcuts import render
from .forms import ESGReportBatchForm

def create_esg_report_batch(request):
    if request.method == 'POST':
        form = ESGReportBatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "ESG Report Batch created successfully!")
        else:
            # Form is invalid, display error message
            messages.error(request, "There was an error creating the batch. Please check the form and try again.")
    else:
        form = ESGReportBatchForm()
    
    return render(request, 'compliance/create_esg_report_batch.html', {'form': form})


    


from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ESGReportBatch, CorporateBulkESGReports
from .forms import CorporateBulkESGReportsForm
from django.contrib import messages

def upload_bulk_reports(request, batch_id):
    # Get the batch object or redirect if not found
    try:
        batch = ESGReportBatch.objects.get(id=batch_id)
    except ESGReportBatch.DoesNotExist:
        return HttpResponse('Batch not found', status=404)

    if request.method == 'POST':
        form = CorporateBulkESGReportsForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.batch = batch  # Associate the report with the batch
            
            # Join the selected standards into a comma-separated string
            report.standards_applied = ",".join(form.cleaned_data['standards_applied'])
            
            report.save()
            messages.success(request, "Report uploaded successfully!")
        else:
            messages.error(request, "There was an error with your submission. Please check the form.")
    
    else:
        form = CorporateBulkESGReportsForm()

    context = {
        'batch': batch,
        'form': form,
    }
    
    return render(request, 'compliance/upload_bulk_reports.html', context)



from django.shortcuts import render, redirect
from .models import ESGReportBatch


def list_esg_report_batch(request):
    # Fetch all ESGReportBatch objects
    batches = ESGReportBatch.objects.all()

    context = {
        'batches': batches
    }

    return render(request, 'compliance/list_esg_report_batch.html', context)




from django.shortcuts import render
from .models import CorporateBulkESGReports  # Updated model name
from django.contrib import messages

def list_corporate_report_batch(request):
    # Fetch all CorporateBulkESGReports objects and related ESGReportBatch data
    reports = CorporateBulkESGReports.objects.select_related('batch').all()  # Use 'batch' to reference the ForeignKey

    # Add a message if there are no reports
    if not reports:
        messages.info(request, "No corporate ESG reports available.")

    context = {
        'reports': reports
    }

    return render(request, 'compliance/list_corporate_report_batch.html', context)



import os
import fitz  # PyMuPDF
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import ExtractedReportPage
import re
from django.conf import settings


def extract_full_text_using_gemini_flash(request, report_id):
    report = get_object_or_404(CorporateBulkESGReports, id=report_id)
    path = report.report_file.path
    ext = os.path.splitext(path)[1].lower()

    if ext != ".pdf":
        messages.error(request, f"Unsupported file format: {ext}")
        return redirect('report_detail', report_id=report.id)

    try:
        # ✅ Configure Gemini
        genai.configure(api_key="AIzaSyA5hzMuaEzsJC_mE5L4IorTi_RWcu6PSpQ")  # Replace with secure access in production
        model = genai.GenerativeModel("models/gemini-2.0-flash")

        # ✅ Extract text from PDF
        doc = fitz.open(path)
        full_raw_text = "\n\n".join([page.get_text("text") for page in doc]).strip()

        # ✅ Define chunking function
        def chunk_text(text, max_chars=100_000):
            for i in range(0, len(text), max_chars):
                yield text[i:i + max_chars]

        cleaned_chunks = []
        prompt = (
            "Carefully read and clean the following ESG report text. "
            "Fix broken line breaks and merge lines that are part of the same sentence or paragraph. "
            "Preserve paragraph structure and logical flow. Do not summarize, skip, or rephrase. "
            "Maintain original content faithfully, making it readable and continuous where it was broken."
        )

        # ✅ Process each chunk through Gemini
        for idx, chunk in enumerate(chunk_text(full_raw_text)):
            print(f"Sending chunk {idx + 1} to Gemini (length: {len(chunk)})")
            response = model.generate_content([prompt, chunk])
            cleaned = response.text.strip()
            cleaned_chunks.append(cleaned)

        full_cleaned_text = "\n\n".join(cleaned_chunks).strip()

        # ✅ Save result to DB
        ExtractedReportPage.objects.update_or_create(
            report=report,
            page_number=1,
            defaults={"page_text": full_cleaned_text}
        )

        messages.success(request, "Text extracted and cleaned using Gemini 2.0 Flash successfully.")

    except Exception as e:
        messages.error(request, f"Gemini extraction error: {e}")

    return redirect('report_detail', report_id=report.id)


from django.shortcuts import render, get_object_or_404
from .models import ESGComplianceScore, ESGComplianceSummary
from .services import evaluate_report_against_framework

def compliance_analysis_view(request):
    pages = ExtractedReportPage.objects.all().select_related("report")
    scores = ESGComplianceScore.objects.all().select_related("page", "compliance_item")
    summary = ESGComplianceSummary.objects.last()  # latest summary

    return render(request, 'compliance/compliance_analysis.html', {
        'pages': pages,
        'scores': scores,
        'summary': summary,
    })

from django.views.decorators.http import require_POST

@require_POST
def ajax_run_compliance(request, evaluation_id):
    try:
        evaluation = Evaluation.objects.get(id=evaluation_id)
        
        summary = evaluate_report_against_framework(evaluation)

        if summary is None:
            return JsonResponse({"message": "Evaluation completed, but no scores were generated."}, status=400)

        redirect_url = reverse('evaluation_list')

        return JsonResponse({
            "message": "Evaluation completed successfully.",
            "summary": {
                "compliance_percentage": float(summary.compliance_percentage),
                "total_score": float(summary.total_score),
                "total_possible": summary.total_possible,
            },
            "redirect_url": redirect_url
        })
    
    except Exception as e:
        return JsonResponse({"message": f"Error: {str(e)}"}, status=500)



def compliance_summary_detail(request, summary_id):
    summary = get_object_or_404(ESGComplianceSummary, id=summary_id)
    return render(request, 'compliance/summary_detail.html', {'summary': summary})



def evaluation_list(request):
    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evaluation created successfully!')
            
    else:
        form = EvaluationForm()
    
    evaluations = Evaluation.objects.all().select_related('company', 'standard')
    return render(request, 'compliance/evaluation_list.html', {'form': form, 'evaluations': evaluations})


def loading(request):
    """
    Render a loading page.
    """
    return render(request, 'compliance/loading.html')


def evaluation_scoring_findings(request, evaluation_id):
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    scores = ESGComplianceScore.objects.filter(evaluation=evaluation).select_related('page', 'compliance_item')
    summary = ESGComplianceSummary.objects.filter(evaluation_id=evaluation).first()
    
    return render(request, 'compliance/evaluation_scoring_findings.html', {
        'evaluation': evaluation,
        'scores': scores,
        'summary': summary
    })
    
def scoring_history(request):
    """
    Render the scoring history page.
    """
    summaries = ESGComplianceSummary.objects.all().order_by('-generated_at')
    return render(request, 'compliance/scoring_history.html', {'summaries': summaries})


def extracted_framework_list(request):
    """
    Render a list of extracted framework items.
    """
    framework_items = ESGComplianceFramework.objects.all().select_related('document')
    return render(request, 'compliance/extracted_framework_list.html', {'framework_items': framework_items})


def compliance_standards(request):
    """
    Render a list of compliance standards.
    """
    standards = ESGComplianceStandard.objects.all()
    compliance_framework = ESGComplianceFramework.objects.all().select_related()
    return render(request, 'compliance/compliance_standards.html', {'standards': standards})

def peer_benchmarking_overview(request):
    return render(request, 'benchmarking/overview.html')







from django.shortcuts import render
from .models import ESGReportBatch, CorporateBulkESGReports

def report_batch_list(request):
    # Query for ESGReportBatch with related CorporateBulkESGReports
    report_batches = ESGReportBatch.objects.prefetch_related('reports').all()

    return render(request, 'compliance/report_batch_list.html', {'report_batches': report_batches})






def compliance_standards_findings(request):
    """
    Render a list of compliance standards findings.
    """
    # findings = ESGComplianceFramework.objects.all().select_related('document')
    return render(request, 'scoring/compliance_standards_findings.html')





def compliance_standards_findings_overview(request):
    """
    Render an overview of compliance standards findings.
    """
    # findings = ESGComplianceFramework.objects.all().select_related('document')
    return render(request, 'scoring/compliance_standards_findings_overview.html')