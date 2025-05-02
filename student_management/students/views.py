from django.shortcuts import render, redirect, get_object_or_404
from .models import StudentInfo
from .forms import StudentForm
from django.contrib import messages
from django.contrib.admin.models import LogEntry, CHANGE, ADDITION, DELETION
from django.contrib.contenttypes.models import ContentType
from .utils import log_student_action

def log_user_change(user, student_instance, message):
    LogEntry.objects.log_action(
        user_id=user.id,
        content_type_id=ContentType.objects.get_for_model(student_instance).pk,
        object_id=student_instance.pk,
        object_repr=str(student_instance),
        action_flag=CHANGE,
        change_message=message,
    )

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
            log_student_action(request.user, student, ADDITION, f"Added student: {student.name}")
            messages.success(request, f"Student '{student.name}' added successfully!")
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
            old_obj = StudentInfo.objects.get(pk=student.pk)
            updated_student = form.save(commit=False)

            changes = []
            for field in form.changed_data:
                old_value = getattr(old_obj, field)
                new_value = getattr(updated_student, field)
                if old_value != new_value:
                    changes.append(f"Changed the {field} of {old_obj.name} from {old_value} to {new_value}")

            updated_student.save()

            if changes:
                log_student_action(request.user, updated_student, CHANGE, ", ".join(changes))

            messages.success(request, f"Student '{student.name}' updated successfully!")
            return redirect('home')
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/form.html', {'form': form, 'title': 'Edit Student'})

# This view handles the deletion of a student.
def delete_students(request, pk):
    student = get_object_or_404(StudentInfo, pk=pk)
    log_student_action(request.user, student, DELETION, f"Deleted student: {student.name}")
    student.delete()
    messages.success(request, f"Student '{student.name}' deleted successfully!")
    return redirect('home')
