from django.core.mail import EmailMessage
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone

from datetime import date, timedelta

from typing import Any

from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404

from django.urls import path
from django.urls import reverse

from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.http import Http404

from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group, AnonymousUser
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control 

import mimetypes

from django.core.paginator import Paginator

from django.db.models import Q 
from django.db.models import Value as V
from django.db.models.functions import Concat

from .models import PostgraduateStudent, Teacher, StudyGroup, Reviewers, Dissertation, Department, Publication, Authors, PublicationTypes, Edition, Specialty, EditionSpecialties, Seminar, SeminarSubscription, EducIndPlan, ResearchIndPlan, DissertationState, Deadline, DeadlineSubmission,NotificationAdmin,Notifications,NotificationStudent, BlackList, Email, Protocol,Order, Report, RegistrationStatus

from .forms import StudentRegisterForm, TeacherForm, CustomAuthenticationForm, StudyGroupForm, DissertationForm, PublicationForm, StudentEditForm, SpecialtyForm, EditionForm, ResearchPlanForm, OrderForm, ReportForm
from .forms import EditionSpecialtiesForm, PublicationTypesForm, DepartmentForm, SeminarForm, SeminarSubscriptionForm, EducIndPlanForm, DeadlineForm, StudentBLForm, EmailForm, AdminForm, ProtocolForm, AuthorForm

def is_moderator(user):
    return user.groups.filter(name='moderators').exists()

def home(request):
	reg = RegistrationStatus.objects.first()
	return render(request, 'home.html', {'reg': reg})

# --------------------
# РЕЄСТРАЦІЯ
# -------------------- 
def register(request):
	if RegistrationStatus.objects.first().is_locked:
		return redirect('phdc_app:home')
	if request.method == "POST":
		form = StudentRegisterForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			password = form.cleaned_data['password']
			if PostgraduateStudent.objects.filter(email=email).exists():
				messages.error(request, "Е-пошта вже існує. Будь-ласка, введіть іншу е-пошту.")
				return render(request, "register.html", {'form': form})
			user = User.objects.create(
				username=email,
				password=make_password(password)
			)
			user_group = Group.objects.get(name='phdstudents')
			user.groups.add(user_group)
			form.save()
			messages.success(request, "Успішна реєстрація!")
			return HttpResponseRedirect('/') 
		else:
			return render(request, "register.html", {'form':form})
	else:
		form = StudentRegisterForm()
		return render(request, 'register.html', {'form':form})

# --------------------
# АВТОРИЗАЦІЯ
# -------------------- 
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login_page(request):
	if request.user.is_authenticated:
		if request.user.groups.all()[0].name == "phdstudents":
			user_email = request.user.username
			student_profile = PostgraduateStudent.objects.get(email = user_email)
			student_id = student_profile.pk
			context = {'student_profile':student_profile}
			return redirect(reverse('phdc_app:student_profile', kwargs={'id': student_id}))
		elif request.user.groups.all()[0].name == "moderators":
			
			return HttpResponseRedirect('/home_admin')
	if request.method == 'POST':
		form = CustomAuthenticationForm(request, request.POST)
		if form.is_valid():
			username = request.POST.get('username')
			password = request.POST.get('password')
			user= authenticate(request, username=username, password=password)
			if user is not None:
				login(request, user)
				if not request.user.groups.exists():
					return HttpResponseRedirect('/home_admin')
				if request.user.groups.all()[0].name == "phdstudents":
					user_email = request.user.username
					student_profile = PostgraduateStudent.objects.get(email = user_email)
					student_id = student_profile.pk
					student_profile_url = reverse('phdc_app:student_profile', kwargs={'id': student_id})
					context = {'student_profile':student_profile}
					return redirect(student_profile_url)
				elif request.user.groups.all()[0].name == "moderators":
					Black_list_handler.add_students_to_bl_auto()
					return HttpResponseRedirect('/home_admin')
				else:
					Black_list_handler.add_students_to_bl_auto()
					return HttpResponseRedirect('/home_admin')
			else:
				messages.info(request, 'Недійсні е-пошта або пароль!')
				return render(request, 'login_page.html')
		return render(request, 'login_page.html', {'form':form})
	else:
		form = CustomAuthenticationForm()
		error_message = None
		return render(request, 'login_page.html', {'form':form, 'error_message': error_message})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_user(request):
	logout(request)
	request.user = AnonymousUser()
	return redirect('phdc_app:home')	

# --------------------
# ПАНЕЛЬ КЕРУВАННЯ
# -------------------- 
@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home_admin(request):
	group = request.user.groups.all()[0].name
	reg_status = RegistrationStatus.objects.first()
	return render(request, 'home_admin.html', {'group':group, 'reg_status':reg_status}) 

# --------------------
# ВИКЛАДАЧІ
# -------------------
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def teachers(request):
    group = request.user.groups.all()[0].name
    return render(request, 'teachers.html', {'group': group})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def teacher_list(request):
    teachers_list = Teacher.objects.all().order_by('-lastname')
    academic_status = request.GET.get('academic_status', '')
    if academic_status:
        teachers_list = teachers_list.filter(academic_status=academic_status)

    query = request.GET.get('teachers_q', '')
    if query:
        teachers_list = teachers_list.filter(
            Q(firstname__icontains=query) |
            Q(lastname__icontains=query) |
            Q(middlename__icontains=query)
        ).order_by('-lastname')

    group = request.user.groups.all()[0].name
    return render(request, 'teacher_list.html', {
        'teachers': teachers_list,
        'group': group,
        'selected_academic_status': academic_status
    })



@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_teacher(request):
	if request.method == "POST":
		form = TeacherForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponse(status=204, headers={'HX-Trigger': 'teacherUpdate'})
		else:
			return render(request, 'teacher_add_modal.html', {'form': form})
	else:
		form = TeacherForm()
	return render(request, 'teacher_add_modal.html', {'form': form})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_teacher(request, id):
	teacher = get_object_or_404(Teacher, pk = id)
	if request.method == "POST":
		form = TeacherForm(request.POST, instance=teacher)
		if form.is_valid():
			form.save()
			return HttpResponse(status=204, headers={'HX-Trigger': 'teacherUpdate'})
		else:
			return render(request, 'teacher_add_modal.html', {'form': form})
	else:
		form = TeacherForm(instance=teacher)
	return render(request, 'teacher_edit_modal.html', {'form': form, 'teacher': teacher})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_teacher(request, id):
	teacher = Teacher.objects.get(pk = id)
	if request.method == "POST":
		teacher = Teacher.objects.get(pk=id)
		teacher.delete()
		return HttpResponse(status=204, headers={'HX-Trigger': 'teacherUpdate'})
	else:
		return  render(request, 'teacher_delete_modal.html', {'teacher': teacher, 'id': id})
	
# --------------------
# ГРУПИ
# -------------------
@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def study_groups(request):
    study_groups = StudyGroup.objects.all()
    departments = Department.objects.all()
    selected_sttype = request.GET.get('sttype', '')
    selected_sgcourse = request.GET.get('sgcourse', '')
    selected_department_id = request.GET.get('department_id', '')

    if selected_sttype:
        study_groups = study_groups.filter(study_type=selected_sttype)
    if selected_sgcourse:
        study_groups = study_groups.filter(course=selected_sgcourse)
    if selected_department_id:
        study_groups = study_groups.filter(department_id=selected_department_id)

    context = {
        'study_groups': study_groups,
        'departments': departments,
        'selected_sttype': selected_sttype,
        'selected_sgcourse': selected_sgcourse,
        'selected_department_id': selected_department_id,
    }

    return render(request, 'study_groups.html', context)

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def study_group_list(request):
    query = request.GET.get('study_groups_q', '')
    selected_sttype = request.GET.get('sttype', '')
    selected_sgcourse = request.GET.get('sgcourse', '')
    selected_department_id = request.GET.get('department_id', '')

    study_groups = StudyGroup.objects.all()

    if query:
        study_groups = study_groups.filter(name__icontains=query)
    if selected_sttype:
        study_groups = study_groups.filter(study_type=selected_sttype)
    if selected_sgcourse:
        study_groups = study_groups.filter(course=selected_sgcourse)
    if selected_department_id:
        study_groups = study_groups.filter(department_id=selected_department_id)

    return render(request, 'study_group_list.html', {'study_groups': study_groups})



@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def study_group(request, id):
	group = request.user.groups.first().name
	study_group = StudyGroup.objects.get(pk = id)
	students = study_group.students.all()

	context = {
		'study_group': study_group,
		'students': students,
		'group':group
	}
	return render(request, 'study_group.html', context) 

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_study_group(request):
	if request.method == "POST":
		form = StudyGroupForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponse(status=204, headers={'HX-Trigger': 'study_groupUpdate'})
		else:
			return render(request, 'study_group_add_modal.html', {'form': form})
	else:
		form = StudyGroupForm()
	return render(request, 'study_group_add_modal.html', {'form': form})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_study_group(request, id):
	study_group = get_object_or_404(StudyGroup, pk = id)
	if request.method == "POST":
		form = StudyGroupForm(request.POST, instance=study_group)
		if form.is_valid():
			form.save()
			students = PostgraduateStudent.objects.filter(study_group_id=id)
			for student in students:
				Is_graduating_status_checker.Is_graduating_status_check(student.id)
			return HttpResponse(status=204, headers={'HX-Trigger': 'study_groupUpdate'})
		else:
			return render(request, 'study_group_add_modal.html', {'form': form})
	else:
		form = StudyGroupForm(instance=study_group)
	return render(request, 'study_group_edit_modal.html', {'form': form, 'study_group': study_group})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_study_group(request, id):
	study_group = StudyGroup.objects.get(pk = id)
	if request.method == "POST":
		study_group = StudyGroup.objects.get(pk=id)
		study_group.delete()
		return HttpResponse(status=204, headers={'HX-Trigger': 'study_groupUpdate'})
	else:
		return  render(request, 'study_group_delete_modal.html', {'study_group': study_group, 'id': id})

