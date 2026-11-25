
import logging

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_POST
from django.db import transaction, IntegrityError

from .models import UserProfile
from .forms import SignupForm, UserProfileForm


logger = logging.getLogger(__name__)


# 1. CUSTOMER SIGNUP
def signup_view(request):

    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    UserProfile.objects.create(user=user)

                login(request, user)

                messages.success(
                    request,
                    "Your VELORA account has been created successfully!"
                )

                return redirect('accounts:profile')

            except IntegrityError:
                messages.error(
                    request,
                    "We could not create your account. Please try again."
                )

            except Exception:
                logger.exception("Unexpected error during signup.")
                messages.error(
                    request,
                    "Something went wrong. Please try again later."
                )

    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


# 2. CUSTOMER LOGIN
def login_view(request):

    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            messages.success(
                request,
                f"Welcome back, {user.first_name or user.username}!"
            )

            return redirect('accounts:profile')

        messages.error(
            request,
            "Invalid username or password. Please try again."
        )

    else:
        form = AuthenticationForm(request)

    return render(request, 'accounts/login.html', {'form': form})


# 3. CUSTOMER LOGOUT
@login_required
@require_POST
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have successfully logged out."
    )

    return redirect('store:home')


# 4. VIEW USER PROFILE
@login_required
def profile_view(request):

    try:
        profile, created = UserProfile.objects.get_or_create(
            user=request.user
        )

        return render(
            request,
            'accounts/profile.html',
            {'profile': profile}
        )

    except Exception:
        logger.exception("Error loading user profile.")

        messages.error(
            request,
            "Unable to load your profile. Please try again."
        )

        return redirect('store:home')


# 5. UPDATE USER PROFILE
@login_required
def update_profile_view(request):

    try:
        profile, created = UserProfile.objects.get_or_create(
            user=request.user
        )

        if request.method == 'POST':

            profile_form = UserProfileForm(
                request.POST,
                instance=profile
            )

            if profile_form.is_valid():
                profile_form.save()

                messages.success(
                    request,
                    "Your profile has been updated successfully!"
                )

                return redirect('accounts:profile')

        else:
            profile_form = UserProfileForm(instance=profile)

        return render(
            request,
            'accounts/update_profile.html',
            {'form': profile_form}
        )

    except Exception:
        logger.exception("Error updating user profile.")

        messages.error(
            request,
            "Unable to update your profile. Please try again."
        )

        return redirect('accounts:profile')
