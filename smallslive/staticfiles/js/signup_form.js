$(document).ready(function() {
  $loginForm = $('#form-login');
  $loginForm.submit(getAjaxSubmitForForm($loginForm, ["login", "password"]));

  $memberForm = $('#form-become-member');
  $memberForm.submit(getAjaxSubmitForForm(
    $memberForm, ["first_name", "last_name", "email", "email2", "password1", "password2",
      "terms_of_service", "privacy"]
  ));

});
