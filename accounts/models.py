from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone



class AuthAdminManager(BaseUserManager):
    def create_user(self, username, email, phone_number, password=None):
        if not email:
            raise ValueError("Users must have an email")
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            phone_number=phone_number,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, phone_number, password):
        user = self.create_user(
            username=username,
            email=email,
            phone_number=phone_number,
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class AuthAdmin(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = AuthAdminManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone_number']

    def __str__(self):
        return self.username


class Student(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class Course(models.Model):
    name = models.CharField(max_length=255)
    instructor = models.CharField(max_length=255)
    description = models.TextField()
    video_link = models.URLField()
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)

    def __str__(self):
        return self.name




class Enrolled(models.Model):
    student_name = models.CharField(max_length=100)
    course_name = models.CharField(max_length=100)
    enrolled_date = models.DateTimeField(auto_now_add=True)



class Assignment(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='assignments/')
    course = models.ForeignKey('Course', on_delete=models.CASCADE)



class Feedback(models.Model):
    user_name = models.CharField(max_length=100)
    rating = models.CharField(max_length=50)
    feedback_text = models.TextField()  
    submitted_at = models.DateTimeField()
    
    user_name = models.CharField(max_length=150)
    rating_choices = [
        ('Excellent', 'Excellent'),
        ('Very Good', 'Very Good'),
        ('Good', 'Good'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
    ]
    rating = models.CharField(max_length=20, choices=rating_choices)
    feedback_text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accounts_feedback'    # forces this table name in DB

    def __str__(self):
        return f"Feedback from {self.user_name} ({self.rating})"