# --------------------
# АСПІРАНТИ
# -------------------
@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def students(request):
    students_list = PostgraduateStudent.objects.all().order_by('-lastname')

    status = request.GET.get('status')
    is_graduate = request.GET.get('is_graduate')
    is_defended = request.GET.get('is_defended')
    is_approved = request.GET.get('is_approved')
    study_group_id = request.GET.get('study_group_id')
    specialty_id = request.GET.get('specialty_id')

    if status:
        students_list = students_list.filter(status=status)
    if is_graduate:
        students_list = students_list.filter(is_graduate=is_graduate)
    if is_defended:
        students_list = students_list.filter(is_defended=is_defended)
    if is_approved:
        students_list = students_list.filter(is_approved=is_approved)
    if study_group_id:
        students_list = students_list.filter(study_group_id=study_group_id)
    if specialty_id:
        students_list = students_list.filter(specialty_id=specialty_id)

    if 'students_q' in request.GET:
        students_q = request.GET['students_q']
        students_list = students_list.annotate(
            search_fullname=Concat('lastname', V(' '), 'firstname', V(' '), 'middlename')
        ).filter(
            Q(search_fullname__icontains=students_q) | 
            Q(lastname__icontains=students_q) | 
            Q(firstname__icontains=students_q) | 
            Q(middlename__icontains=students_q)
        ).order_by('-lastname')

    students_paginator = Paginator(students_list, 5)
    page = request.GET.get('page')
    students = students_paginator.get_page(page)

    study_groups = StudyGroup.objects.all()
    specialties = Specialty.objects.all()

    context = {
        'students': students,
        'status': status,
        'is_graduate': is_graduate,
        'is_defended': is_defended,
        'is_approved': is_approved,
        'study_groups': study_groups,
        'specialties': specialties,
        'selected_study_group_id': study_group_id,
        'selected_specialty_id': specialty_id
    }
    return render(request, 'students.html', context)

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def student_profile_nav(request):
	email=request.user.username
	student=PostgraduateStudent.objects.get(email=email)
	url = reverse('phdc_app:student_profile', kwargs={'id': student.id})
	return redirect(url)

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_student(request, id):
	if request.user.groups.name !='phdstudents':
		student=PostgraduateStudent.objects.get(pk=id)
		if request.method == 'POST':
			
			user = User.objects.get(username = student.email)
			student.delete()
			user.delete()
			url = reverse('phdc_app:students')
			return redirect(url)	
		else:
			return render(request, 'student_delete_modal.html', {'student':student})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def student_profile(request, id):
	student_profile = PostgraduateStudent.objects.get(pk = id) 
	dissertation = Dissertation.objects.filter(student_id = id).first()
	authors = Authors.objects.filter(student_id=id)
	publicatin_ids = [author.publication_id for author in authors]
	publications = Publication.objects.filter(name__in=publicatin_ids)
	student_publications = publications.filter(is_suitable='Зарахована')[:3]
	group = request.user.groups.all()[0].name

	context = {
		'group':group,
		'student_profile': student_profile,
		'dissertation': dissertation,
		'student_publications': student_publications
	}
	return render(request, 'student_profile.html', context) 

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_student_to_bl(request, id):
	student = get_object_or_404(PostgraduateStudent, pk=id)
	if request.method == "POST":
		form = StudentBLForm(request.POST)
		if form.is_valid():
			bl_entry = form.save(commit=False)
			bl_entry.student_id = student
			bl_entry.date = timezone.now()
			bl_entry.save()
			Notification_service.notify_student("Вас було занесено до списку перевірки", student )
			return HttpResponse(status=204, headers={'HX-Trigger': 'BLUpdate'})
		else:
			return render(request, 'add_student_to_bl_modal.html', {'form': form , 'id':id})
	else:
		form = StudentBLForm()
		return render(request, 'add_student_to_bl_modal.html', {'form': form , 'id':id})

def edit_student(request, id):
	group = request.user.groups.first().name
	student_old = PostgraduateStudent.objects.get(pk = id)
	original_email = student_old.email
	if request.method == "POST":
		form = StudentEditForm(request.POST, instance=student_old)
		if form.is_valid():
			student = form.save()
			user = User.objects.get(username=original_email)
			if student.email!=original_email:
				user.username = student.email
				user.save()
			if user.password!=form.cleaned_data.get('password'):
				password = form.cleaned_data.get('password')
				user.set_password(password)
				user.save()
				update_session_auth_hash(request, user)
			Is_defended_status_checker.check_postgraduateStudent_condition(id)
			Is_graduating_status_checker.Is_graduating_status_check(id)
			if request.user.groups.first().name == 'phdstudents':
				Notification_service.notify_admin("Аспірант "+ student.fullname() + " відредагував профіль", request)
			return redirect('phdc_app:student_profile', id=id)
		else:
			return render(request, "student_edit.html", {'form':form, 'group':group})
	else:
		form = StudentEditForm(instance=student_old)
		return render(request, 'student_edit.html', {'form':form, 'id':id, 'group':group})

# --------------------
# ПЛАН НАУКОВОЇ РОБОТИ
# ------------------- 
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def research_plans(request, id):
    student = get_object_or_404(PostgraduateStudent, pk=id)
    group = request.user.groups.all()[0].name
    rpyear = request.GET.get('rpyear', '')
    rpsemester = request.GET.get('rpsemester', '')
    rplocation = request.GET.get('rplocation', '')
    context = {
        'id': id,
        'group': group,
        'student': student,
        'selected_rpyear': rpyear,
        'selected_rpsemester': rpsemester,
        'selected_rplocation': rplocation
    }
    return render(request, 'research_plans.html', context)


@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def research_plan_list(request, id):
    student = get_object_or_404(PostgraduateStudent, pk=id)
    research_plans = ResearchIndPlan.objects.filter(student_id = id)
    rpyear = request.GET.get('rpyear', '')
    rpsemester = request.GET.get('rpsemester', '')
    rplocation = request.GET.get('rplocation', '')
    if rpyear:
        research_plans = research_plans.filter(year = rpyear)
    if rpsemester:
        research_plans = research_plans.filter(semester = rpsemester)
    if rplocation:
        research_plans = research_plans.filter(location = rplocation)
    
    return render(request, 'research_plan_list.html', {'research_plans': research_plans, 'id': id})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_research_plan(request, id):
	student = get_object_or_404(PostgraduateStudent, pk=id)
	if request.method == "POST":
		form = ResearchPlanForm(request.POST)
		if form.is_valid():
			research_plan = form.save(commit=False)
			research_plan.student_id = student
			research_plan.save()
			if request.user.groups.first().name == 'phdstudents':
				Notification_service.notify_admin("Аспірант "+ student.fullname() + " додав індивідуальний план наукової роботи", request)
			return HttpResponse(status=204, headers={'HX-Trigger': 'researchPlanUpdate'})
		else:
			return render(request, 'research_plan_add_modal.html', {'form': form})
	else:
		form = ResearchPlanForm()
		return render(request, 'research_plan_add_modal.html', {'form': form})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_research_plan(request, id):
	research_plan = ResearchIndPlan.objects.get(pk = id)
	student_id = research_plan.student_id
	student = PostgraduateStudent.objects.get(pk=student_id.id)
	if request.method == "POST":
		form = ResearchPlanForm(request.POST, instance=research_plan)
		if form.is_valid():
			research_plan = form.save(commit=False)
			research_plan.student_id = student_id
			research_plan.save()
			if request.user.groups.first().name == 'phdstudents':
				Notification_service.notify_admin("Аспірант "+ student.fullname() + " відредагував індивідуальний план наукової роботи", request)
			return HttpResponse(status=204, headers={'HX-Trigger': 'researchPlanUpdate'})
		else:
			return render(request, 'research_plan_edit_modal.html', {'form': form})
	else:
		form = ResearchPlanForm(instance=research_plan)
		return render(request, 'research_plan_edit_modal.html', {'form': form})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_research_plan(request, id):
	research_plan = ResearchIndPlan.objects.get(pk = id)
	student_id = research_plan.student_id
	student = PostgraduateStudent.objects.get(pk=student_id.id)
	if request.method == "POST":
		research_plan = ResearchIndPlan.objects.get(pk=id)
		research_plan.delete()
		if request.user.groups.first().name == 'phdstudents':
				Notification_service.notify_admin("Аспірант "+ student.fullname() + " видалив індивідуальний план наукової роботи", request)
		return HttpResponse(status=204, headers={'HX-Trigger': 'researchPlanUpdate'})
	else:
		return  render(request, 'research_plan_delete_modal.html', {'research_plan': research_plan, 'id': id})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def show_research_plan(request, id):
	research_plan = ResearchIndPlan.objects.get(pk = id)
	return  render(request, 'research_plan_info_modal.html', {'research_plan': research_plan, 'id': id})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def impl_research_plan(request, id):
	research_plan = ResearchIndPlan.objects.get(pk = id)
	return  render(request, 'research_plan_impl_modal.html', {'research_plan': research_plan, 'id': id})

