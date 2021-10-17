from django.shortcuts import render
from django.views.generic import View
from validate_email import validate_email
from django.contrib import messages

# Create your views here.
class RegistrationView(View):
	def get(self, request):
		return render(request, 'auth/register.html')

	def post(self, request):
		data = request.POST
		email = request.POST.get('email')
		password = request.POST.get('password')
		password2 = request.POST.get('password2')

		if not validate_email(email):
			messages.add_message(request, messages.ERROR, 'Please Enter A Valid Email!')

		if not validate_email(email):
			messages.add_message(request, messages.ERROR, 'Passwords MUST contain at least 6 characters!')

		return render(request, 'auth/register.html', context={'data': data})