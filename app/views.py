from django.shortcuts import redirect, render
from django.views.generic import View
from validate_email import validate_email
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from .utils import generate_token
from django.contrib.auth.decorators import login_required
from .models import *

from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import authenticate, login, logout

import cloudinary
import cloudinary.uploader
import cloudinary.api

import threading

# Create your views here.
@login_required(login_url='login')
def index(request):
    images = Image.objects.all().order_by('-image_date')
    return render(request, 'home.html', {'images': images})

# profile page
@login_required(login_url='login')
def profile(request):
    current_user = request.user
    images = Image.objects.filter(user_id=current_user.id)
    profile = Profile.objects.filter(user_id=current_user.id).first()
    return render(request, 'profile.html', {"images": images, "profile": profile})

# save image  with image name,image caption and upload image to cloudinary
@login_required(login_url='login')
def save_image(request):
  if request.method == 'POST':
			image_name = request.POST['image_name']
			image_caption = request.POST['image_caption']
			image_file = request.FILES['image_file']
			image_file = cloudinary.uploader.upload(image_file)
			image_url = image_file['url']
			image_public_id = image_file['public_id']
			image = Image(image_name=image_name, image_caption=image_caption, image=image_url,
										profile_id=request.POST['user_id'], user_id=request.POST['user_id'])
			image.save_image()
			return redirect('/profile', {'success': 'Image Uploaded Successfully'})
  else:
      return render(request, 'profile.html', {'danger': 'Image Upload Failed'})

class EmailThread(threading.Thread):
	def __init__(self, email_message):
		self.email_message = email_message
		threading.Thread.__init__(self)

	def run(self):
		self.email_message.send()

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
		user.is_active = True

		user.save()

		current_site = get_current_site(request)
		email_subject = 'Activate Your Account'
		message = render_to_string('auth/activate.html',
		{
			'user': user,
			'domain': current_site.domain,
			'uid': urlsafe_base64_encode(force_bytes(user.pk)),
			'token': generate_token.make_token(user)
		})

		email_message = EmailMessage(
			email_subject,
			message,
			settings.EMAIL_HOST_USER,
			[email]
    )
		EmailThread(email_message).start()

		messages.add_message(request, messages.SUCCESS, 'Account Successfully Created !')

		return redirect('login')

class LoginView(View):
	def get(self, request):
		return render(request, 'auth/login.html')
	
	def get(self, request):
		context = {
			'data': request.POST,
			'has_error': False
		}
		username = request.POST.get('username')
		password = request.POST.get('password')
		if username == '':
			messages.add_message(request, messages.ERROR, 'Username is Required!')
			context['has_error'] = True
		if password == '':
			messages.add_message(request, messages.ERROR, 'Password is Required!')
			context['has_error'] = True

		user = authenticate(request, username = username, password = password)

		if not user and not context['has_error']:
			messages.add_message(request, messages.ERROR, 'Invalid login!')
			context['has_error'] = True
		if context ['has_error']:
			return render(request, 'auth/login.html', status = 401, context=context)
		login(request, user)
		return redirect('home')

class ActivateAccountView(View):
	def get(self, request, uidb64, token):
		try:
			uid = force_text(urlsafe_base64_decode(uidb64))
			user = User.objects.get(pk = uid)
		except Exception as identifier:
			user = None

		if user is not None and generate_token.check_token(user, token):
			user.is_active = True
			user.save()
			messages.add_message(request, messages.SUCCESS, 'Account Activated Successfully!')
			return redirect('login')

		return render(request, 'auth/activate_fail.html', status = 401)	

class HomeView(View):
	def get(self, request):
		return render(request, 'home.html')

@login_required(login_url='login')
def user_profile(request, id):
	if User.objects.filter(id=id).exists():
			user = User.objects.get(id=id)
			images = Image.objects.filter(user_id=id)
			profile = Profile.objects.filter(user_id=id).first()
			return render(request, 'user-profile.html', {'images': images, 'profile': profile, 'user': user})
	else:
			return redirect('/')

class LogoutView(View):
	def post(self, request):
		logout(request)
		messages.add_message(request, messages.SUCCESS, 'Logout Successfully!')

		return redirect('login')
