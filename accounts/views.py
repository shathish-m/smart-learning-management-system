from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import StudentRegisterForm
from django.db.models import Q
from .models import Student, Course
from accounts.models import Course
from urllib.parse import urlparse, parse_qs
from accounts.models import Enrolled
from .models import Assignment, Enrolled  
from django.urls import reverse
from .models import Feedback
from django.contrib import messages


# Home page
def index_view(request):
    return render(request, 'index.html')

# Register new user
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash password
            user.save()
            messages.success(request, "✅ Registered successfully! Please log in.")
            return redirect('login')
        else:
            messages.error(request, "❌ Registration failed. Please check the details.")
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

# Login
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {"error": "Invalid credentials"})
    return render(request, "login.html")

# Home (after login)
@login_required(login_url='login')
def home_view(request):
    return render(request, "home.html")

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# COURSE MANAGEMENT

# List all courses
@login_required(login_url='login')
def course_management(request):
    courses = Course.objects.all()
    return render(request, 'course-management.html', {'courses': courses})

# Add course
@login_required(login_url='login')
def add_course(request):
    if request.method == 'POST':
        Course.objects.create(
            name=request.POST['name'],
            instructor=request.POST['instructor'],
            description=request.POST['description'],
            video_link=request.POST['video_link'],
            image = request.FILES.get('image')  
        )
    return redirect('course_management')

# Edit course
@login_required(login_url='login')
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.name = request.POST['name']
        course.instructor = request.POST['instructor']
        course.description = request.POST['description']
        course.video_link = request.POST['video_link']

        if 'image' in request.FILES:
            course.image = request.FILES['image'] 
        course.save()
    return redirect('course_management')

# Delete course
@login_required(login_url='login')
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    return redirect('course_management')


def student_register(request):
    if request.method == 'POST':
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_login')
    else:
        form = StudentRegisterForm()
    return render(request, 'studentauth/register.html', {'form': form})

def student_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            student = Student.objects.get(username=username, password=password)
            # Store username in session
            request.session['username'] = student.username
            return redirect('student_dashboard')
        except Student.DoesNotExist:
            return render(request, 'studentauth/login.html', {'error': 'Invalid username or password'})
    return render(request, 'studentauth/login.html')



def student_list(request):
    query = request.GET.get('q', '').strip()
    students = Student.objects.all()
    if query:
        students = students.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query)
        )
    students = students.order_by('username')
    return render(request, 'student_list.html', {'students': students, 'q': query})


def student_dashboard(request):
    if 'username' not in request.session:
        return redirect('student_login')  # Force login if session expired

    student = Student.objects.get(username=request.session['username'])
    courses = Course.objects.all()
    return render(request, 'studentauth/student_home.html', {'student': student, 'courses': courses})


def get_youtube_id(url):
    """
    Extracts YouTube video ID from various URL formats.
    """
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()

    if host == "youtu.be":
        return parsed.path.lstrip("/")
    if host in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]
        if parsed.path.startswith("/embed/"):
            return parsed.path.split("/")[2]
        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/")[2]
    return None


def course_showcase(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    assignments = Assignment.objects.filter(course=course)
    youtube_id = get_youtube_id(course.video_link)  # your defined helper function

    students = Student.objects.all()  # Fetch all students
    courses = Course.objects.all()    # Fetch all courses

    # Enrollment check (optional)
    student_name = request.session.get('student_name')
    is_enrolled = False
    if student_name:
        is_enrolled = Enrolled.objects.filter(student_name=student_name, course_name=course.name).exists()

    context = {
        'course': course,
        'assignments': assignments,
        'youtube_id': youtube_id,
        'students': students,
        'courses': courses,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'studentauth/course_showcase.html', context)





def enroll_course(request):
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        course_name = request.POST.get('course_name')
        course = Course.objects.get(name=course_name)
        course_id = course.id

        # Save the enrollment
        Enrolled.objects.create(
            student_name=student_name,
            course_name=course_name
        )

        if Enrolled.objects.filter(student_name=student_name, course_name=course_name).exists():
            messages.warning(request, "You are already enrolled in this course.")
        else:
            Enrolled.objects.create(student_name=student_name, course_name=course_name)
            messages.success(request, "Enrollment successful!")

        return redirect('course_showcase', course_id=course_id)

    return redirect('course_showcase')





def enrolled_students_list(request):
    students = Enrolled.objects.all().order_by('-enrolled_date')  # Latest first
    return render(request, 'enrolled_students.html', {'students': students})


def assignment_list_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        course_id = request.POST.get('course')
        file = request.FILES.get('file')

        if title and course_id and file:
            course = Course.objects.get(id=course_id)
            Assignment.objects.create(title=title, file=file, course=course)
            return redirect('assignment_list')  # Change to your url name

    assignments = Assignment.objects.all()
    courses = Course.objects.all()
    return render(request, 'assignments.html', {
        'assignments': assignments,
        'courses': courses
    })




def course_detail(request, course_id):
    # Get the course by ID, or return 404 if not found
    course = get_object_or_404(Course, id=course_id)

    # Filter assignments for this particular course
    assignments = Assignment.objects.filter(course=course)

    # Initialize flag
    feedback_submitted = False

    # Process feedback form submission (if any)
    if request.method == 'POST' and 'user_name' in request.POST:
        user_name = request.POST.get('user_name')
        rating = request.POST.get('rating')
        feedback_text = request.POST.get('feedback_text')

        Feedback.objects.create(
            user_name=user_name,
            rating=rating,
            feedback_text=feedback_text
        )

        feedback_submitted = True

    # Context variables for enroll modal
    students = Student.objects.all()
    courses = Course.objects.all()

    # Determine if current logged-in user is enrolled in the course
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrolled.objects.filter(
            student__username=request.user.username,
            course=course
        ).exists()

    context = {
        'course': course,
        'assignments': assignments,
        'feedback_submitted': feedback_submitted,
        'students': students,
        'courses': courses,
        'is_enrolled': is_enrolled,
    }

    return render(request, 'studentauth/course_showcase.html', context)



def submit_feedback(request):
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        rating = request.POST.get('rating')
        feedback_text = request.POST.get('feedback_text')

        # Save feedback to DB
        Feedback.objects.create(
            user_name=user_name,
            rating=rating,
            feedback_text=feedback_text
        )
        # Redirect back or to a thank you page after submission
        return redirect(reverse('course_detail', kwargs={'course_id': request.POST.get('course_id')}))  
        # Adjust redirect URL/name as per your routing

    # For GET or others, you can redirect or show an error
    return redirect('studentauth/course_showcase.html')  # Adjust as needed




def feedback_list(request):
    feedbacks = Feedback.objects.all().order_by('-submitted_at')
    return render(request, 'feedback.html', {'feedbacks': feedbacks})


