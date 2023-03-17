from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
#from hijack.admin import HijackUserAdminMixin

from .models import SmallsUser


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'duplicate_email': "A user with that email address already exists.",
        'password_mismatch': "The two password fields didn't match.",
    }
    email = forms.EmailField(label="Email", max_length=50,)
    password1 = forms.CharField(label="Password",
        widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation",
        widget=forms.PasswordInput,
        help_text="Enter the same password as above, for verification.")

    class Meta:
        model = SmallsUser
        fields = ("email",)

    def clean_email(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        email = self.cleaned_data["email"]
        try:
            SmallsUser._default_manager.get(email=email)
        except SmallsUser.DoesNotExist:
            return email
        raise forms.ValidationError(
            self.error_messages['duplicate_email'],
            code='duplicate_email',
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    email = forms.EmailField()
    password = ReadOnlyPasswordHashField(label="Password",
        help_text="Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>.")

    class Meta:
        model = SmallsUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class SmallsUserAdmin(UserAdmin):
    add_form_template = 'admin/auth/user/add_form.html'
    date_hierarchy = 'last_login'
    fieldsets = (
        ('Important info', {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'address_1', 'address_2', 'city', 'state',
                                      'zip', 'country', 'phone_1', 'website', 'photo')}),
        ('Site info', {'fields': ('access_level', 'login_count', 'accept_agreement', 'renewal_date',
                                  'subscription_price', 'company_name', 'newsletter')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_vip',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'archive_access_until')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('email', 'artist', 'access_level', 'login_count', 'subscription_price',
                    'date_joined', 'renewal_date',  'is_active', 'hijack_field')
    list_filter = ('access_level', 'is_active')
    search_fields = ('email',)
    save_on_top = True
    ordering = ['email', 'last_login']

admin.site.register(SmallsUser, SmallsUserAdmin)

