from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse
import json

from .models import ScanHistory
from .utils import extract_text_from_file, analyze_text_mock

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'detector/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'detector/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    return render(request, 'detector/dashboard.html')

@login_required
def analyze_text_api(request):
    if request.method == 'POST':
        text_content = ""
        filename = ""
        
        # Check if file was uploaded
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            filename = uploaded_file.name
            try:
                text_content = extract_text_from_file(uploaded_file, filename)
            except Exception as e:
                return JsonResponse({'error': f'Failed to process file: {str(e)}'}, status=400)
        else:
            text_content = request.POST.get('text', '').strip()
            
        if not text_content:
            return JsonResponse({'error': 'No text provided'}, status=400)
            
        # Analyze text
        analysis_result = analyze_text_mock(text_content)
        
        # Save to history
        scan = ScanHistory.objects.create(
            user=request.user,
            filename=filename,
            analyzed_text=text_content,
            ai_probability=analysis_result['ai_probability'],
            perplexity=analysis_result['perplexity'],
            burstiness=analysis_result['burstiness'],
            heatmap_data=analysis_result['heatmap_data']
        )
        
        # Add id to result
        analysis_result['id'] = scan.id
        
        return JsonResponse(analysis_result)
        
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def history_list_view(request):
    scans = ScanHistory.objects.filter(user=request.user)
    return render(request, 'detector/history.html', {'scans': scans})

@login_required
def history_detail_view(request, pk):
    scan = get_object_or_404(ScanHistory, pk=pk, user=request.user)
    return render(request, 'detector/history_detail.html', {'scan': scan})
