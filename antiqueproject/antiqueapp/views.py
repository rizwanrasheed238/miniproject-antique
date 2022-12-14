from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


# def index(request):
#     return render(request,"index-1.html")

from django.shortcuts import render
from django.contrib import messages, auth
from django.shortcuts import render, redirect
from .models import Account,Category,product
from django.contrib.auth import authenticate
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.mail import send_mail





# from asyncio.windows_events import NULL
# from django.shortcuts import render, redirect
# from category.models import Category, Subcategory
# from credentialapp.models import log_user
# from productapp.models import Product
# from django.contrib import messages
# from credentialapp.views import login
# from .models import Cart, Wishlist
# from django.contrib import messages

# # Create your views here.
def products(request):
    products = product.objects.all()
    category = Category.objects.all()
    return render(request, 'product.html', {'datas': products, 'category': category})

def home(request):
    products = product.objects.all()
    category = Category.objects.all()
    return render(request, 'home.html', {'datas': products, 'category': category})

def productdet(request,id):
    products = product.objects.filter(id=id)
    # category = Category.objects.all()
    return render(request, 'productdet.html', {'datas': products})


def blog(request):
    return render(request,"blog.html")

def cart(request):
    return render(request,"cart.html")

def login(request):
    if request.method == 'POST':
        email=request.POST['email']
        password=request.POST['password']

        user=authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            request.session['email']=email
            messages.success(request, 'you are logged in')
            # store user details in session

            request.session['email']=email

            return redirect('home')
        else:
            messages.success(request, 'invalid login credentials')
            return redirect('register')
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        email=request.POST['email']
        password=request.POST['password']
        fname=request.POST['fname']
        lname=request.POST['lname']
        phone_number=request.POST['phone']
        password=request.POST['password']
        cpassword = request.POST['cpassword']

        print(email,password,fname,lname,phone_number)
        if Account.objects.filter(email=email).exists():
            messages.error(request, 'email already exists')
            return redirect('login')
        elif password!=cpassword:
             messages.error(request, 'password not matching')
             messages.info(request,"password not matching")
             return redirect('login')
        else:
            user=Account.objects.create_user(email=email, password=password, fname=fname, lname=lname,  phone_number=phone_number)
            user.save()
            messages.success(request, 'you are registered')
            messages.success(request, 'Thank you for registering with us.')
            messages.success(request, 'Please verify your email for login!')

            current_site = get_current_site(request)
            message = render_to_string('account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            send_mail(
                'Please activate your account',
                message,
                'medievalstore123@gmail.com',
                [email],
                fail_silently=False,
            )

            return redirect('/login/?command=verification&email=' + email)
            # return redirect('login')
    return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')

def index(request):
    products = product.objects.all()
    category = Category.objects.all()
    return render(request,'index-1.html',{'datas':products,'category':category})


def search(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        if query:
            multiple_q = Q(Q(name__icontains=query) | Q(descripton__icontains=query))
            products = product.objects.filter(multiple_q)
            return render(request, 'search.html', {'product':products})
        else:
            messages.info(request, 'No search result!!!')
            print("No information to show")
    return render(request, 'search.html', {})



def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email

            current_site = get_current_site(request)
            message = render_to_string('ResetPassword_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            send_mail(
                'Please activate your account',
                message,
                'medievalstore123@gmail.com',
                [email],
                fail_silently=False,
            )

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'resetPassword.html')

# def add_wishlist(request,id):
#     if 'email' in request.session:
#         item=Account.objects.get(id=id)
#         user=request.session['email']
#         if Account.objects.filter( user_id =user,product_id=item).exists():
#             return redirect('view_wishlist')
#         else:
#             new_wishlist=Account(user_id=user,product_id=item.id)
#             new_wishlist.save()
#             return redirect('view_wishlist')
#     messages.success(request, 'Sign in..!!')
#     return redirect(login)
#
#
# @login_required(login_url='login')
# def view_wishlist(request):
#     if 'email' in request.session:
#         email = request.session['email']
#         cart=Account.objects.filter(user_id=email)
#         category=Category.objects.all()
#
#         return render(request,"wishlist.html",{'cart':cart,'email':email,'category':category})
#     return redirect(login)
#
# # Remove Items From Wishlist
# def de_wishlist(request,id):
#     Account.objects.get(id=id).delete()
#     return redirect('view_wishlist')