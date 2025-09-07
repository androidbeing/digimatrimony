from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required

from .models import (
    MemberProfile,
    FamilyDetail,
    BirthDetail,
    ProfessionalDetail,
    Caste,
    Koottam,
    Dhosam,
    Rasi,
    Star,
    Education,
    Profession,
    ProfilePhoto,
    Notification
)
from datetime import datetime, date
import re

from django.shortcuts import get_object_or_404

def home(request):
    return render(request, 'main/home.html')


def privacy_policy(request):
    return render(request, 'main/privacy_policy.html')


def generate_password(mobile, *args, **kwargs):
    """Initial password is simply reverse of mobile number."""
    return (mobile or '')[::-1]


def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        gender = request.POST.get('gender', '').strip()

        # Server-side validation
        name_pattern = re.compile(r'^[A-Z][a-zA-Z]*$')
        if not first_name or not name_pattern.match(first_name):
            return render(request, 'main/register.html', {'error': 'First name must start with a capital letter and contain letters only.'})
        if last_name and not name_pattern.match(last_name):
            return render(request, 'main/register.html', {'error': 'Last name must start with a capital letter and contain letters only.'})
        if not mobile:
            return render(request, 'main/register.html', {'error': 'Mobile number is required.'})

        # Normalize mobile: strip non-digits, handle optional +91/91/0 prefixes
        digits = re.sub(r'\D', '', mobile)
        # If starts with country code 91 or leading 0, take last 10 digits
        if len(digits) > 10:
            digits = digits[-10:]

        if len(digits) != 10:
            return render(request, 'main/register.html', {'error': 'Mobile number must contain 10 digits (optionally prefixed with +91 or 0).'} )

        # Indian mobile numbers should start with 6-9
        if digits[0] not in '6789':
            return render(request, 'main/register.html', {'error': 'Invalid Indian mobile number. It should start with 6,7,8, or 9.'})

        # use normalized 10-digit mobile as canonical username
        mobile = digits

        if User.objects.filter(username=mobile).exists():
            messages.error(request, 'A user with this mobile already exists. Please login.')
            return redirect('login')

        password = generate_password(mobile)

        user = User.objects.create_user(username=mobile, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()

        # create profile
        profile = MemberProfile.objects.create(user=user, mobile=mobile, gender=gender or 'O')
        profile.save()

        # add to Member group
        group, _ = Group.objects.get_or_create(name='Member')
        user.groups.add(group)

        # auto-login
        user = authenticate(username=mobile, password=password)
        if user:
            auth_login(request, user)
            messages.success(request, 'Registration successful. You are logged in.')
            return redirect('matches')

        messages.success(request, 'Registration successful. Please login using the generated password.')
        return redirect('login')

    return render(request, 'main/register.html')


def login_view(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(username=mobile, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('matches')
        # Render the login page with an inline error so the template can show it without a redirect
        return render(request, 'main/login.html', {'error': 'Invalid credentials. Please check your mobile number and password.'})

    return render(request, 'main/login.html')


def logout_view(request):
    auth_logout(request)
    return redirect('home')


@login_required
def matches(request):
    # show opposite-gender members
    try:
        profile = request.user.profile
        my_gender = profile.gender
    except MemberProfile.DoesNotExist:
        my_gender = None

    if my_gender == 'M':
        target_gender = 'F'
    elif my_gender == 'F':
        target_gender = 'M'
    else:
        target_gender = None

    # helper to determine if a profile has filled required sections
    def is_profile_complete(p: MemberProfile):
        try:
            fd = p.family_detail
            bd = p.birth_detail
            pd = p.professional_detail
        except (FamilyDetail.DoesNotExist, BirthDetail.DoesNotExist, ProfessionalDetail.DoesNotExist):
            return False

        # require at least one meaningful field in each section
        family_filled = any([fd.father_name, fd.mother_name, fd.siblings, fd.caste_id, fd.koottam_id, fd.kula_deity])
        birth_filled = any([bd.date_of_birth, bd.time_of_birth, bd.place_of_birth, bd.rasi_id, bd.star_id])
        prof_filled = any([pd.education_id, pd.profession_id, pd.monthly_income])

        return family_filled and birth_filled and prof_filled

    # if current user's profile is not complete, prompt them to fill it
    try:
        me_profile = request.user.profile
        me_complete = is_profile_complete(me_profile)
    except MemberProfile.DoesNotExist:
        me_profile = None
        me_complete = False

    qs = MemberProfile.objects.exclude(user=request.user)
    if target_gender:
        qs = qs.filter(gender=target_gender)

    # filter only fully completed profiles
    profiles = [p for p in qs if is_profile_complete(p)]

    return render(request, 'main/matches.html', {'profiles': profiles, 'me_complete': me_complete})


@login_required
def shortlisted(request):
    # placeholder: list of profiles the user shortlisted
    return render(request, 'main/shortlisted.html', {})


@login_required
def notifications(request):
    notifications = Notification.objects.all().order_by('-created_at')
    return render(request, 'main/notifications.html', {'notifications': notifications})


@login_required
def profile(request):
    # show and edit profile section-wise
    try:
        profile = request.user.profile
    except MemberProfile.DoesNotExist:
        # create a basic profile so the user sees the profile page and can fill details
        profile = MemberProfile.objects.create(user=request.user, mobile=getattr(request.user, 'username', '') or '')
        messages.info(request, 'A basic profile was created. Please complete your details.')

    if request.method == 'POST' and profile:
        section = request.POST.get('section')
        if section == 'member':
            # update user and basic profile
            first = request.POST.get('first_name', '').strip()
            last = request.POST.get('last_name', '').strip()
            mobile = request.POST.get('mobile', '').strip()
            gender = request.POST.get('gender', '').strip() or profile.gender

            if first:
                request.user.first_name = first
            if last:
                request.user.last_name = last
            if mobile:
                # also update profile.mobile
                profile.mobile = mobile
            profile.gender = gender
            request.user.save()
            profile.save()
            messages.success(request, 'Basic profile saved.')
            return redirect(reverse('profile'))
        if section == 'family':
            # validate mandatory fields first to avoid DB IntegrityError
            kula = request.POST.get('kula_deity', '').strip()
            if not kula:
                messages.error(request, 'Please fill Kula Deity before saving family details.')
                return redirect(reverse('profile') + '#family-form')

            # safe create/update
            fd, _ = FamilyDetail.objects.get_or_create(profile=profile)
            # CharFields in FamilyDetail are not null=True; use empty string instead of None
            fd.father_name = request.POST.get('father_name', '').strip() or ''
            fd.mother_name = request.POST.get('mother_name', '').strip() or ''
            fd.siblings = request.POST.get('siblings', '').strip() or ''
            fd.kula_deity = kula or ''
            caste_id = request.POST.get('caste')
            if caste_id:
                try:
                    fd.caste = Caste.objects.get(pk=int(caste_id))
                except (Caste.DoesNotExist, ValueError):
                    fd.caste = None
            else:
                fd.caste = None
            # save koottam FK if provided
            koottam_id = request.POST.get('koottam')
            if koottam_id:
                try:
                    fd.koottam = Koottam.objects.get(pk=int(koottam_id))
                except (Koottam.DoesNotExist, ValueError):
                    fd.koottam = None
            else:
                fd.koottam = None
            fd.save()
            messages.success(request, 'Family details saved.')
            return redirect(reverse('profile') + '#family-form')

        if section == 'birth':
            bd, _ = BirthDetail.objects.get_or_create(profile=profile)
            dob = request.POST.get('date_of_birth') or None
            tob = request.POST.get('time_of_birth') or None
            bd.date_of_birth = dob
            bd.time_of_birth = tob
            # place_of_birth is a CharField (blank=True) - store empty string if not provided
            bd.place_of_birth = request.POST.get('place_of_birth', '').strip() or ''
            rasi_id = request.POST.get('rasi')
            if rasi_id:
                try:
                    bd.rasi = Rasi.objects.get(pk=int(rasi_id))
                except (Rasi.DoesNotExist, ValueError):
                    bd.rasi = None
            else:
                bd.rasi = None
            # dhosam (new) - FK
            dhosam_id = request.POST.get('dhosam')
            if dhosam_id:
                try:
                    bd.dhosam = Dhosam.objects.get(pk=int(dhosam_id))
                except (Dhosam.DoesNotExist, ValueError):
                    bd.dhosam = None
            else:
                bd.dhosam = None
            star_id = request.POST.get('star')
            if star_id:
                try:
                    bd.star = Star.objects.get(pk=int(star_id))
                except (Star.DoesNotExist, ValueError):
                    bd.star = None
            else:
                bd.star = None
            bd.save()
            messages.success(request, 'Birth details saved.')
            return redirect(reverse('profile') + '#birth-form')

        if section == 'professional':
            pd, _ = ProfessionalDetail.objects.get_or_create(profile=profile)
            # education and profession (FKs)
            edu_id = request.POST.get('education')
            if edu_id:
                try:
                    pd.education = Education.objects.get(pk=int(edu_id))
                except (Education.DoesNotExist, ValueError):
                    pd.education = None
            else:
                pd.education = None

            prof_id = request.POST.get('profession')
            if prof_id:
                try:
                    pd.profession = Profession.objects.get(pk=int(prof_id))
                except (Profession.DoesNotExist, ValueError):
                    pd.profession = None
            else:
                pd.profession = None

            income = request.POST.get('monthly_income')
            try:
                pd.monthly_income = int(income) if income else None
            except ValueError:
                pd.monthly_income = None
            pd.save()
            messages.success(request, 'Professional details saved.')
            return redirect(reverse('profile') + '#prof-form')

        if section == 'reset_password':
            # change user's password after validating old password and confirmation
            old = request.POST.get('old_password', '')
            new = request.POST.get('new_password', '')
            conf = request.POST.get('confirm_password', '')
            # basic checks
            if not request.user.check_password(old):
                messages.error(request, 'Old password is incorrect.')
                return redirect(reverse('profile') + '#reset-password')
            if not new or new != conf:
                messages.error(request, 'New password and confirmation do not match.')
                return redirect(reverse('profile') + '#reset-password')
            # set and save new password, then logout so user can login again
            request.user.set_password(new)
            request.user.save()
            auth_logout(request)
            messages.success(request, 'Password changed. Please login with your new password.')
            return redirect('login')

    # provide options for dropdowns
    castes = Caste.objects.all()
    rasis = Rasi.objects.all()
    stars = Star.objects.all()
    koottams = Koottam.objects.all()
    dhosams = Dhosam.objects.all()
    educations = Education.objects.all()
    professions = Profession.objects.all()
    # compute date range for date of birth: between 50 years ago and 18 years ago
    today = date.today()
    try:
        max_dob = date(today.year - 18, today.month, today.day)
    except ValueError:
        # handle Feb29 edge-case by rolling back to last valid day
        max_dob = date(today.year - 18, today.month, 28)
    try:
        min_dob = date(today.year - 50, today.month, today.day)
    except ValueError:
        min_dob = date(today.year - 50, today.month, 28)

    return render(request, 'main/profile.html', {
        'profile': profile,
        'castes': castes,
        'rasis': rasis,
    'stars': stars,
    'koottams': koottams,
    'dhosams': dhosams,
        'educations': educations,
        'professions': professions,
        'min_dob': min_dob.isoformat(),
        'max_dob': max_dob.isoformat(),
    })


@login_required
def profile_detail(request, pk):
    # show read-only profile of another user (MemberProfile.pk)
    profile = get_object_or_404(MemberProfile, pk=pk)
    return render(request, 'main/profile_detail.html', {'profile': profile})



# Photo upload
@login_required
def profile_photo_upload(request):
    profile = request.user.profile
    if profile.photos.count() >= 5:
        messages.error(request, "Maximum 5 photos allowed.")
        return redirect('profile')
    if request.method == "POST" and request.FILES.get('photo'):
        photo = request.FILES['photo']
        if photo.size > 5 * 1024 * 1024:
            messages.error(request, "Max file size is 5MB.")
            return redirect('profile')
        if not photo.content_type in ['image/jpeg', 'image/png']:
            messages.error(request, "Only JPEG and PNG allowed.")
            return redirect('profile')
        is_primary = profile.photos.count() == 0
        ProfilePhoto.objects.create(profile=profile, image=photo, is_primary=is_primary)
        messages.success(request, "Photo uploaded.")
    return redirect('profile')

# Set primary photo
@login_required
def profile_photo_set_primary(request, pk):
    profile = request.user.profile
    photo = get_object_or_404(ProfilePhoto, pk=pk, profile=profile)
    ProfilePhoto.objects.filter(profile=profile, is_primary=True).update(is_primary=False)
    photo.is_primary = True
    photo.save()
    messages.success(request, "Profile photo updated.")
    return redirect('profile')

# Delete photo
@login_required
def profile_photo_delete(request, pk):
    profile = request.user.profile
    photo = get_object_or_404(ProfilePhoto, pk=pk, profile=profile)
    photo.delete()
    messages.success(request, "Photo deleted.")
    return redirect('profile')

@login_required
def profile_photo_set_primary(request, pk):
    profile = request.user.profile
    photo = get_object_or_404(ProfilePhoto, pk=pk, profile=profile)
    ProfilePhoto.objects.filter(profile=profile, is_primary=True).update(is_primary=False)
    photo.is_primary = True
    photo.save()
    messages.success(request, "Profile photo updated.")
    return redirect('profile')

@login_required
def profile_photo_delete(request, pk):
    profile = request.user.profile
    photo = get_object_or_404(ProfilePhoto, pk=pk, profile=profile)
    photo.delete()
    messages.success(request, "Photo deleted.")
    return redirect('profile')