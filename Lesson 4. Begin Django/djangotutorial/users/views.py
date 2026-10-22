from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from .forms import CustomUserLoginForm, CustomUserCreationForm, CustomPasswordResetForm, CustomSetPasswordForm
from .utils import save_custom_image
from django.contrib import messages

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.
def user_login(request):
    if request.method == "POST":
        form = CustomUserLoginForm(data = request.POST)
        #print('post data', request.POST)
        if form.is_valid():
            user = authenticate(request,
                                username=form.cleaned_data["username"],
                                password=form.cleaned_data["password"])
            if user is not None:
                login(request, user)
                return redirect("homepage")
        else:
            print('form errors', form.errors)
    else:
        form = CustomUserLoginForm()
    return render(request, "login.html", {'form': form})

def user_register(request):
    if request.method == 'POST':
        # print("---Зберігаємо дані користувача---")
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                if 'email' in form.cleaned_data:
                    user.username = form.cleaned_data['email']
                if 'image' in request.FILES:
                    image = request.FILES.get("image")
                    user.image_small = save_custom_image(image, size=(300,300), folder="small")
                    user.image_medium = save_custom_image(image, size=(800,800), folder="medium")
                    user.image_large = save_custom_image(image, size=(1200,1200), folder="large")
                user.save()
                login(request, user)
                return redirect('homepage')
            except Exception as e:
                messages.error(request, f"Щось пішло не так: {str(e)}")
        else:
            messages.success(request, 'Виправте помилки у формі')
    else:
        form = CustomUserCreationForm()

    return render(request, "register.html", {"form": form})

def user_logout(request):
    logout(request)
    return redirect('homepage')

def password_reset_request(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect('users:password_reset_done')
        else:
            messages.info(request, 'Виникли помилки при заповненні форми')
    else:
        form = CustomPasswordResetForm()

    return render(request, 'password_reset.html', {'form': form})

def password_reset_done(request):
    return render(request, 'password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('users:password_reset_complete')
            else:
                messages.info(request, 'Виникли помилки при заповненні форми')
        else:
            form = CustomSetPasswordForm(user)

        return render(request, 'password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'Посилання для відновлення пароля недійсне')
        return render(request, 'password_reset_confirm.html', {'form': None})

def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')