# --------------------
# НАВЧАЛЬНИЙ ПЛАН
# ------------------- 
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def educ_plans(request, id):
    student = get_object_or_404(PostgraduateStudent, pk=id)
    group = request.user.groups.all()[0].name
    educyear = request.GET.get('educyear', '')
    educsemester = request.GET.get('educsemester', '')
    eductype = request.GET.get('eductype', '')
    educlocation = request.GET.get('educlocation', '')
    context = {
        'id': id,
        'group': group,
        'student': student,
        'selected_educyear': educyear,
        'selected_educsemester': educsemester,
        'selected_eductype': eductype,
        'selected_educlocation': educlocation
    }
    return render(request, 'educ_plans.html', context)


@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def educ_plan_list(request, id):
    student = get_object_or_404(PostgraduateStudent, pk=id)
    educ_plans = EducIndPlan.objects.filter(student_id = id)
    educyear = request.GET.get('educyear', '')
    educsemester = request.GET.get('educsemester', '')
    eductype = request.GET.get('eductype', '')
    educlocation = request.GET.get('educlocation', '')
    if educyear:
        educ_plans = educ_plans.filter(year = educyear)
    if educsemester:
        educ_plans = educ_plans.filter(semester = educsemester)
    if eductype:
        educ_plans = educ_plans.filter(dis_type = eductype)
    if educlocation:
        educ_plans = educ_plans.filter(location = educlocation)
		
    return render(request, 'educ_plan_list.html', {'educ_plans': educ_plans, 'id': id})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def educ_plan_list(request, id):
    student = get_object_or_404(PostgraduateStudent, pk=id)
    query = request.GET.get('educ_plans_q', '')

    filters = {
        'year': request.GET.get('educyear'),
        'semester': request.GET.get('educsemester'),
        'dis_type': request.GET.get('eductype'),
        'attestation_form': request.GET.get('educatform'),
        'location': request.GET.get('educlocation'),
    }
    filters = {k: v for k, v in filters.items() if v}

    if query or filters:
        educ_plans = student.educ_plans.filter(
            Q(discipline__icontains=query),
            **filters
        )
    else:
        educ_plans = student.educ_plans.all()

    educ_plans_paginator = Paginator(educ_plans, 8)
    page = request.GET.get('page')
    educ_plans = educ_plans_paginator.get_page(page)

    context = {
        'student': student,
        'educ_plans': educ_plans,
        'selected_educyear': request.GET.get('educyear'),
        'selected_educsemester': request.GET.get('educsemester'),
        'selected_eductype': request.GET.get('eductype'),
        'selected_educatform': request.GET.get('educatform'),
        'selected_educlocation': request.GET.get('educlocation'),
    }
    return render(request, 'educ_plan_list.html', context)



@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_educ_plan(request, id):
	student = PostgraduateStudent.objects.get(pk=id)
	if request.method == "POST":
		form = EducIndPlanForm(request.POST)
		if form.is_valid():
			educ_ind_plan = form.save(commit=False)
			educ_ind_plan.student_id = student
			educ_ind_plan.save()
			if request.user.groups.first().name == 'phdstudents':
				Notification_service.notify_admin("Аспірант "+ student.fullname() + " додав індивідуальний навчальний план", request)
			return HttpResponse(status=204, headers={'HX-Trigger': 'educPlanUpdate'})
		else:
			form = EducIndPlanForm()
			return render(request, 'educ_plan_add_modal.html', {'form': form})
	else:
		form = EducIndPlanForm()
		return render(request, 'educ_plan_add_modal.html', {'form': form})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_educ_plan(request, id, student_id):
	educ_plan = EducIndPlan.objects.get(pk = id)
	student = PostgraduateStudent.objects.get(pk=student_id)
	if request.method == "POST":
		form = EducIndPlanForm(request.POST, instance=educ_plan)
		if form.is_valid():
			educ_ind_plan = form.save(commit=False)
			educ_ind_plan.student_id = student
			educ_ind_plan.save()
			if request.user.groups.first().name == 'phdstudents':
				Notification_service.notify_admin("Аспірант "+ student.fullname() + " відредагував індивідуальний навчальний план", request)
			return HttpResponse(status=204, headers={'HX-Trigger': 'educPlanUpdate'})
		else:
			return render(request, 'educ_plan_edit_modal.html', {'form': form})
	else:
		form = EducIndPlanForm(instance=educ_plan)
		return render(request, 'educ_plan_edit_modal.html', {'form': form})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_educ_plan(request, id):
	educ_plan = EducIndPlan.objects.get(pk = id)
	student_id=educ_plan.student_id
	student = PostgraduateStudent.objects.get(pk=student_id.id)
	if request.method == "POST":
		educ_plan = EducIndPlan.objects.get(pk = id)
		educ_plan.delete()
		if request.user.groups.first().name == 'phdstudents':
				Notification_service.notify_admin("Аспірант "+ student.fullname() + " видалив індивідуальний навчальний план", request)
		return HttpResponse(status=204, headers={'HX-Trigger': 'educPlanUpdate'})
	else:
		return  render(request, 'educ_plan_delete_modal.html', {'educ_plan': educ_plan, 'id': id})

# --------------------
# ДИСЕРТАЦІЯ
# ------------------- 
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dissertation(request, id):
	student = PostgraduateStudent.objects.get(pk=id)
	group = request.user.groups.all()[0].name
	dissertation = Dissertation.objects.get(student_id=id)
	dissertation_id = dissertation.id
	reviewers_list = Reviewers.objects.filter(dissertation_id=dissertation.id)
	reviewer_1 = []
	reviewer_2 = []
	counter = 0

	for reviewer in reviewers_list:
		if counter == 0:
			reviewer_1.append(reviewer)
		else:
			reviewer_2.append(reviewer)
		counter += 1

	context = {
        'student': student,
		'group':group,
        'dissertation': dissertation,
        'dissertation_id': dissertation_id,
        'reviewer_1': reviewer_1,
        'reviewer_2': reviewer_2
    }
	return render(request, 'dissertation.html', context)

def add_dissertation(request, id):
    if request.method == "POST":
        form = DissertationForm(request.POST, request.FILES)  
        if form.is_valid():
            form_data = form.save(commit=False)
            student = get_object_or_404(PostgraduateStudent, pk=id)
            form_data.student_id = student
            form_data.save()
            if request.user.groups.first().name == 'phdstudents':
                Notification_service.notify_admin("Аспірант "+ student.fullname() + " додав дисертацію в систему", request)

            dissertation = Dissertation.objects.get(student_id=id)
            reviewer_1 = Reviewers(reviewer_id=form.cleaned_data.get('reviewer_1'), dissertation_id=dissertation)
            reviewer_1.save()
            reviewer_2 = Reviewers(reviewer_id=form.cleaned_data.get('reviewer_2'), dissertation_id=dissertation)
            reviewer_2.save()

            return redirect('phdc_app:dissertation', id=id)
        else:
            return render(request, "dissertation_add.html", {'form': form})
    else:
        form = DissertationForm()
        return render(request, 'dissertation_add.html', {'form': form, 'id': id})

def edit_dissertation(request, id, state):
    group = request.user.groups.first().name
    dissertation = Dissertation.objects.get(pk=id)
    student = dissertation.student_id
    original_state = state
    if request.method == "POST":
        form = DissertationForm(request.POST, request.FILES, instance=dissertation)  
        if form.is_valid():
            dissertationnew = form.save(commit=False)
            dissertation = form.save()
            Responsible_check_handler.cancel_check(dissertation)
            Is_defended_status_checker.check_dissertation_condition(cls=Is_defended_status_checker, dissertation_id=id)
            if request.user.groups.first().name=='phdstudents':
                Notification_service.notify_admin("Аспірант "+ student.fullname()+" змінив дисертацію", request)
            print(dissertationnew.state)
            print('and')
            print(original_state)
            if dissertationnew.state != original_state:
                print('works')
                Dissertation_state_history_handler.remember_state(id)

            student = dissertation.student_id
            reviewers = Reviewers.objects.filter(dissertation_id=dissertation)

            for reviewer in reviewers:
                reviewer.delete()

            reviewer_1 = Reviewers(reviewer_id=form.cleaned_data.get('reviewer_1'), dissertation_id=dissertation)
            reviewer_2 = Reviewers(reviewer_id=form.cleaned_data.get('reviewer_2'), dissertation_id=dissertation)
            reviewer_1.save()
            reviewer_2.save()

            return redirect('phdc_app:dissertation', id=student.id)
        else:
            return render(request, "dissertation_edit.html", {'form': form, 'group':group})
    else:
        reviewers = Reviewers.objects.filter(dissertation_id=dissertation)
        form = DissertationForm(instance=dissertation)
        reviewer_count = reviewers.count()
        if reviewer_count >= 1:
            form = DissertationForm(instance=dissertation, initial={'reviewer_1': reviewers[0].reviewer_id})
        if reviewer_count == 2:
            form.fields['reviewer_2'].initial = reviewers[1].reviewer_id
        return render(request, 'dissertation_edit.html', {'form': form, 'id': id, 'group':group})
	
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_dissertation(request, id):
    dissertation = get_object_or_404(Dissertation, pk=id)
    student_id = dissertation.student_id.id
    if request.method == "POST":
        dissertation.delete()
        response = HttpResponse()
        response['HX-Redirect'] = reverse('phdc_app:student_profile', args=[student_id])
        return response
    return render(request, 'dissertation_delete_modal.html', {'dissertation': dissertation, 'id': id})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def states(request, id):
	group = request.user.groups.first().name
	dissertation = get_object_or_404(Dissertation, pk = id)
	states = dissertation.states.all()

	context = {
		'states': states,
		'dissertation': dissertation,
		'group':group
	}
	return render(request, 'states.html', context)

