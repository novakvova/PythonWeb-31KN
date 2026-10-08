from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from .forms import CustomUserLoginForm, CustomUserCreationForm
from .utils import save_custom_image
from django.contrib import messages


# Create your views here.
def user_login(request):
    if request.method == "POST":
        form = CustomUserLoginForm(request.POST)
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