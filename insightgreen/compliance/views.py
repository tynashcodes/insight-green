import json
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import ESGComplianceFramework, ESGComplianceReport

import fitz  # PyMuPDF

from .forms import ESGComplianceReportForm, TestTableForm

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

def compliance_report_upload(request):
    if request.method == 'POST':
        form = ESGComplianceReportForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the selected compliance frameworks (a list of values)
            selected_compliance_frameworks = form.cleaned_data['compliance_frameworks']
            
            # Join the selected values into a comma-separated string
            compliance_frameworks_str = ",".join(selected_compliance_frameworks)
            
            # Save the instance with the comma-separated values for compliance_frameworks
            instance = form.save(commit=False)
            instance.compliance_frameworks = compliance_frameworks_str
            instance.save()

            # Show a success message
            messages.success(request, 'ESG Compliance Report submitted successfully!')
            return redirect('compliance_report_upload')  # Redirect to avoid resubmitting the form
        else:
            messages.error(request, 'Error submitting the report. Please check the form.')
            print(form.errors)  # Debug: print errors to terminal/log
    else:
        form = ESGComplianceReportForm()

    return render(request, 'compliance/report_upload.html', {'form': form})




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
        truncated_text = full_text[:1000000]  # Limit to 1 million characters

        prompt = f"""
You are analyzing a text extracted from a sustainability PDF (like GRI Standards).

Please extract all sections that:
1. Start with a heading like "Disclosure X-X Title"
2. Are followed by a REQUIREMENTS section — extract this fully
3. If a RECOMMENDATIONS section normally comes after REQUIREMENTS, include it as well
4. Ignore any GUIDANCE sections
5. Preserve any bullet points, roman numerals, and numbers exactly as they appear — do not reformat or summarize
6. Include the page number for each disclosure (i.e., the page where the disclosure starts)

Format:
[
  {{
    "disclosure": "Disclosure 3-1 Title",
    "requirements": ["requirement 1", "requirement 2", "..."],
    "recommendations": ["recommendation 1", "..."],  # optional
    "page": 3
  }},
  ...
]

Here is the extracted document:
\"\"\" 
{truncated_text}
\"\"\"
"""

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        result = response.text.strip()

        # Try to load as JSON (clean any extra markdown if needed)
        json_str = result.strip('```json').strip('```')
        data = json.loads(json_str)

        # Save to DB
        for idx, item in enumerate(data):
            disclosure = ESGComplianceFramework.objects.create(
                document=doc,
                disclosure_title=item.get("disclosure"),
                page_number=item.get("page", 0),
                requirements="\n".join(item.get("requirements", [])),
                recommendations="\n".join(item.get("recommendations", [])) if "recommendations" in item else "",
                standard_area=doc.document_title
            )

        return JsonResponse({"message": "Disclosures and requirements saved successfully", "count": len(data)})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)