def download_file(request, id):
    dissertation = get_object_or_404(Dissertation, id=id)
    
    if not dissertation.file:
        raise Http404
    
    file_path = dissertation.file.path
    file_name = dissertation.file.name.split('/')[-1]
    mime_type, _ = mimetypes.guess_type(file_path)
    
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type=mime_type or "application/octet-stream")
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# --------------------
# ПРОТОКОЛИ
# ------------------- 
@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def protocols(request, id):
    group = request.user.groups.first().name
    student = get_object_or_404(PostgraduateStudent, pk=id)
    departments = Department.objects.all()
    department_id = request.GET.get('department_id', '')
    
    return render(request, 'protocols.html', {
        'id': id,
        'student': student,
        'group': group,
        'departments': departments,
        'department_id': department_id
    })

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def protocol_list(request, id):
    student = get_object_or_404(PostgraduateStudent, pk=id)
    query = request.GET.get('protocols_q', '')
    department_id = request.GET.get('department_id') 
    protocols = student.protocols.all()
    if query:
        protocols = protocols.filter(Q(number__icontains=query))

    if department_id:
        protocols = protocols.filter(department_id=department_id)

    protocols_paginator = Paginator(protocols, 5)
    page = request.GET.get('page')
    protocols = protocols_paginator.get_page(page)
    departments = Department.objects.all()
    context = {
        'student': student,
        'protocols': protocols,
        'departments': departments,
        'selected_department_id': department_id
    }
    return render(request, 'protocol_list.html', context)

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_protocol(request, id):
	student = PostgraduateStudent.objects.get(pk=id)
	if request.method == "POST":
		form = ProtocolForm(request.POST)
		if form.is_valid():
			protocol = form.save(commit=False)
			protocol.student_id = student
			protocol.save()
			return HttpResponse(status=204, headers={'HX-Trigger': 'protocolUpdated'})
		else:
			form = ProtocolForm()
			return render(request, 'protocol_add_modal.html', {'form': form})
	else:
		form = ProtocolForm()
		return render(request, 'protocol_add_modal.html', {'form': form})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_protocol(request, id, student_id):
	protocol = Protocol.objects.get(pk = id)
	student = PostgraduateStudent.objects.get(pk=student_id)
	if request.method == "POST":
		form = ProtocolForm(request.POST, instance=protocol)
		if form.is_valid():
			protocol = form.save(commit=False)
			protocol.student_id = student
			protocol.save()
			return HttpResponse(status=204, headers={'HX-Trigger': 'protocolUpdated'})
		else:
			return render(request, 'protocol_edit_modal.html', {'form': form})
	else:
		form = ProtocolForm(instance=protocol)
		return render(request, 'protocol_edit_modal.html', {'form': form})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_protocol(request, id):
	protocol = Protocol.objects.get(pk = id)
	if request.method == "POST":
		protocol = Protocol.objects.get(pk = id)
		protocol.delete()
		return HttpResponse(status=204, headers={'HX-Trigger': 'protocolUpdated'})
	else:
		return  render(request, 'protocol_delete_modal.html', {'protocol': protocol, 'id': id})
	
# --------------------
# ВИДАННЯ
# ------------------- 
@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def editions(request):
	return render(request, 'editions.html', {'editions':editions})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edition_list(request):
    query = request.GET.get('editions_q', '')
    if query:
        editions = Edition.objects.filter(
            Q(name__icontains=query) 
        ).order_by('-name')
    else:
        editions = Edition.objects.all().order_by('-name')
    
    editions_paginator = Paginator(editions, 5)
    page = request.GET.get('page')
    editions = editions_paginator.get_page(page)
    
    return render(request, 'edition_list.html', {'editions': editions})


@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_edition(request):
	if request.method == "POST":
		form = EditionForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponse(status=204, headers={'HX-Trigger': 'editionUpdate'})
		else:
			return render(request, 'edition_add_modal.html', {'form': form})
	else:
		form = EditionForm()
	return render(request, 'edition_add_modal.html', {'form': form})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_edition(request, id):
	edition = get_object_or_404(Edition, pk = id)
	if request.method == "POST":
		form = EditionForm(request.POST, instance=edition)
		if form.is_valid():
			form.save()
			return HttpResponse(status=204, headers={'HX-Trigger': 'editionUpdate'})
		else:
			return render(request, 'edition_edit_modal.html', {'form': form, 'edition': edition})
	else:
		form = EditionForm(instance=edition)
	return render(request, 'edition_edit_modal.html', {'form': form, 'edition': edition})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_edition(request, id):
	edition = Edition.objects.get(pk = id)
	if request.method == "POST":
		edition = Edition.objects.get(pk=id)
		edition.delete()
		return HttpResponse(status=204, headers={'HX-Trigger': 'editionUpdate'})
	else:
		return  render(request, 'edition_delete_modal.html', {'edition': edition, 'id': id})
	
# --------------------
# СПЕЦІАЛЬНОСТІ ВИДАННЯ
# ------------------- 
@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edition_specs(request, id):
	edition = get_object_or_404(Edition, pk = id)
	return render(request, 'edition_specs.html', {'id':id, 'edition':edition})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edition_spec_list(request, id):
    edition = get_object_or_404(Edition, pk=id)
    edition_specs = EditionSpecialties.objects.filter(edition_id=id)
    specs_ids = edition_specs.values_list('specialty_id', flat=True)
    specialties = Specialty.objects.filter(id__in=specs_ids)
    specialties_paginator = Paginator(specialties, 5)
    page = request.GET.get('page')
    specialties = specialties_paginator.get_page(page)
    
    departments = Department.objects.all()
    
    context = {
        'edition_id': id,
        'specialties': specialties,
    }
    
    return render(request, 'edition_spec_list.html', context)


@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_edition_spec(request, id):
	edition = get_object_or_404(Edition, pk = id)
	if request.method == "POST":
		form = EditionSpecialtiesForm(request.POST, edition=edition)
		if form.is_valid():
			form.save()
			return HttpResponse(status=204, headers={'HX-Trigger': 'editionSpecUpdate'})
		else:
			return render(request, 'edition_spec_add_modal.html', {'form': form})
	else:
		form = EditionSpecialtiesForm(edition=edition)
	return render(request, 'edition_spec_add_modal.html', {'form': form})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_edition_spec(request, id, edition_id):
	specialty = Specialty.objects.get(pk = id)
	edition = Edition.objects.get(pk = edition_id)
	edition_spec = EditionSpecialties.objects.get(edition_id = edition_id, specialty_id = id)
	if request.method == "POST":
		specialty = Specialty.objects.get(pk = id)
		edition = Edition.objects.get(pk = edition_id)
		edition_spec = EditionSpecialties.objects.get(edition_id = edition_id, specialty_id = id)
		edition_spec.delete()
		return HttpResponse(status=204, headers={'HX-Trigger': 'editionSpecUpdate'})
	else:
		return  render(request, 'edition_spec_delete_modal.html', {'edition_spec': edition_spec, 'id': id, 'edition_id': edition_id})

# --------------------
# СПЕЦІАЛЬНОСТІ 
# -------------------  
@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def specialties(request):
	return render(request, 'specialties.html', {'specialties':specialties})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def specialty_list(request):
    query = request.GET.get('specialties_q', '')
    if query:
        specialties = Specialty.objects.filter(
            Q(name__icontains=query) 
        ).order_by('-name')
    else:
        specialties = Specialty.objects.all().order_by('-name')
    
    specialties_paginator = Paginator(specialties, 5)
    page = request.GET.get('page')
    specialties = specialties_paginator.get_page(page)

    return render(request, 'specialty_list.html', {'specialties': specialties})


@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_specialty(request):
	if request.method == "POST":
		form = SpecialtyForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponse(status=204, headers={'HX-Trigger': 'specialtyUpdate'})
		else:
			return render(request, 'specialty_add_modal.html', {'form': form})
	else:
		form = SpecialtyForm()
	return render(request, 'specialty_add_modal.html', {'form': form})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_specialty(request, id):
	specialty = get_object_or_404(Specialty, pk = id)
	if request.method == "POST":
		form = SpecialtyForm(request.POST, instance=specialty)
		if form.is_valid():
			form.save()
			return HttpResponse(status=204, headers={'HX-Trigger': 'specialtyUpdate'})
		else:
			return render(request, 'specialty_edit_modal.html', {'form': form, 'specialty': specialty})
	else:
		form = SpecialtyForm(instance=specialty)
	return render(request, 'specialty_edit_modal.html', {'form': form, 'specialty': specialty})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_specialty(request, id):
	specialty = Specialty.objects.get(pk = id)
	if request.method == "POST":
		specialty = Specialty.objects.get(pk=id)
		specialty.delete()
		return HttpResponse(status=204, headers={'HX-Trigger': 'specialtyUpdate'})
	else:
		return  render(request, 'specialty_delete_modal.html', {'specialty': specialty, 'id': id})

