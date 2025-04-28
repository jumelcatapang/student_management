from django.shortcuts import render, redirect, get_object_or_404
from .models import StudentInfo
from .forms import StudentForm

# This view handles the home page and student listing.
def home(request):
    query = request.GET.get('q')
    if query:
        students = StudentInfo.objects.filter(name__icontains=query)
    else:
        students = StudentInfo.objects.all()
    return render(request, 'students/index.html', {'students': students})

# This view handles displaying details of a single student.
def view_students(request, pk):
    student = get_object_or_404(StudentInfo, pk=pk)
    return render(request, 'students/view.html', {'student': student})
    
# This view handles the addition of a new student.
def add_students(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.save()
            return redirect('home')
    else:
        form = StudentForm()
    return render(request, 'students/form.html', {'form': form, 'title': 'Add Student'})

# This view handles the editing of an existing student.
def edit_students(request, pk):
    student = get_object_or_404(StudentInfo, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/form.html', {'form': form, 'title': 'Edit Student'})

# This view handles the deletion of a student.
def delete_students(request, pk):
    student = get_object_or_404(StudentInfo, pk=pk)
    student.delete()
    return redirect('home')
