import re
from pytest_bdd import scenario, given, when, then


@scenario('add_artist.feature', 'Submitting an empty artist form')
def test_add_artists():
    pass


@given("I'm an admin user")
def admin_user(django_user_model):
    admin = django_user_model.objects.create_superuser('admin', 'password')
    return admin


@when('I go to the artist add page')
def go_to_article(browser, live_server):
    browser.visit(live_server.url + '/artists/add/')


@when('I should see a form')
def see_a_form(browser):
    assert browser.find_by_tag('form')


@when(re.compile('I input (?P<value>\w+) for (?P<field>\w+)'))
def input_value(value, field, browser):
    browser.fill(field, value)


@when(re.compile('I press (?P<value>\w+)'))
def press_button(browser, value):
    browser.find_by_name('submit').first.click()


@then('I should see error message')
def see_error_message(browser):
    assert browser.find_by_css('span[id^="error"]')