# --------------------
# ТИПИ ПУБЛІКАЦІЙ 
# -------------------
@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def pub_types(request):
	return render(request, 'pub_types.html', {'pub_types':pub_types})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def pub_type_list(request):
    query = request.GET.get('pub_types_q', '')
    if query:
        pub_types = PublicationTypes.objects.filter(
            Q(name__icontains=query) 
        ).order_by('-name')
    else:
        pub_types = PublicationTypes.objects.all().order_by('-name')
    
    specialties_paginator = Paginator(specialties, 5)
    page = request.GET.get('page')
    specialties = specialties_paginator.get_page(page)
    
    return render(request, 'pub_type_list.html', {'pub_types': pub_types})


@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_pub_type(request):
	if request.method == "POST":
		form = PublicationTypesForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponse(status=204, headers={'HX-Trigger': 'pubTypeUpdate'})
		else:
			return render(request, 'pub_type_add_modal.html', {'form': form})
	else:
		form = PublicationTypesForm()
		return render(request, 'pub_type_add_modal.html', {'form': form})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_pub_type(request, id):
	pub_type = PublicationTypes.objects.get(pk = id)
	if request.method == "POST":
		pub_type = PublicationTypes.objects.get(pk=id)
		pub_type.delete()
		return HttpResponse(status=204, headers={'HX-Trigger': 'pubTypeUpdate'})
	else:
		return  render(request, 'pub_type_delete_modal.html', {'pub_type': pub_type, 'id': id})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def research_plans(request, id):
    student = get_object_or_404(PostgraduateStudent, pk=id)
    research_plans = ResearchIndPlan.objects.filter(student_id=id)
    return render(request, 'research_plans.html', {'student': student, 'research_plans': research_plans, 'id': id})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def research_plan_list(request, id):
    student = get_object_or_404(PostgraduateStudent, pk=id)
    research_plans = ResearchIndPlan.objects.filter(student_id=id)
    rpyear = request.GET.get('rpyear', '')
    rpsemester = request.GET.get('rpsemester', '')
    rplocation = request.GET.get('rplocation', '')
    
    if rpyear:
        research_plans = research_plans.filter(year=rpyear)
    if rpsemester:
        research_plans = research_plans.filter(semester=rpsemester)
    if rplocation:
        research_plans = research_plans.filter(location=rplocation)
    
    return render(request, 'research_plan_list.html', {
        'research_plans': research_plans,
        'id': id,
        'selected_rpyear': rpyear,
        'selected_rpsemester': rpsemester,
        'selected_rplocation': rplocation
    })

# --------------------
# ПУБЛІКАЦІЇ 
# -------------------
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def publications(request, id):
    student = get_object_or_404(PostgraduateStudent, pk=id)
    group = request.user.groups.all()[0].name
    types = PublicationTypes.objects.all()
    pbappr = request.GET.get('pbappr', '')
    pbcoef = request.GET.get('pbcoef', '')
    context = {
        'id': id,
        'group': group,
        'student': student,
        'selected_pbappr': pbappr,
        'selected_pbcoef': pbcoef,
        'types': types
    }
    return render(request, 'publications.html', context)


@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def publication_list(request, id):
    authors = Authors.objects.filter(student_id=id)
    publications = Publication.objects.filter(pubauth__in=authors)
    query = request.GET.get('publications_q', '')
    pbappr = request.GET.get('pbappr', '')
    pbcoef = request.GET.get('pbcoef', '')
    if pbappr:
        publications = publications.filter(is_suitable=pbappr)
    if pbcoef:
        publications = publications.filter(Q(coef=pbcoef) | Q(coef__exact='0' if pbcoef == '0.0' else ''))
    if query:
        publications = publications.filter(
            Q(name__icontains=query) 

        )
    publications_paginator = Paginator(publications, 5)
    page = request.GET.get('page')
    publications = publications_paginator.get_page(page)
    return render(request, 'publication_list.html', {'publications': publications, 'student_id': id})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_publication(request, student_id):
    group = request.user.groups.first().name
    if request.method == "POST":
        form = PublicationForm(request.POST)
        if form.is_valid():
            publication = form.save(commit=False)
            student = PostgraduateStudent.objects.get(pk=student_id)
            author = Authors(publication_id=publication, student_id=student)
            publication.save()
            author.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'publicationUpdate'})
        else:
            return render(request, 'publication_add_modal.html', {'form': form, 'group':group})
    else:
        form = PublicationForm()
        return render(request, 'publication_add_modal.html', {'form': form, 'group':group})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_publication(request, publication_id):
    if request.method == "POST":
        publication = Publication.objects.get(pk=publication_id)
        publication.delete()
        return HttpResponse(status=204, headers={'HX-Trigger': 'publicationUpdate'})
    else:
        return render(request, 'publication_delete_modal.html', {'publication_id': publication_id})

# --------------------
# ПУБЛІКАЦІЯ
# -------------------
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def publication(request, id):
	group = request.user.groups.first().name
	publication = Publication.objects.get(pk = id)
	return render(request, 'publication.html', {'publication': publication, 'group':group}) 
 
def edit_publication(request, id):
	group = request.user.groups.first().name
	if request.method == "POST":
		publication = Publication.objects.get(pk = id)
		form = PublicationForm(request.POST, instance=publication)
		if form.is_valid():
			form.save()
			Is_defended_status_checker.check_publication_condition(Is_defended_status_checker, id)
			return redirect('phdc_app:publication', id=id)
		else:
			return render(request, "publication_edit.html", {'form':form})
	else:
		publication = Publication.objects.get(pk = id)
		form = PublicationForm(instance=publication)
		return render(request, 'publication_edit.html', {'form':form, 'id':id, 'group' :group})
	
# --------------------
# АВТОРИ ПУБЛІКАЦІЇ
# -------------------
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def authors(request, id):
	group = request.user.groups.first().name
	publication = get_object_or_404(Publication, pk = id)

	return render(request, 'authors.html', {'publication':publication, 'group':group})

from django.db.models import Q

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def author_list(request, id):
    publication = get_object_or_404(Publication, pk=id)
    query = request.GET.get('authors_q', '')
    authors = Authors.objects.filter(publication_id=id).select_related('student_id', 'teacher_id')
    if query:
        authors = authors.filter(
            Q(student_id__firstname__icontains=query) | 
            Q(student_id__middlename__icontains=query) | 
            Q(student_id__lastname__icontains=query) |
            Q(teacher_id__firstname__icontains=query) | 
            Q(teacher_id__middlename__icontains=query) | 
            Q(teacher_id__lastname__icontains=query)
        )
    authors_paginator = Paginator(authors, 5)
    page = request.GET.get('page')
    authors = authors_paginator.get_page(page)
    context = {
        'publication': publication,
        'authors': authors,
    }
    return render(request, 'author_list.html', context)


@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_authors(request, id):
    publication = get_object_or_404(Publication, pk=id)
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            auth = form.save(commit=False)
            auth.publication_id = publication  
            auth.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'authorsUpdate'})
        else:
            return render(request, 'author_add_modal.html', {'form': form})
    else:
        form = AuthorForm()
        return render(request, 'author_add_modal.html', {'form': form})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_author(request, id):
    author = get_object_or_404(Authors, pk=id)
    if request.method == "POST":
        author.delete()
        return HttpResponse(status=204, headers={'HX-Trigger': 'authorsUpdate'})
    else:
        return render(request, 'author_delete_modal.html', {'id':id})

# --------------------
# КАФЕДРИ
# ------------------- 
@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def departments(request):
	return render(request, 'departments.html', {'departments': departments})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def department_list(request):
    query = request.GET.get('departments_q', '')
    if query:
        departments = Department.objects.filter(
            Q(name__icontains=query) 
        ).order_by('-name')
    else:
        departments = Department.objects.all().order_by('-name')
    
    departments_paginator = Paginator(departments, 5)
    page = request.GET.get('page')
    departments = departments_paginator.get_page(page)  
    return render(request, 'department_list.html', {'departments': departments})


@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_department(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'departmentUpdate'})
        else:
            return render(request, 'department_add_modal.html', {'form': form})
    else:
        form = DepartmentForm()
        return render(request, 'department_add_modal.html', {'form': form})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_department(request, id):
	department = Department.objects.get(pk = id)
	if request.method == "POST":
		department = Department.objects.get(pk=id)
		department.delete()
		return HttpResponse(status=204, headers={'HX-Trigger': 'departmentUpdate'})
	else:
		return  render(request, 'department_delete_modal.html', {'department': department, 'id': id})

