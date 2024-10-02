from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Profile(models.Model):
    OPTION_CHOICES = [
        ('Teacher', 'Teacher'),
        ('Student', 'Student'),
        ('Admin', 'Admin'),
        ('Newbei', 'Newbei'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=70)
    phone_number = models.CharField(max_length=13)
    role = models.CharField(choices=OPTION_CHOICES, max_length=7)

    def __str__(self):
        return self.full_name

class Date(models.Model):
    date = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.date

class Lesson(models.Model):
    name = models.CharField(max_length=70)
    date = models.CharField(max_length=40)
    teacher = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='teacher')
    students = models.ManyToManyField(Profile, related_name='students')
    dates = models.ManyToManyField(Date, related_name='dates')

    def __str__(self):
        return self.name

class Mark(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    student = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.CharField(max_length=10)
    mark = models.IntegerField()

    class Meta:
        unique_together = ('lesson', 'student', 'date')

    def __str__(self):
        return self.student.full_name
