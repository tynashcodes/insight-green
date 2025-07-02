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
from django.http import JsonResponse

def extract_text_from_pdf(request, id):
    doc = get_object_or_404(ESGComplianceReport, id=id)

    try:
        with doc.report_file.open(mode='rb') as f:
            pdf = fitz.open(stream=f.read(), filetype="pdf")

            headings = set()

            for page in pdf:
                blocks = page.get_text("dict")["blocks"]
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span.get("text", "").strip()
                                font_size = span.get("size", 0)

                                # You can tweak this threshold based on your PDF style
                                if font_size >= 14 and text:
                                    headings.add(text)

            pdf.close()

        return JsonResponse({"headings": sorted(headings)}, json_dumps_params={'indent': 2})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)