from pathlib import Path
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from .forms import StudentAvatarForm, StudentFilterForm
from .models import Student


def home(request):
    return render(request, 'main_practic/home.html')


def role_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.is_teacher:
        return redirect('main_practic:teacher-page')
    if request.user.is_student:
        return redirect('main_practic:student-page')
    return redirect('main_practic:no-profile')


@login_required
def student_page(request):
    if not getattr(request.user, "is_student", False):
        return HttpResponseForbidden('Доступ только для студентов')
    return render(request, 'main_practic/student.html')


@login_required
def teacher_page(request):
    if not getattr(request.user, "is_teacher", False):
        return HttpResponseForbidden('Доступ только для преподавателей')
    return render(request, 'main_practic/teacher.html')


@login_required
def no_profile_page(request):
    if request.user.is_student or request.user.is_teacher:
        return redirect('role-redirect')
    return render(request, 'main_practic/no_profile.html')


def upload_raw(request):
    if request.method == "POST" and request.FILES.get("file_upload"):
        f = request.FILES["file_upload"]
        dest = Path(settings.MEDIA_ROOT) / "raw" / f.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb+") as out:
            for chunk in f.chunks():
                out.write(chunk)
        return HttpResponse(f"Загружено: {dest}")
    return render(request, "main_practic/upload_raw.html")        


@login_required
def student_avatar_update(request):
    u = request.user
    if not (u.is_authenticated and getattr(u, "is_student", False)):
        return render(request, "main_practic/no_access.html", status=403) 

    student = u.student_profile
    if request.method == "POST":
        form = StudentAvatarForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Аватар обновлён")
            return redirect("main_practic:student-page")          
    else:
        form = StudentAvatarForm(instance=student)
    return render(request, "main_practic/avatar_form.html", {"form": form}) 


# список студентов с GET-фильтрами

def student_list(request):
    form = StudentFilterForm(request.GET or None)
    students = Student.objects.select_related('user', 'group').all()

    if form.is_valid():
        cd = form.cleaned_data

        if cd.get('surname'):
            students = students.filter(user__last_name__icontains=cd['surname'])

        if cd.get('group'):
            students = students.filter(group=cd['group'])

        if cd.get('group_name'):
            students = students.filter(group__name__icontains=cd['group_name'])

    return render(request, 'main_practic/student_list.html', {
        'form': form,
        'students': students,
    })