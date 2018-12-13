from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .models import Classroom, Student
from .forms import ClassroomForm, StudentForm, Signup, Signin
from django.http import Http404

def classroom_list(request):
	classrooms = Classroom.objects.all()
	context = {
		"classrooms": classrooms,
	}
	return render(request, 'classroom_list.html', context)

def student_list(request):
	students = Student.objects.all()
	context = {
		"students": students,
	}
	return render(request, 'classroom_detail.html', context)


def classroom_detail(request, classroom_id):
	classroom = Classroom.objects.get(id=classroom_id)
	students = Student.objects.filter(classroom=classroom).order_by('name', 'exam_grade')
	context = {
		"classroom": classroom,
		"students": students,
	}
	return render(request, 'classroom_detail.html', context)


def classroom_create(request):
	if request.user.is_anonymous:
		return redirect('signin')
	form = ClassroomForm()
	if request.method == "POST":
		form = ClassroomForm(request.POST, request.FILES or None)
		if form.is_valid():
			classroom= form.save(commit=False)
			classroom.teacher=request.user
			classroom.save()
			messages.success(request, "Successfully Created!")
			return redirect('classroom-list')
		print (form.errors)
	context = {
	"form": form,
	}
	return render(request, 'create_classroom.html', context)


def classroom_update(request, classroom_id):
	classroom = Classroom.objects.get(id=classroom_id)
	form = ClassroomForm(instance=classroom)
	if request.method == "POST":
		form = ClassroomForm(request.POST, request.FILES or None, instance=classroom)
		if form.is_valid():
			form.save()
			messages.success(request, "Successfully Edited!")
			return redirect('classroom-list')
		print (form.errors)
	context = {
	"form": form,
	"classroom": classroom,
	}
	return render(request, 'update_classroom.html', context)


def classroom_delete(request, classroom_id):
	Classroom.objects.get(id=classroom_id).delete()
	messages.success(request, "Successfully Deleted!")
	return redirect('classroom-list')

def new_student(request, classroom_id):
	form= StudentForm
	classroom= Classroom.objects.get(id=classroom_id)
	if not (request.user== classroom.teacher):
		raise Http404
	if request.method == "POST":
		form = StudentForm(request.POST)
		if form.is_valid():
			student= form.save(commit=False)
			student.classroom= classroom
			student.save()
			return redirect('classroom-detail', classroom_id)
	context = {
		"form":form,
		"classroom": classroom,
	}
	return render (request, 'new_student.html', context)

def student_delete(request,classroom_id, student_id):
	classroom= Classroom.objects.get(id=classroom_id)
	if request.user == classroom.teacher:
		Student.objects.get(id=student_id).delete()
	# classroom = Classroom.objects.get(id=classroom_id)
	# Student.objects.filter(classroom=classroom).delete()
		messages.success(request, "Successfully Deleted!")
		return redirect(classroom.get_absolute_url())

def student_update(request, classroom_id, student_id):
	student = Student.objects.get(id=student_id)
	classroom= Classroom.objects.get(id=classroom_id)
	if request.user == classroom.teacher:
		form = StudentForm(instance=student)
		if request.method == "POST":
			form = StudentForm(request.POST, instance=student)
			if form.is_valid():
				form.save()
				messages.success(request, "Successfully Edited!")
				return redirect(classroom.get_absolute_url())
			print (form.errors)
	context = {
	"form": form,
	"student": student,
	"classroom": classroom
	}
	return render(request, 'update_student.html', context)

def signup(request):
	form = Signup()
	if request.method == 'POST':
		form = Signup(request.POST)
		if form.is_valid():
			user = form.save(commit=False)

			user.set_password(user.password)
			user.save()

			login(request, user)
			# Where you want to go after a successful signup
			return redirect("classroom-list")
	context = {
		"form":form,
	}
	return render(request, 'signup.html', context)

def signin(request):
	form = Signin()
	if request.method == 'POST':
		form = Signin(request.POST)
		if form.is_valid():

			username = form.cleaned_data['username']
			password = form.cleaned_data['password']

			auth_user = authenticate(username=username, password=password)
			if auth_user is not None:
				login(request, auth_user)
				# Where you want to go after a successful login
				return redirect('classroom-list')

	context = {
		"form":form
	}
	return render(request, 'signin.html', context)

def signout(request):
	logout(request)
	# Where you would like to redirect the user after successfully logging out
	return redirect("signin")



