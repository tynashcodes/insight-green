from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ESGComplianceReportForm

# Create your views here.
def index(request):
    """
    Render the index page for the compliance app.
    """
    return render(request, 'compliance/index.html')

<<<<<<< HEAD
def graph(request):
    """
    Render the graph page for the compliance app.
    """
    return render(request, 'graph.html')
=======
def compliance_report_upload(request):
    if request.method == 'POST':
        form = ESGComplianceReportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'ESG Compliance Report submitted successfully!')
        else:
            messages.error(request, 'Error submitting the report. Please check the form.')
    else:
        form = ESGComplianceReportForm()
    return render(request, 'compliance/report_upload.html', {'form': form})
>>>>>>> 212f352442d019ff513574271baa895a9ed423f0
