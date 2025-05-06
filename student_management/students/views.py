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

#machine learning
import os
import joblib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



def get_interest_choices():
    interests = StudentInfo.objects.values_list('interest', flat=True).distinct()
    choices = [(i, i.title()) for i in interests if i]  # avoid None/empty
    return choices


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
        form.fields['interest'].choices = INTEREST_CHOICES
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
        form.fields['interest'].choices = INTEREST_CHOICES
    return render(request, 'students/form.html', {'form': form, 'title': 'Edit Student'})


# This view handles the deletion of a student.
def delete_students(request, pk):
    student = get_object_or_404(StudentInfo, pk=pk)
    log_student_action(request.user, student, DELETION, f"Deleted student: {student.name}")
    student.delete()
    messages.success(request, f"Student '{student.name}' deleted successfully!")
    return redirect('home')



#Machine Learning
# Get BASE_DIR (one level up from your current file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load ML model and interest mapping
model_path = os.path.join(BASE_DIR, 'machine_learning', 'course_predictor.joblib')
interest_map_path = os.path.join(BASE_DIR, 'machine_learning', 'interest_mapping.joblib')

model = joblib.load(model_path)
interest_map = joblib.load(interest_map_path)

# Convert interest_map keys to choices for dropdown
INTEREST_CHOICES = sorted([(key, key.title()) for key in interest_map.keys()], key=lambda x: x[1])

@csrf_exempt
def predict_course(request):
    if request.method == "POST":
        try:
            age = int(request.POST.get("age"))
            gender = request.POST.get("gender")
            interest = request.POST.get("interest")

            gender_encoded = 0 if gender.lower() == "male" else 1
            interest_encoded = interest_map.get(interest.lower())

            if interest_encoded is None:
                return JsonResponse({"error": "Unknown interest"}, status=400)

            prediction = model.predict([[age, gender_encoded, interest_encoded]])
            return JsonResponse({"predicted_course": prediction[0]})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST allowed"}, status=405)