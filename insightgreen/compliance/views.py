from django.contrib import messages
from django.shortcuts import redirect, render
from .models import ESGComplianceReport

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

def compliance_report_upload(request):
    if request.method == 'POST':
        form = ESGComplianceReportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'ESG Compliance Report submitted successfully!')
            return redirect('compliance_report_upload')  # Redirect to clear the form
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
from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
import re


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