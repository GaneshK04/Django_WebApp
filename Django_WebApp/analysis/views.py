from django.shortcuts import render, redirect, get_object_or_404
from .forms import UploadFileForm
from .models import UploadedFile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = UploadedFile(file=request.FILES['file'])
            uploaded_file.save()
            return redirect('analysis:process_file', pk=uploaded_file.pk)
    else:
        form = UploadFileForm()
    return render(request, 'analysis/upload.html', {'form': form})

def process_file(request, pk):
    uploaded_file = get_object_or_404(UploadedFile, pk=pk)
    df = pd.read_csv(uploaded_file.file.path)
    
    summary_stats = df.describe().to_html()
    first_rows = df.head().to_html()
    missing_values = df.isnull().sum().to_dict()

  
    fig, ax = plt.subplots()
    df.hist(ax=ax)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_png = buf.getvalue()
    buf.close()
    hist_data = base64.b64encode(image_png).decode('utf-8')

    context = {
        'summary_stats': summary_stats,
        'first_rows': first_rows,
        'missing_values': missing_values,
        'hist_data': hist_data,
    }
    return render(request, 'analysis/results.html', context)