# --------------------
# ДЕДЛАЙНИ
# -------------------
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deadlines(request):
	deadlines = Deadline.objects.all
	group = request.user.groups.all()[0].name
	currdate = date.today()
	if group =='phdstudents':
		student = PostgraduateStudent.objects.get(email=request.user.username)
		deadlines = Deadline.objects.filter(Q(group_id=student.study_group_id) | Q(student_id=student))
	return render(request, 'deadlines.html', {'deadlines':deadlines, 'group':group, 'currdate':currdate})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deadline_list(request):
    query = request.GET.get('deadlines_q', '')
    if query:
        deadlines = Deadline.objects.filter(
            Q(name__icontains=query) 
        ).order_by('-name')
    else:
        deadlines = Deadline.objects.all().order_by('-name')
        if request.user.groups.all()[0].name == 'phdstudents':
            email = request.user.username
            student = PostgraduateStudent.objects.get(email=email)
            deadlines = Deadline.objects.filter(group_id=student.study_group_id)

    deadlines_paginator = Paginator(deadlines, 5)
    page = request.GET.get('page')
    deadlines = deadlines_paginator.get_page(page)
    group = request.user.groups.all()[0].name
    return render(request, 'deadline_list.html', {'deadlines': deadlines, 'group': group})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_deadline(request):
    if request.method == "POST":
        form = DeadlineForm(request.POST)
        if form.is_valid():
            deadline = form.save()
            if deadline.group_id is not None:
                Notification_service.notify_student_group('Вам призначено нове завдання: ' + deadline.description ,deadline.group_id.id )
            return redirect('phdc_app:deadlines')
        else:
            return render(request, 'deadline_add.html', {'form': form})
    else:
        form = DeadlineForm()
        return render(request, 'deadline_add.html', {'form': form})


@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_deadline(request, id):
    deadline = Deadline.objects.get(pk=id)
    if request.method == "POST":
        form = DeadlineForm(request.POST, instance=deadline)
        if form.is_valid():
            form.save()
            return HttpResponse(status=204)
        else:
            return render(request, 'deadline_edit_modal.html', {'form': form , 'id':id})
    else:
        form = DeadlineForm(instance=deadline)
        return render(request, 'deadline_edit_modal.html', {'form': form , 'id':id})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_deadline(request, id):
    deadline = Deadline.objects.get(pk=id)
    if request.method == "POST":
        deadline.delete()
        return HttpResponse(status=204)
    else:
        return render(request, 'deadline_delete_modal.html', {'deadline': deadline, 'id': id})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def show_deadline_info(request, id):
	deadline = Deadline.objects.get(pk=id)
	return render(request, 'show_deadline_info_modal.html', {'deadline': deadline, 'id': id})

# --------------------
# ВИКОНАННЯ ДЕДЛАЙНУ
# -------------------
@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deadline_submissions(request, id):
    return render(request, 'deadline_submissions.html', {'id':id})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deadline_submission_list(request, id):
    deadline_submissions = DeadlineSubmission.objects.filter(deadline_id=id)
    students = [subscriber.student_id for subscriber in deadline_submissions]
    
    deadline_submissions_paginator = Paginator(deadline_submissions, 5)
    page = request.GET.get('page')
    deadline_submissions = deadline_submissions_paginator.get_page(page)
    return render(request, 'deadline_submission_list.html', {'deadline_submissions': deadline_submissions, 'id': id})


@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_deadline_submission(request, id):
    if request.user.groups.all()[0].name == 'phdstudents':
        email = request.user.username
        student = PostgraduateStudent.objects.get(email=email)
        deadline = Deadline.objects.get(pk=id)
        existingds = DeadlineSubmission.objects.filter(student_id=student, deadline_id=deadline).exists()
        if existingds:
            info = 'Ви вже виконали цей дедлайн!'
            return render(request, 'add_deadline_submission_modal.html', {'info':info})
        deadlinesubmission = DeadlineSubmission(student_id=student, deadline_id=deadline, date=timezone.now, is_approved='Очікується перевірка')
        deadlinesubmission.save()
        Notification_service.notify_admin('Аспірант ' + student.fullname() + '\n' + 'подав на перевірку виконання завдання ' + '"' + deadline.description + '"', request)
        info = 'Ви успішно виконали дедлайн!'
        return render(request, 'add_deadline_submission_modal.html', {'info':info})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_deadline_submission(request, id):
    if request.user.groups.all()[0].name == 'phdstudents':
        deadline=Deadline.objects.get(id=id)
        student = PostgraduateStudent.objects.get(email = request.user.username)
        existingds = DeadlineSubmission.objects.filter(student_id=student, deadline_id=deadline)
        if existingds.exists():
            info = 'Ви скасували виконання дедлайну!'
            existingds.delete()
            Notification_service.notify_admin('Аспірант ' + student.lastname + ' видалив виконання завдання ' + deadline.description, request)
            return render(request, 'delete_deadline_submission_modal.html', {'info':info})
        info = 'Ви ще не виконали цей дедлайн!'
        return render(request, 'delete_deadline_submission_modal.html', {'info':info})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def approve_submission(request, id, deadline_id):
	deadline = Deadline.objects.get(pk=deadline_id)
	deadline_submission = DeadlineSubmission.objects.get(pk=id)
	if request.method == "POST":
		deadline_submission.is_approved = 'Затверджено'
		deadline_submission.save()
		Notification_service.notify_student('Ваше виконання завдання :' + deadline.description + ' було зараховане', deadline_submission.student_id.id )
		return HttpResponse(status=204, headers={'HX-Trigger': 'deadlineSubmissionUpdate'})
	else:
		return render(request, 'approve_submission_modal.html', {'deadline_id': deadline_id, 'id': id})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def decline_submission(request, id, deadline_id):
    deadline = Deadline.objects.get(pk=deadline_id)
    deadline_submission = DeadlineSubmission.objects.get(pk=id)
    if request.method == "POST":
        deadline_submission.is_approved = 'Не затверджено'
        deadline_submission.save()
        Notification_service.notify_student( 'Ваше виконання завдання :' + deadline.description + ' було відхилене', deadline_submission.student_id.id)
        return HttpResponse(status=204, headers={'HX-Trigger': 'deadlineSubmissionUpdate'})
    else:
        return render(request, 'decline_submission_modal.html', {'deadline_id': deadline_id, 'id': id})

# --------------------
# СПИСОК ПЕРЕВІРКИ
# -------------------
@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def blacklists(request):
	return render(request, 'blacklists.html', {'blacklists':blacklists})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def blacklists_cats(request, category):
	return render(request, 'blacklists_cats.html', {'category':category})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def blacklist_list(request, category):
    query = request.GET.get('black_q', '')
    
    if query:
        blacklists = blacklists.filter(
            Q(student_id__firstname__icontains=query)|
			Q(student_id__middlename__icontains=query)|
			Q(student_id__lastname__icontains=query)
        )
    blacklists = BlackList.objects.filter(category = category)
    blacklists_paginator = Paginator(blacklists, 5)
    page = request.GET.get('page')
    blacklists = blacklists_paginator.get_page(page)
    group = request.user.groups.all()[0].name
    return render(request, 'blacklist_list.html', {'blacklists': blacklists})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def show_bl_entry_info(request, id):
	blacklist = BlackList.objects.get(pk = id)
	return render(request, 'show_bl_entry_info_modal.html', {'blacklist': blacklist, 'id': id})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_bl_entry(request, id):
	blacklist = BlackList.objects.get(pk = id)
	if request.method == "POST":
		blacklist = BlackList.objects.get(pk=id)
		blacklist.delete()
		return HttpResponse(status=204, headers={'HX-Trigger': 'blacklistUpdate'})
	else:
		return  render(request, 'blacklist_delete_modal.html', {'blacklist': blacklist, 'id': id})

# --------------------
# СПОВІЩЕННЯ
# -------------------
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def notifications(request):
	return render(request, 'notifications.html', {'notifications':notifications})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def show_notifications(request):
    if request.method == 'POST':
        nots = NotificationAdmin.objects.all()
        for n in nots:
            n.is_read = 'Так'
            n.delete()
        return HttpResponse(status=204)

    notifications = NotificationAdmin.objects.all()
    return render(request, 'show_notifications_modal.html', {'notifications': notifications})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def show_student_notifications(request):
    email = request.user.username
    student = PostgraduateStudent.objects.get(email=email) 
    if request.method == 'POST':
        NotificationStudent.objects.filter(student_id=student).delete()
        return HttpResponse(status=204)

    notification_students = NotificationStudent.objects.filter(student_id=student)
    notifications = [ns.notification_id for ns in notification_students]
    return render(request, 'show_student_notifications_modal.html', {'notifications': notifications})

# --------------------
# АДМІН
# -------------------
@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_settings(request):
    email = request.user.username
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            user = request.user
            email = form.cleaned_data['email']
            if User.objects.filter(username__iexact=email).exists():
                form.add_error('email', 'Е-пошта ' + email + ' вже існує! Будь-ласка, введіть іншу е-пошту.')
      
            else:
                password = form.cleaned_data.get('password')
                user.set_password(password)
                user.username = form.cleaned_data['email']
                user.save()
                update_session_auth_hash(request, user)
 
            return HttpResponse(status=204)
        else:
            form = AdminForm(initial={'email': email})
            return render(request, 'admin_settings_modal.html', {'form': form})
    else:
        form = AdminForm(initial={'email': email})
        return render(request, 'admin_settings_modal.html', {'form': form})
	

