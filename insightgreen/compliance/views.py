from django.shortcuts import render

# Create your views here.
def index(request):
    """
    Render the index page for the compliance app.
    """
    return render(request, 'compliance/index.html')

def compliance_report_upload(request):
    """
    Handle the upload of compliance reports.
    """
    if request.method == 'POST':
        # Handle file upload logic here
        pass
    return render(request, 'compliance/report_upload.html')