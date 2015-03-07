from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm


def index(request):
    context_dict = {}

    category_list = Category.objects.order_by('-likes')[:5]
    context_dict['categories'] = category_list

    pages_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = pages_list
    return render(request, 'rango/index.html', context_dict)


def about(request):
    context_dict = {'emphasized_message': 'This is italicized!'}
    return render(request, 'rango/about.html', context_dict)


def category(request, category_name_slug):
    context_dict = {'category_name_slug': category_name_slug}

    try:
        cat = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = cat.name

        context_dict['category'] = cat
        pages = Page.objects.filter(category=cat)
        context_dict['pages'] = pages

    except Category.DoesNotExist:
        pass

    return render(request, 'rango/category.html', context_dict)

@login_required()
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print form.errors

    else:
        form = CategoryForm()

    return render(request, 'rango/add_category.html', {'form': form})

@login_required()
def add_page(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                return category(request, category_name_slug)
        else:
            print form.errors

    else:
        form = PageForm()

    context_dict = {'form': form, 'category': cat, 'category_name_slug': category_name_slug}

    return render(request, 'rango/add_page.html', context_dict)


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True

            new_user = authenticate(username=request.POST['username'], password=request.POST['password'])
            login(request, new_user)  # automatically logs in new user

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html',
                  {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                context = {'disabled': 'Your Rango account is currently disabled.'}
                return render(request, 'rango/login.html', context)
        else:
            context = {'failure': 'Sorry, we do not recognize your username or password. Please try logging in again.'}
            return render(request, 'rango/login.html', context)
    else:
        return render(request, 'rango/login.html', {})


def restricted(request):
    context = {'success': 'You are authenticated!', 'failure': 'You are not logged in!'}
    return render(request, 'rango/restricted.html', context)

@login_required()
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')