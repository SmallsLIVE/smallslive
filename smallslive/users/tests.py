from django.test import TestCase
from .models import SmallsUser
from .forms import UserSignupForm

class TestUserSignupPriorToPayment(TestCase):

    # Email
    def test_user_signup_mispelled_email(self):
        form = UserSignupForm(data = {
            'email' : 'jsam.audio@gmail.con',
            'password1' : 'testing',
            'password2' : 'testing',
            'terms_of_service' : True,
            'newsletter' : False,
        })
        self.assertFalse(form.is_valid())

    def test_user_signup_overly_long_email(self):
        form = UserSignupForm(data = {
            'email' : 'jsamajsamajsamajsamajsamajsamajsamajsamajsamajsamajsamajsamajsamajsamajsamajamessam@gmail.com',
            'password1' : 'testing',
            'password2' : 'testing',
            'terms_of_service' : True,
            'newsletter' : False,
        })
        self.assertFalse(form.is_valid())

    # Passwords
    def test_user_signup_mismatched_passwords(self):
        form = UserSignupForm(data = {
            'email' : 'jsam.audio@gmail.com',
            'password1' : 'testing',
            'password2' : 'testng',
            'terms_of_service' : True,
            'newsletter' : False,
        })
        self.assertFalse(form.is_valid())

    # Checkboxes
    def test_user_signup_forgot_checkboxes(self):
        form = UserSignupForm(data = {
            'email' : 'jsam.audio@gmail.com',
            'password1' : 'testing',
            'password2' : 'testing',
            'terms_of_service' : False,
            'newsletter' : False,
        })
        self.assertFalse(form.is_valid())

    # Names
    def test_user_signup_overly_long_first_name(self):
        form = UserSignupForm(data = {
            'email' : 'jsam.audio@gmail.com',
            'password1' : 'testing',
            'password2' : 'testing',
            'terms_of_service' : True,
            'newsletter' : False,
            'first_name' : 'abcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcd',
            'last_name' : 'Doe',
        })
        self.assertFalse(form.is_valid())

    def test_user_signup_overly_long_last_name(self):
        form = UserSignupForm(data = {
            'email' : 'jsam.audio@gmail.com',
            'password1' : 'testing',
            'password2' : 'testing',
            'terms_of_service' : True,
            'newsletter' : False,
            'first_name' : 'John',
            'last_name' : 'abcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcd',
        })
        self.assertFalse(form.is_valid())

    # Correct
    def test_user_signup_min_correct_info(self):
        form = UserSignupForm(data = {
            'email' : 'jsam.audio@gmail.com',
            'password1' : 'testing',
            'password2' : 'testing',
            'terms_of_service' : True,
            'newsletter' : False,
        })
        self.assertTrue(form.is_valid())

    def test_user_signup_correct_info(self):
        form = UserSignupForm(data = {
            'email' : 'jsam.audio@gmail.com',
            'password1' : 'testing',
            'password2' : 'testing',
            'terms_of_service' : True,
            'newsletter' : True,
            'first_name' : 'John',
            'last_name' : 'Doe',
        })
        self.assertTrue(form.is_valid())

# class TestSupporterSignup(TestCase):
#     # code goes here

# class TestBenefactorSignup(TestCase):
#     # code goes here
