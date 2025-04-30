from django.shortcuts import render, redirect, get_object_or_404
from .models import StudentInfo
from .forms import StudentForm

#machine learning
import os
import joblib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


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



#Machine Learning
# Get BASE_DIR (one level up from your current file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load ML model and interest mapping
model_path = os.path.join(BASE_DIR, 'machine_learning', 'course_predictor.joblib')
interest_map_path = os.path.join(BASE_DIR, 'machine_learning', 'interest_mapping.joblib')

model = joblib.load(model_path)
interest_map = joblib.load(interest_map_path)

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