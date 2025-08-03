from django.urls import path
from . import views


urlpatterns = [
    path('', views.index_view, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('courses/', views.course_management, name='course_management'),
    path('courses/add/', views.add_course, name='add_course'),
    path('courses/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('courses/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('student_register/', views.student_register, name='student_register'),
    path('student_login/', views.student_login, name='student_login'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('course/<int:course_id>/', views.course_showcase, name='course_showcase'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('enroll/', views.enroll_course, name='enroll_course'),
    path('enrolled_students/', views.enrolled_students_list, name='enrolled_students'),
    path('assignments/', views.assignment_list_view, name='assignment_list'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('feedback/', views.feedback_list, name='feedback_list'),





]