def registration_status_toggle(request):
	if request.user.groups.first().name != 'phdstudents':
		status = RegistrationStatus.objects.first()
		if status.is_locked :
			status.is_locked = False
			status.save()
			info ='Ви відкрили реєстрацію'
		elif not status.is_locked:
			status.is_locked = True
			status.save()
			info ='Ви закрили реєстрацію'
		return render(request, 'registration_status_info.html', {'info':info})


# ---------------
# СЕМІНАРИ
# -------------------
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def seminars(request):
    group = request.user.groups.all()[0].name
    departments = Department.objects.all()
    selected_department_id = request.GET.get('department_id', '')

    seminars = Seminar.objects.all()

    if selected_department_id:
        seminars = seminars.filter(department_id=selected_department_id)

    context = {
        'seminars': seminars,
        'group': group,
        'departments': departments,
        'selected_department_id': selected_department_id,
    }

    return render(request, 'seminars.html', context)

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def seminar_list(request):
    query = request.GET.get('seminars_q', '')
    selected_department_id = request.GET.get('department_id', '')

    seminars = Seminar.objects.all()

    if query:
        seminars = seminars.filter(Q(name__icontains=query))
    if selected_department_id:
        seminars = seminars.filter(department_id=selected_department_id)

    seminars_paginator = Paginator(seminars, 8)
    page = request.GET.get('page')
    seminars = seminars_paginator.get_page(page)
    group = request.user.groups.all()[0].name
    return render(request, 'seminar_list.html', {'seminars': seminars, 'group': group})


@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_seminar(request):
	if request.method == "POST":
		form = SeminarForm(request.POST)
		if form.is_valid():
			seminar = form.save()
			study_groups=StudyGroup.objects.all()
			for group in study_groups:
				Notification_service.notify_student_group('Додано новий семінар :'+seminar.name, group.id)
			return HttpResponse(status=204, headers={'HX-Trigger': 'seminarUpdate'})
		else:
			return render(request, 'seminar_add_modal.html', {'form': form})
	else:
		form = SeminarForm()
		return render(request, 'seminar_add_modal.html', {'form': form})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_seminar(request, id):
	seminar = get_object_or_404(Seminar, pk = id)
	if request.method == "POST":
		form = SeminarForm(request.POST, instance=seminar)
		if form.is_valid():
			form.save()
			return HttpResponse(status=204, headers={'HX-Trigger': 'seminarUpdate'})
		else:
			return render(request, 'seminar_edit_modal.html', {'form': form, 'seminar': seminar, 'id':id})
	else:
		form = SeminarForm(instance=seminar)
		return render(request, 'seminar_edit_modal.html', {'form': form, 'seminar': seminar, 'id':id})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_seminar(request, id):
	seminar = Seminar.objects.get(pk = id)
	if request.method == "POST":
		seminar = Seminar.objects.get(pk=id)
		seminar.delete()
		return HttpResponse(status=204, headers={'HX-Trigger': 'seminarUpdate'})
	else:
		return  render(request, 'seminar_delete_modal.html', {'seminar': seminar, 'id': id})

# --------------------
# РЕЄСТРАЦІЯ НА СЕМІНАР
# -------------------
@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def seminar_subscribers(request, id):
	seminar = get_object_or_404(Seminar, pk = id)
	return render(request, 'seminar_subscribers.html', {'id':id, 'seminar':seminar})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def seminar_subscribers_list(request, id):
    seminar_subscribers = SeminarSubscription.objects.filter(seminar_id=id)
    students = [subscriber.student_id for subscriber in seminar_subscribers]
    
    students_paginator = Paginator(students, 5)
    page = request.GET.get('page')
    students = students_paginator.get_page(page)
    
    return render(request, 'seminar_subscribers_list.html', {'students': students, 'id': id})


@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_seminar_subscriber(request, id):
    if request.method == "POST":
        seminar = Seminar.objects.get(pk=id)
        form = SeminarSubscriptionForm(request.POST, seminar_id=seminar)
        if form.is_valid():
            form.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'seminar_subscriberUpdate'})
        else:
            return render(request, 'seminar_subscriber_add_modal.html', {'form': form})
    else:
        seminar = Seminar.objects.get(pk=id)
        form = SeminarSubscriptionForm(seminar_id=seminar)
        return render(request, 'seminar_subscriber_add_modal.html', {'form': form})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_seminar_subscriber(request, seminar_id, student_id):
    if request.method == "POST":
        seminar_subscriber = SeminarSubscription.objects.get(seminar_id=seminar_id, student_id=student_id)
        seminar_subscriber.delete()
        return HttpResponse(status=204, headers={'HX-Trigger': 'seminar_subscriberUpdate'})
    else:
        student = get_object_or_404(PostgraduateStudent, pk=student_id)
        return render(request, 'seminar_subscriber_delete_modal.html', {'student': student, 'seminar_id': seminar_id})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_seminar_sub(request, id):
    if request.user.groups.all()[0].name == 'phdstudents':
        email = request.user.username
        student = PostgraduateStudent.objects.get(email=email)
        seminar = Seminar.objects.get(pk=id)
        existingsub = SeminarSubscription.objects.filter(student_id=student, seminar_id=seminar).exists()
        if existingsub:
            info = 'Ви вже зареєстровані на цей семінар!'
            return render(request, 'seminar_subscriber_conf_modal.html', {'info':info})
        seminar_subscription = SeminarSubscription(student_id=student, seminar_id=seminar)
        seminar_subscription.save()
        Notification_service.notify_admin('Аспірант ' + student.lastname + ' зареєструвався на семінар ' + seminar.name, request)
        info = 'Ви зареєструвались на семінар!'
        return render(request, 'seminar_subscriber_conf_modal.html', {'info':info})
	
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_seminar_sub(request, id):
    if request.user.groups.all()[0].name == 'phdstudents':
        seminar=Seminar.objects.get(id=id)
        student = PostgraduateStudent.objects.get(email = request.user.username)
        existingsub = SeminarSubscription.objects.filter(student_id=student, seminar_id=seminar).exists()
        if existingsub:
            info = 'Ви скасували реєстрацію на семінар!'
            sub = SeminarSubscription.objects.get(student_id=student, seminar_id=seminar)
            sub.delete()
            Notification_service.notify_admin('Аспірант ' + student.lastname + 'скасував реєстрацію на семінар ' + seminar.name, request)
            return render(request, 'seminar_unsubscriber_conf_modal.html', {'info':info})
        
        info = 'Ви ще не зареєстровані на цей семінар!'
        return render(request, 'seminar_unsubscriber_conf_modal.html', {'info':info})

# -------------------
# ПОВІДОМЛЕННЯ
# -------------------
def send_email(request):
    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data["student_id"]
            student = student_id
            email = student.email
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]
            mail = EmailMessage(subject, message, "PHDCENTRE Адміністратор <ms6967476@gmail.com>", [email])
            mail.send()
            messages.success(request, "Листа надіслано")
            return HttpResponse(status=204)
    else:
        form = EmailForm()
    return render(request, 'send_email.html', {'form': form})

# --------------------
# НАКАЗИ
# -------------------
@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def orders(request, id):
    group = request.user.groups.first().name
    student = get_object_or_404(PostgraduateStudent, pk=id)
    return render(request, 'orders.html', {
        'id': id,
        'student': student,
        'group': group,
        'departments': departments,
    })

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_list(request, id):
    student = get_object_or_404(PostgraduateStudent, pk=id)

    orders = Order.objects.filter(student_id =id )
    orders_paginator = Paginator(orders, 5)
    page = request.GET.get('page')
    orders = orders_paginator.get_page(page)
    context = {
        'student': student,
        'orders': orders,

    }
    return render(request, 'order_list.html', context)

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_order(request, id):
	student = PostgraduateStudent.objects.get(pk=id)
	if request.method == "POST":
		form = OrderForm(request.POST)
		if form.is_valid():
			order = form.save(commit=False)
			order.student_id = student
			order.save()
			return HttpResponse(status=204, headers={'HX-Trigger': 'orderUpdated'})
		else:
			form = OrderForm()
			return render(request, 'order_add_modal.html', {'form': form})
	else:
		form = OrderForm()
		return render(request, 'order_add_modal.html', {'form': form})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_order(request, id, student_id):
	order = Order.objects.get(pk = id)
	student = PostgraduateStudent.objects.get(pk=student_id)
	if request.method == "POST":
		form = OrderForm(request.POST, instance=order)
		if form.is_valid():
			order = form.save(commit=False)
			order.student_id = student
			order.save()
			return HttpResponse(status=204, headers={'HX-Trigger': 'orderUpdated'})
		else:
			return render(request, 'order_edit_modal.html', {'form': form})
	else:
		form = OrderForm(instance=order)
		return render(request, 'order_edit_modal.html', {'form': form})

@user_passes_test(is_moderator)
@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_order(request, id):
	order = Order.objects.get(pk = id)
	if request.method == "POST":
		order = Order.objects.get(pk = id)
		order.delete()
		return HttpResponse(status=204, headers={'HX-Trigger': 'orderUpdated'})
	else:
		return  render(request, 'order_delete_modal.html', {'order': order, 'id': id})


