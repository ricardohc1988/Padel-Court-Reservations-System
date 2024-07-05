from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.utils import timezone
from django.utils.timezone import make_aware
from .utils import generate_code, send_verification_email, resend_verification_email, send_reservation_confirmation_email, send_reservation_cancellation_email
from .models import Location, Reservation, User
from .forms import ReservationForm, SignUpForm, LoginForm, UserAccountUpdateForm, CodeVerificationForm
from django.db.models import Q
import datetime
from datetime import timedelta

def home(request):
    return render(request, 'home.html')

def locations_list(request):
    locations = Location.objects.all()
    return render(request, 'locations.html', {'locations': locations})

def signup_view(request):
    """
    Handles user signup process.

    If request method is POST:
        - Validates SignUpForm.
        - Saves the user as inactive.
        - Generates and sends a verification code via email.
        - Redirects to 'verify_email' page.

    If request method is GET:
        - Renders 'signup.html' template with SignUpForm.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Rendered 'signup.html' template with SignUpForm or redirects to 'verify_email' page.
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            code = generate_code()
            request.session['code'] = code
            request.session['user_id'] = user.id
            request.session['code_generated_at'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S') 

            send_verification_email(user, code)

            return redirect('verify_email')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def verify_email(request):
    """
    Handles the email verification process for user registration.

    This view checks the validity of the verification code submitted by the user
    against the code stored in the session. If valid, it activates the user account
    and redirects to the login page. If invalid or expired, it displays appropriate
    error messages.

    Returns:
        HttpResponse: Renders the 'registration/verify_email.html' template with
        the verification form and user email context.
    """
    user_email = User.objects.get(id=request.session['user_id']).email
    if request.method == 'POST':
        form = CodeVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            code_generated_at = request.session.get('code_generated_at')
            
            if code_generated_at:
                code_generated_at = make_aware(timezone.datetime.strptime(code_generated_at, '%Y-%m-%d %H:%M:%S'))
                if timezone.now() - code_generated_at > timedelta(minutes=3):
                    messages.error(request, 'Code has expired. Please request a new code.')
                    return render(request, 'registration/verify_email.html', {'form': form, 'user_email': user_email})

            if code == request.session.get('code'):
                user_id = request.session.get('user_id')
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()
                del request.session['code']
                del request.session['user_id']
                del request.session['code_generated_at']
                messages.success(request, 'Your email has been verified. You can now log in.')
                return redirect('login')
            else:
                messages.error(request, 'Invalid code')
    else:
        form = CodeVerificationForm()
    return render(request, 'registration/verify_email.html', {'form': form, 'user_email': user_email})

def resend_code(request):
    """
    Resends a new verification code to the user's email for account activation.

    This view generates a new verification code, stores it in the session, and
    sends it to the user's email address stored in the session. It also handles
    session expiration and redirects to the signup page if necessary.

    Returns:
        HttpResponseRedirect: Redirects to the 'verify_email' view after sending
        the new verification code.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please sign up again.')
        return redirect('signup')

    user = User.objects.get(id=user_id)
    code = generate_code()
    request.session['code'] = code
    request.session['code_generated_at'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

    resend_verification_email(user, code)

    messages.success(request, 'A new code has been sent to your email.')
    return redirect('verify_email')

def login_view(request):
    """
    Handles user authentication and login process.

    This view manages the user login form submission, validates user credentials,
    and logs the user into the system if authentication is successful. If the form
    submission is invalid, it displays an error message to the user.

    Returns:
        HttpResponse: Renders the 'registration/login.html' template with the login
        form and appropriate messages based on the form validation.
    """
    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('reservations_list')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    """
    Handles user logout process.

    This view logs out the currently authenticated user, clears any session data
    associated with the user's session, and redirects to the home page.

    Returns:
        HttpResponseRedirect: Redirects to the 'home' view after logging out the user.
    """
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

@login_required(login_url='/login/')
def my_account(request):
    """
    Handles user account update functionality.

    This view allows users to update their account information such as username,
    email, and other profile details. It validates the form submission and updates
    the user's information if the form data is valid. If the form is not valid,
    it displays validation errors to the user.

    Returns:
        HttpResponse: Renders the 'registration/my_account.html' template with the
        account update form and success/error messages based on form validation.
    """
    if request.method == 'POST':
        form = UserAccountUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Information updated successfully')
            return redirect('my_account')
    else:
        form = UserAccountUpdateForm(instance=request.user)
    
    return render(request, 'registration/my_account.html', {'form': form})

@login_required(login_url='/login/')
def reservations_list(request):
    """
    Displays a list of upcoming reservations for the logged-in user.

    This view retrieves upcoming reservations from the database based on the current
    date and time. It filters reservations that are confirmed and haven't passed yet.
    The filtered reservations are then rendered in the 'reservations.html' template.

    Returns:
        HttpResponse: Renders the 'reservations.html' template with the upcoming
        reservations retrieved from the database.
    """
    now = timezone.localtime(timezone.now())
    today = now.date()

    upcoming_reservations = Reservation.objects.filter(
        Q(user=request.user) &
        Q(status='confirmed') &
        (Q(date__gt=today) | (Q(date=today) & Q(start_time__gt=now.time())))
    ).order_by('date', 'start_time')

    return render(request, 'reservations.html', {'upcoming_reservations': upcoming_reservations})

@login_required(login_url='/login/')
def new_reservation(request):
    """
    Handles the creation of a new reservation.

    This view processes the submission of a reservation form, validates the form data,
    checks for conflicting reservations, and sends a confirmation email upon successful
    reservation creation. It also handles errors related to date/time validation and
    conflicting bookings.

    Returns:
        HttpResponse: Renders the 'new_reservation.html' template with the reservation
        form and appropriate success/error messages based on form validation.
    """
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            now = timezone.localtime(timezone.now())

            if reservation.date < now.date():
                messages.error(request, 'Please choose another date.')
                return render(request, 'new_reservation.html', {'form': form})

            start_time = datetime.datetime.strptime(request.POST['start_time'], '%H:%M').time()
            end_time = datetime.datetime.strptime(request.POST['end_time'], '%H:%M').time()

            if reservation.date == now.date() and start_time <= now.time():
                messages.error(request, 'Please choose a future time for today.')
                return render(request, 'new_reservation.html', {'form': form})

            end_time = (datetime.datetime.combine(reservation.date, end_time) - timedelta(minutes=1)).time()
            reservation.end_time = end_time.strftime('%H:%M')

            conflicting_reservations = Reservation.objects.filter(
                court=reservation.court,
                date=reservation.date,
                start_time__lte=reservation.end_time,
                end_time__gte=reservation.start_time,
                status = 'confirmed',
            ).exclude(pk=reservation.pk)

            if conflicting_reservations.exists():
                messages.error(request, 'Court is already booked for this time.')
                return render(request, 'new_reservation.html', {'form': form})

            reservation.save()
            send_reservation_confirmation_email(reservation)
            messages.success(request, 'Reservation created successfully and confirmation email sent.')
            return redirect('reservations_list')
    else:
        form = ReservationForm()

    return render(request, 'new_reservation.html', {'form': form})

@login_required(login_url='/login/')
def past_reservations(request):
    """
    Displays a list of past reservations for the logged-in user.

    This view retrieves past reservations from the database based on the current
    date and time. It filters reservations that are confirmed and have already passed.
    The filtered reservations are then rendered in the 'past_reservations.html' template.

    Returns:
        HttpResponse: Renders the 'past_reservations.html' template with the past
        reservations retrieved from the database.
    """
    now = timezone.localtime(timezone.now())
    today = now.date()

    past_reservations = Reservation.objects.filter(
        Q(user=request.user) &
        Q(status='confirmed') & 
        (Q(date__lt=today) | (Q(date=today) & Q(end_time__lt=now.time())))
    ).order_by('-date')

    return render(request, 'past_reservations.html', {'past_reservations': past_reservations})

@login_required(login_url='/login/')
def cancelled_reservations(request):
    """
    Displays a list of cancelled reservations for the logged-in user.

    This view retrieves cancelled reservations from the database and filters them
    based on the logged-in user. The filtered reservations are then rendered in
    the 'cancelled_reservations.html' template.

    Returns:
        HttpResponse: Renders the 'cancelled_reservations.html' template with the
        cancelled reservations retrieved from the database.
    """
    cancelled_reservations = Reservation.objects.filter(user=request.user, status='cancelled').order_by('-date')
    return render(request, 'cancelled_reservations.html', {'cancelled_reservations': cancelled_reservations})

@login_required(login_url='/login/')
def cancel_reservation(request, id):
    """
    Handles the cancellation of a reservation.

    This view allows a logged-in user to cancel a reservation if it is in 'confirmed'
    status and meets the cancellation conditions (not less than 2 hours before the
    reservation start time). Upon successful cancellation, an email notification is sent
    to the user. It handles errors related to reservation status and cancellation timing.

    Returns:
        HttpResponseRedirect: Redirects to the 'reservations_list' view after successfully
        cancelling the reservation or displaying an error message.
    """
    reservation = get_object_or_404(Reservation, id=id)

    if reservation.status == 'confirmed':
        start_time = datetime.datetime.strptime(reservation.start_time, '%H:%M').time()
        now = timezone.localtime(timezone.now())
        time_difference = datetime.datetime.combine(now.date(), start_time) - datetime.datetime.combine(now.date(), now.time())

        if reservation.date == now.date()and time_difference.total_seconds() / 3600 < 2:
           messages.error(request, 'Reservation cannot be cancelled less than 2 hours before start time.')
        else:
            reservation.status = 'cancelled'
            reservation.save()
            send_reservation_cancellation_email(reservation)
            messages.info(request, 'Reservation cancelled')
            return redirect('reservations_list')
    else:
        messages.error(request, 'Reservation cannot be cancelled.')

    return redirect('reservations_list')
