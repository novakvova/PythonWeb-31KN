from django.contrib.auth.forms import (AuthenticationForm,
                                       UserCreationForm,
                                       SetPasswordForm)
from django import forms
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string

from users.models import CustomUser


class CustomUserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Логін',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


class CustomUserCreationForm(UserCreationForm):
    # username = forms.CharField(
    #     label="Логін",
    #     widget=forms.TextInput(attrs={'class': 'form-control'})
    # )

    email = forms.EmailField(
        label="Електронна пошта",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    first_name = forms.CharField(
        label="Ім'я",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', "placeholder": "Вкажіть ім'я"})
    )

    last_name = forms.CharField(
        label="Прізвище",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    image = forms.ImageField(
        label="Зображення",
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
        label="Пароль",
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    password2 = forms.CharField(
        label="Повторіть пароль",
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'image', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Дана пошта уже зареєстрована")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Паролі не співпадають.")
        return password2


class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(
        label='Електронна пошта',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Користувача з такою поштою не знайдено")
        return email

    def save(self, request):
        email = self.cleaned_data['email']
        user = CustomUser.objects.get(email=email)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = request.build_absolute_uri(
            f'/users/reset/{uid}/{token}/'
        )

        subject = 'Відновлення пароля'
        html_message = render_to_string('password_reset_email.html', {
            'user': user,
            'reset_link': reset_link,
        })
        plain_message = (
            f'Привіт, {user.first_name}!\n\n'
            f'Щоб встановити новий пароль, перейдіть за посиланням:\n{reset_link}\n\n'
            f'Якщо ви не робили цей запит, проігноруйте цей лист.'
        )

        send_mail(
            subject,
            plain_message,  # текстова версія (запасна)
            None,
            [email],
            html_message=html_message,  # красивий HTML-лист
        )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="Новий пароль",
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Вкажіть новий пароль'
        })
    )

    new_password2 = forms.CharField(
        label="Повторіть пароль",
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторіть новий пароль'
        })
    )