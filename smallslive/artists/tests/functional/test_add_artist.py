import pytest
import pytest_bdd
import re
from functools import partial
from pytest_bdd import given, when, then
from users.models import SmallsEmailAddress

scenario = partial(pytest_bdd.scenario, 'add_artist.feature')
pytestmark = pytest.mark.django_db


@scenario('Submitting an empty artist form')
def test_submit_empty_form(transactional_db):
    pass


@scenario('Submitting a valid artist')
def test_add_valid_artist(transactional_db):
    pass


@given("I'm an admin user")
def admin_user(browser, live_server, django_user_model):
    django_user_model.objects.create_superuser('admin@example.com', 'password')
    browser.visit(live_server.url + '/accounts/login/')
    browser.fill('login', 'admin@example.com')
    browser.fill('password', 'password')
    browser.find_by_css('button[type="submit"]').first.click()


@when('I go to the artist add page')
def go_to_article(browser, live_server):
    browser.visit(live_server.url + '/artists/add/')


@when('I should see a form')
def see_a_form(browser):
    assert browser.find_by_tag('form')


@when(re.compile('I input (?P<value>[.@\w]+) for (?P<field>\w+)'))
def input_value(value, field, browser):
    browser.fill(field, value)


@when(re.compile('I press (?P<value>\w+)'))
def press_button(browser, value):
    browser.find_by_name('submit').first.click()


@when(re.compile('I choose (?P<value>\w+) for (?P<field>\w+) radio button'))
def choose_radio_button(field, value, browser):
    browser.choose(field, value)

@then('I should see an error message')
def see_error_message(browser):
    assert browser.find_by_css('span[id^="error"]')

@then(re.compile('the text "(?P<value>[. @\w]+)" should be present'))
def see_message(value, browser):
    assert browser.is_text_present(value)
