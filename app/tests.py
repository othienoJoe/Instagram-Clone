from django.test import TestCase
from django.urls import reverse

# Create your tests here.
class BaseTest(TestCase):
	def setUp(self):
		self.register_url=reverse('register')
		self.login_url=reverse('login')
		self.user={
			'email':'testemail@gmail.com',
			'username':'username',
			'password':'password',
			'password2':'password',
			'name':'fullname'
		}

		self.user_short_password={
			'email':'testemail@gmail.com',
			'username':'username',
			'password':'tes',
			'password2':'tes',
			'name':'fullname'
    }

class RegisterTest(BaseTest):
  def test_can_view_page_correctly(self):
			response=self.client.get(self.register_url)
			self.assertEqual(response.status_code,200)
			self.assertTemplateUsed(response,'auth/register.html')

  def test_can_register_user(self):
			response=self.client.post(self.register_url,self.user,format='text/html')
			self.assertEqual(response.status_code,302)

  def test_cant_register_user_withshortpassword(self):
			response=self.client.post(self.register_url,self.user_short_password,format='text/html')
			self.assertEqual(response.status_code,400)