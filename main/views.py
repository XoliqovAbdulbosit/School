from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth import login as user_login, logout as user_logout, authenticate
from django.shortcuts import redirect
from main.models import Profile, Lesson, Mark, Date


# Create your views here.
def home(request):
    user = None
    lessons = None
    if request.user.is_authenticated:
        user = Profile.objects.get(user=request.user)
        lessons = Lesson.objects.filter(Q(students = user)| Q(teacher = user))
    return render(request, 'home.html', {'user': user, 'lessons': lessons})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            user_login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'login.html')

def logout(request):
    if request.method == 'POST':
        user_logout(request)
        return redirect('home')

def table(request, id):
    lesson = Lesson.objects.get(pk=id)
    dates = lesson.dates.all().order_by('date')
    students = lesson.students.all()
    access = Profile.objects.get(user = request.user) == lesson.teacher
    if request.method == 'POST':
        if request.POST.get('mark', None) is None:
            date = Date.objects.create(date=request.POST['date'])
            lesson.dates.add(date)
            for student in students:
                Mark.objects.create(lesson=lesson, student=student, date=date, mark=0)
        else:
            mark = Mark.objects.get(lesson=lesson, student=Profile.objects.get(full_name=request.POST['student']), date=request.POST['date'])
            mark.mark = request.POST['mark']
            mark.save()
    dct = {}
    for student in students:
        marks = Mark.objects.filter(lesson=lesson, student=student).order_by('date')
        dct[student.full_name] = marks
    return render(request, 'table.html', {'students': dct, 'dates': dates, 'access': access, 'id': id})
