from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Student, Assignment, Notice

def dashboard(request):
    # Latest 5 notices aur assignments fetch karo
    notices = Notice.objects.all()[:5]
    assignments = Assignment.objects.all()[:5]
    
    context = {
        'notices': notices,
        'assignments': assignments,
    }
    return render(request, 'tracker/dashboard.html', context)

def assignment_list(request):
    # Saare assignments, due date ke hisaab se sorted (models.py mein Meta ordering hai)
    assignments = Assignment.objects.all()
    return render(request, 'tracker/assignment_list.html', {'assignments': assignments})

def student_register(request):
    if request.method == 'POST':
        roll_no = request.POST.get('roll_no', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        department = request.POST.get('department', 'CSE')
        semester = request.POST.get('semester', 1)
        
        # Basic validation
        if roll_no and full_name:
            try:
                Student.objects.create(
                    roll_no=roll_no,
                    full_name=full_name,
                    email=email,
                    department=department,
                    semester=int(semester)
                )
                messages.success(request, "✅ Student registered successfully!")
                return redirect('student_register')
            except Exception as e:
                messages.error(request, f"❌ Error: Roll No might already exist. ({e})")
        else:
            messages.error(request, "❌ Roll No and Full Name are required.")
            
    return render(request, 'tracker/student_register.html')