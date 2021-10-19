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

class RegisterTest(BaseTest):
  def test_can_view_page_correctly(self):
			response=self.client.get(self.register_url)
			self.assertEqual(response.status_code,200)
			self.assertTemplateUsed(response,'auth/register.html')