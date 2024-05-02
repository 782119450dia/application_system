from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator  # Import correct du générateur de token
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import render, redirect
from authentification import settings

def home(request):
    return render(request, 'app/index.html')


def register(request):
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        password1 = request.POST['password1']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom a déjà été pris")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà associé à un compte")
            return redirect('register')
        if not username.isalnum():
            messages.error(request, 'Le nom doit être alphanumérique')
            return redirect('register')
        if password != password1:
            messages.error(request, 'Les deux mots de passe ne correspondent pas.')
            return redirect('register')

        mon_utilisateur = User.objects.create_user(username=username, email=email, password=password)
        mon_utilisateur.first_name = firstname
        mon_utilisateur.last_name = lastname
        mon_utilisateur.is_active = False
        mon_utilisateur.save()
        messages.success(request, 'Votre compte a été créé avec succès')

        # Envoi d'email de bienvenue
        subject = "Bienvenue sur le système de gestion des contributions et des paiements Django"
        message = "Bienvenue " + mon_utilisateur.first_name + " " + mon_utilisateur.last_name + "\n Nous sommes heureux de vous compter parmi nous\n\n\nMerci\n\n Ibrahima, programmeur"
        from_email = settings.EMAIL_HOST_USER
        to_list = [mon_utilisateur.email]
        send_mail(subject, message, from_email, to_list, fail_silently=False)

        # Email de confirmation
        current_site = get_current_site(request)
        email_subject = "Confirmation de l'adresse email sur Ibrahima"
        messageConfirm = render_to_string("template_confirmation_email.html", {
            "name": mon_utilisateur.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(mon_utilisateur.pk)),
            'token': default_token_generator.make_token(mon_utilisateur)  # Utilisation du générateur de token par défaut
        })
        email = EmailMessage(
            email_subject,
            messageConfirm,
            settings.EMAIL_HOST_USER,
            [mon_utilisateur.email]
        )
        email.fail_silently = False
        email.send()
        return redirect('login')
    return render(request, 'app/register.html')


def logIn(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Ce nom d'utilisateur n'existe pas.")
            return redirect('login')  # Rediriger vers la page de connexion avec un message d'erreur
        authenticated_user = authenticate(username=username, password=password)
        if authenticated_user is not None:
            login(request, authenticated_user)
            firstname = authenticated_user.first_name
            return render(request, 'app/index.html', {'firstname': firstname})
        else:
            messages.error(request, 'Mauvaise authentification')
            return redirect('login')
    return render(request, 'app/login.html')


def logOut(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès')
    return redirect('home')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)  # Changement de variable pour éviter la confusion avec la classe User
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):  # Utilisation du générateur de token par défaut
        user.is_active = True
        user.save()
        messages.success(request, "votre compte a été activé félicitations connectez-vous maintenant")
        return redirect('login')
    else:
        messages.error(request, 'activation échouée!!!! ')
        return redirect('home')
