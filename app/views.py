from django.shortcuts import redirect, render
from django.views.generic import View
from validate_email import validate_email
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.conf import settings

# Create your views here.
class RegistrationView(View):
	def get(self, request):
		return render(request, 'auth/register.html')

	def post(self, request):
		context={
			'data': request.POST,
			'has_error': False
		}
		email = request.POST.get('email')
		username = request.POST.get('username')
		full_name = request.POST.get('name')
		password = request.POST.get('password')
		password2 = request.POST.get('password2')

		if not validate_email(email):
			messages.add_message(request, messages.ERROR, 'Please Enter A Valid Email!')
			context['has_error'] = True

		if not validate_email(email):
			messages.add_message(request, messages.ERROR, 'Passwords MUST contain at least 6 characters!')
			context['has_error'] = True

		if password != password2:
			messages.add_message(request, messages.ERROR, 'Passwords DO NOT Match !')
			context['has_error'] = True

		if User.objects.filter(email = email).exists():
			messages.add_message(request, messages.ERROR, 'Email Already Taken !')
			context['has_error'] = True

		if User.objects.filter(username = username).exists():
			messages.add_message(request, messages.ERROR, 'Username Already Taken !')
			context['has_error'] = True

		if context['has_error']:
		  return render(request, 'auth/register.html', context)

		user = User.objects.create_user(username = username, email = email)
		user.set_password(password)
		user.first_name = full_name
		user.last_name = full_name
		user.is_active = False

		user.save()

		current_site = get_current_site(request)
		email_subject = 'Activate Your Account',
		message = render_to_string('auth/activate.html',
		{
			'user': user,
			'domain': current_site.domain,
			'uid': urlsafe_base64_encode(force_bytes(user.pk)),
			'token': PasswordResetTokenGenerator.make_token(user)
		})

		email_message = EmailMessage(
			email_subject,
			message,
			settings.EMAIL_HOST_USER,
			[email],
    )
		email_message.send()

		messages.add_message(request, messages.SUCCESS, 'Account Successfully Created !')

		return redirect('login')

class LoginView(View):
	def get(self, request):
		return render(request, 'auth/login.html')
		
class ActivateAccountView(View):
	def get(self, request, uidb64, token):
		try:
			uid = force_text(urlsafe_base64_decode(uidb64))
			user = User.objects.get(pk = uid)
		except Exception as identifier:
			user = None

		if user is not None and PasswordResetTokenGenerator.check_token(user, token):
			user.is_active = True
			user.save()
			messages.add_message(request, messages.INFO, 'Account Activated Successfully!')
			return redirect('login')

		return render(request, 'auth/activate_fail.html', status = 401)	