# --------------------
# ЗВІТИ
# -------------------

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def reports(request, id):
    group = request.user.groups.first().name
    student = get_object_or_404(PostgraduateStudent, pk=id)
    return render(request, 'reports.html', {
        'id': id,
        'student': student,
        'group': group,
        'departments': departments,
    })

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def report_list(request, id):
    student = get_object_or_404(PostgraduateStudent, pk=id)

    reports = Report.objects.filter(student_id =id )
    reports_paginator = Paginator(reports, 5)
    page = request.GET.get('page')
    reports = reports_paginator.get_page(page)
    context = {
        'student': student,
        'reports': reports,

    }
    return render(request, 'report_list.html', context)

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_report(request, id):
	student = PostgraduateStudent.objects.get(pk=id)
	if request.method == "POST":
		form = ReportForm(request.POST, request.FILES)
		print('before v')
		if form.is_valid():
			print('after v')
			report = form.save(commit=False)
			report.student_id = student
			report.save()
			return HttpResponse(status=204, headers={'HX-Trigger': 'reportUpdated'})
		else:
			form = ReportForm()
			return render(request, 'report_add_modal.html', {'form': form})
	else:
		form = ReportForm()
		return render(request, 'report_add_modal.html', {'form': form})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_report(request, id, student_id):
	report = Report.objects.get(pk = id)
	student = PostgraduateStudent.objects.get(pk=student_id)
	if request.method == "POST":
		form = ReportForm(request.POST, instance=report)
		if form.is_valid():
			report = form.save(commit=False)
			report.student_id = student
			report.save()
			return HttpResponse(status=204, headers={'HX-Trigger': 'reportUpdated'})
		else:
			return render(request, 'report_edit_modal.html', {'form': form})
	else:
		form = ReportForm(instance=report)
		return render(request, 'report_edit_modal.html', {'form': form})

@login_required(login_url="phdc_app:login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_report(request, id):
	report = Report.objects.get(pk = id)
	if request.method == "POST":
		report = Report.objects.get(pk = id)
		report.delete()
		return HttpResponse(status=204, headers={'HX-Trigger': 'reportUpdated'})
	else:
		return  render(request, 'report_delete_modal.html', {'report': report, 'id': id})

def download_report(request, id):
    report = Report.objects.get(pk=id)
    
    if not report.file:
        print('nofile')
    
    file_path = report.file.path
    file_name = report.file.name.split('/')[-1]
    mime_type, _ = mimetypes.guess_type(file_path)
    
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type=mime_type or "application/octet-stream")
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

class Is_defended_status_checker:
    @staticmethod
    def check_publication_condition(cls, publication_id):
        publication = Publication.objects.get(id=publication_id)
        students_ids = publication.pubauth.all().values_list('student_id', flat=True)
        for id in students_ids:
            cls.check_postgraduateStudent_condition(id)

    @staticmethod
    def check_postgraduateStudent_condition(student_id):
        student = PostgraduateStudent.objects.get(id=student_id)
        authors = Authors.objects.filter(student_id=student_id)
        publication_ids = authors.values_list('publication_id', flat=True)
        related_publications = Publication.objects.filter(id__in=publication_ids)
        suitable_publications_count = related_publications.filter(is_suitable='Зараховано').count()
        
        dissertation_state = '0%'
        if student.dissertation.exists():
            dissertation_state = student.dissertation.first().state

        state = student.status
        is_graduate = student.is_graduate
        if suitable_publications_count >= 3 and state == 'Навчається' and is_graduate == 'Так' and dissertation_state == '100%':
            student.is_defended = 'Рекомендований(-а) до захисту'
            student.save()

    @staticmethod
    def check_dissertation_condition(cls, dissertation_id):
        dissertation = Dissertation.objects.get(id=dissertation_id)
        student_id = dissertation.student_id_id
        cls.check_postgraduateStudent_condition(student_id)

class Is_graduating_status_checker:
     @staticmethod
     def Is_graduating_status_check(student_id):
          student = PostgraduateStudent.objects.get(id=student_id)
          if student.status =='Навчається' and student.study_group_id.course == '4':
               student.is_graduate = 'Так'
               student.save()
     
class Dissertation_state_history_handler:
    @staticmethod
    def remember_state(diss_id):
        print('yes')
        dissertation = Dissertation.objects.get(id=diss_id)
        state = DissertationState(new_state=dissertation.state, dissertation_id=dissertation, date = timezone.now())
        state.save()

class Responsible_check_handler:
    @staticmethod
    def approve_check(entity):
      entity.is_approved = 'Затверджено'
      entity.save()
    
    @staticmethod
    def disapprove_check(entity):
      entity.is_approved = 'Не затверджено'
      entity.save()

    @staticmethod
    def cancel_check(entity):
      entity.is_approved = 'Очікується перевірка'
      entity.save()

class Deadline_submission_handler:
   @staticmethod
   def submit(student_id, deadline_id):
      deadline_submission = DeadlineSubmission(student_id = student_id, deadline_id = deadline_id, date= timezone.now())
      deadline_submission.save()
  
class Black_list_handler:

  @staticmethod
  def add_students_to_bl_auto():
    print('start')
    active_deadlines = Deadline.objects.filter(is_active='Активний')
    print(active_deadlines)
    for deadline in active_deadlines:
      print('if')
      if timezone.now().date() > deadline.date:
        deadline.is_active = 'Не активний'
        deadline.save()
        print('saving')
        if deadline.group_id is not None:
          study_group = StudyGroup.objects.get(id=deadline.group_id.id)
          students = PostgraduateStudent.objects.filter(study_group_id = study_group.id)
          for student in students:
            related_submission = DeadlineSubmission.objects.filter(student_id=student.pk, deadline_id=deadline.pk).first()
            if related_submission is None or related_submission.is_approved == 'Не затверджено':
              description = f"Просрочено дедлайн : {deadline.description}"
              blacklist = BlackList(student_id =student, deadline_id=deadline, description=description, category='Дедлайни', date=timezone.now())
              blacklist.save()
              Notification_service.notify_student(description, student.pk)
              
        if deadline.student_id is not None:
          student = PostgraduateStudent.objects.get(pk=deadline.student_id.id)
          related_submission = DeadlineSubmission.objects.filter(student_id=student.pk, deadline_id=deadline.pk).first()
          if related_submission is None or related_submission.is_approved == 'Не затверджено':
            description = f"Просрочено дедлайн : {deadline.description}"
            blacklist = BlackList(student_id=student, deadline_id=deadline, description=description, category='Дедлайни', date=timezone.now())
            blacklist.save()
            Notification_service.notify_student(description, student.pk)    


  @staticmethod
  def add_student_to_bl_manual(student_id, cause):
    blacklist = BlackList(student_id=student_id, description=cause)
    blacklist.save()



class Notification_service:
    @staticmethod
    def notify_student(description, student_id):
        notification = Notifications(description=description, date=timezone.now())
        notification.save()
        student = PostgraduateStudent.objects.get(pk=student_id)
        email = Email.objects.filter(email=student.email).first()
        unread_notification = NotificationStudent(student_id=student, notification_id=notification, is_read=False)
        unread_notification.save()
        if email is None:
            email = Email(
                name=student.firstname,
                email=student.email,
                subject="Сповіщення",
                message="Вам надійшли нові сповіщення в PHD centre! Зайдіть, будь ласка, та перевірте",
                last_sent=None
            )
            email.save()
        now = timezone.now()
        if email.last_sent is None or (now - email.last_sent) > timedelta(days=1):
            email.subject = "Сповіщення"
            email.message = "Вам надійшли нові сповіщення в PHD centre! Зайдіть, будь ласка, та перевірте"
            mail = EmailMessage(
                email.subject,
                email.message,
                "PHDCENTRE Адміністратор <ms6967476@gmail.com>",
                [email.email]
            )
            mail.send()
            email.last_sent = now
            email.save()

    @staticmethod
    def notify_student_group(description, group_id):
        study_group = StudyGroup.objects.get(id=group_id)
        students = study_group.students.all()
        for student in students:
            Notification_service.notify_student(description, student.id)

    @staticmethod
    def notify_admin(description, request):
        notification = NotificationAdmin(description=description, date=timezone.now(), is_read=False)
        notification.save()
        email = request.user.username
        email_obj = Email.objects.filter(email=email).first()
        
        now = timezone.now()
        if not email_obj or email_obj.last_sent is None or (now - email_obj.last_sent) > timedelta(days=1):
            mail = EmailMessage(
                "Сповіщення",
                description,
                "PHDCENTRE Адміністратор <ms6967476@gmail.com>",
                [email]
            )
            mail.send()
            if email_obj:
                email_obj.last_sent = now
                email_obj.save()

    @staticmethod
    def mark_admin_notification_as_read(notification_id):
        notification = NotificationAdmin.objects.get(pk=notification_id)
        notification.is_read = True
        notification.save()

    @staticmethod
    def mark_all_admin_notification_as_read():
        unread_notifications = NotificationAdmin.objects.filter(is_read=False)
        for notification in unread_notifications:
            notification.is_read = True
            notification.save()

    @staticmethod
    def mark_student_notification_as_read(student_id, notification_id):
        notification = NotificationStudent.objects.get(student_id=student_id, notification_id=notification_id)
        notification.is_read = True
        notification.save()

    @staticmethod
    def mark_all_student_notification_as_read(student_id):
        notifications = NotificationStudent.objects.filter(student_id=student_id)
        for notification in notifications:
            notification.is_read = True
            notification.save()


