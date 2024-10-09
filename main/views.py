from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth import login as user_login, logout as user_logout, authenticate
from django.shortcuts import redirect
from main.models import Profile, Lesson, Mark, Date, Payment, History


# Create your views here.
def home(request):
    """View function for home page of site."""
    lessons = None
    user = None
    admin = False
    users = {}
    if request.user.is_authenticated:
        user = Profile.objects.get(user=request.user)
        admin = user.role == 'Admin'
        if request.method == 'POST':
            if request.POST.get('amount', None) is not None:
                profile = Profile.objects.get(pk=request.POST.get('id'))
                amount = int(request.POST.get('amount', None))
                Payment(student=profile, amount=amount).save()
                profile.balance += amount
                profile.save()
                History(text=f'Payment: {profile.id} {amount}').save()
            elif request.POST.get('option', None) is not None:
                option = request.POST.get('option')
                profile = Profile.objects.get(pk=request.POST.get('id'))
                lesson = Lesson.objects.get(pk=request.POST.get('lesson_id'))
                if option == 'Add':
                    lesson.students.add(profile)
                else:
                    lesson.students.remove(profile)
                lesson.save()
                History(text=f'Group: {option} {lesson.id} {profile.id}').save()
            elif request.POST.get('full_name', None) is not None:
                user = User.objects.create_user(username="username", password="Password.VERY7")
                user.username = user.id
                user.password = f'User.{user.id}'
                user.save()
                profile = Profile(user=user, full_name=request.POST.get('full_name'), phone_number=request.POST.get('phone_number'), role=request.POST.get('role')).save()
                History(text=f'User: {profile.id}').save()
            elif request.POST.get('price', None) is not None:
                teacher = Profile.objects.get(pk=request.POST.get('teacher'))
                lesson = Lesson(name=request.POST.get('name'), teacher=teacher, price=request.POST.get('price')).save()
                History(text=f'Lesson: {lesson.id} {teacher.id}').save()
        if admin:
            for user in Profile.objects.all():
                if user.balance <= 0:
                    users[user.id] = user
            lessons = Lesson.objects.all()
        else:
            lessons = Lesson.objects.filter(Q(students=user) | Q(teacher=user))
    return render(request, 'home.html', {'user': user, 'lessons': lessons, 'admin': admin, 'users': users})


def login(request):
    """View function for login page."""
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
    """View function for logout page."""
    if request.method == 'POST':
        user_logout(request)
        return redirect('home')


def table(request, id):
    """View function for table page."""
    lesson = Lesson.objects.get(pk=id)
    dates = lesson.dates.all().order_by('date')
    students = lesson.students.all()
    access = Profile.objects.get(user=request.user) == lesson.teacher
    if request.method == 'POST':
        if request.POST.get('mark', None) is None:
            date = Date.objects.create(date=request.POST['date'])
            lesson.dates.add(date)
            for student in students:
                student.balance -= lesson.price
                student.save()
                teacher = Profile.objects.get(pk=lesson.teacher.id)
                teacher.balance += lesson.price
                teacher.save()
                Mark.objects.create(lesson=lesson, student=student, date=date, mark=0)
            History(text=f'Lesson: {lesson.id} Payment').save()
        else:
            mark = Mark.objects.get(lesson=lesson, student=Profile.objects.get(full_name=request.POST['student']), date=request.POST['date'])
            mark.mark = request.POST['mark']
            mark.save()
    dct = {}
    for student in students:
        marks = Mark.objects.filter(lesson=lesson, student=student).order_by('date')
        dct[f'{student.pk}. {student.full_name}'] = marks
    return render(request, 'table.html', {'students': dct, 'dates': dates, 'access': access, 'id': id})
