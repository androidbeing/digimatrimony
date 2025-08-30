from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class MemberProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    mobile = models.CharField(max_length=15, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='O')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        name = f"{self.user.first_name} {self.user.last_name}".strip()
        return name or self.mobile


class Caste(models.Model):
    caste = models.CharField(max_length=100, unique=True)
    caste_ta = models.CharField(max_length=100, blank=True, help_text='Tamil name')

    class Meta:
        verbose_name = 'Caste'
        verbose_name_plural = 'Castes'

    def __str__(self):
        return self.caste


class Koottam(models.Model):
    caste = models.ForeignKey(Caste, on_delete=models.CASCADE, related_name='koottams')
    subcaste = models.CharField(max_length=100)
    subcaste_ta = models.CharField(max_length=100, blank=True, help_text='Tamil name')

    class Meta:
        unique_together = (('caste', 'subcaste'),)
        verbose_name = 'Koottam'
        verbose_name_plural = 'Koottams'

    def __str__(self):
        return f"{self.subcaste} ({self.caste.caste})"


class FamilyDetail(models.Model):
    profile = models.OneToOneField(MemberProfile, on_delete=models.CASCADE, related_name='family_detail')
    father_name = models.CharField(max_length=200, blank=True)
    mother_name = models.CharField(max_length=200, blank=True)
    siblings = models.CharField(max_length=200, blank=True, help_text='Comma separated names or count')
    caste = models.ForeignKey(Caste, on_delete=models.SET_NULL, null=True, blank=True)
    koottam = models.ForeignKey(Koottam, on_delete=models.SET_NULL, null=True, blank=True)
    kula_deity = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Family of {self.profile}"


class Rasi(models.Model):
    rasi = models.CharField(max_length=50, unique=True)
    rasi_ta = models.CharField(max_length=50, blank=True, help_text='Tamil name')

    class Meta:
        verbose_name = 'Rasi'
        verbose_name_plural = 'Rasis'

    def __str__(self):
        return self.rasi


class Star(models.Model):
    rasi = models.ForeignKey(Rasi, on_delete=models.CASCADE, related_name='stars')
    star = models.CharField(max_length=50)
    star_ta = models.CharField(max_length=50, blank=True, help_text='Tamil name')

    class Meta:
        unique_together = (('rasi', 'star'),)
        verbose_name = 'Star'
        verbose_name_plural = 'Stars'

    def __str__(self):
        return f"{self.star} ({self.rasi.rasi})"


class BirthDetail(models.Model):
    profile = models.OneToOneField(MemberProfile, on_delete=models.CASCADE, related_name='birth_detail')
    date_of_birth = models.DateField(null=True, blank=True)
    time_of_birth = models.TimeField(null=True, blank=True)
    place_of_birth = models.CharField(max_length=200, blank=True)
    rasi = models.ForeignKey(Rasi, on_delete=models.SET_NULL, null=True, blank=True)
    star = models.ForeignKey(Star, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Birth details for {self.profile}"

    
class Education(models.Model):
    education = models.CharField(max_length=100, unique=True)
    education_ta = models.CharField(max_length=100, blank=True, help_text='Tamil name')

    class Meta:
        verbose_name = 'Education'
        verbose_name_plural = 'Educations'

    def __str__(self):
        return self.education


class Profession(models.Model):
    profession = models.CharField(max_length=100, unique=True)
    profession_ta = models.CharField(max_length=100, blank=True, help_text='Tamil name')

    class Meta:
        verbose_name = 'Profession'
        verbose_name_plural = 'Professions'

    def __str__(self):
        return self.profession


class ProfessionalDetail(models.Model):
    profile = models.OneToOneField(MemberProfile, on_delete=models.CASCADE, related_name='professional_detail')
    education = models.ForeignKey(Education, on_delete=models.SET_NULL, null=True, blank=True)
    profession = models.ForeignKey(Profession, on_delete=models.SET_NULL, null=True, blank=True)
    monthly_income = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1000), MaxValueValidator(9999999)],
        help_text='Enter monthly income (min 4 digits, max 7 digits)'
    )

    def __str__(self):
        return f"Professional details for {self.profile}"
