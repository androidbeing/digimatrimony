from django.contrib import admin
from .models import MemberProfile, Caste, Koottam, FamilyDetail, Rasi, Star, BirthDetail, Education, Profession, ProfessionalDetail

@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'mobile', 'gender', 'created_at')
    search_fields = ('mobile', 'user__first_name', 'user__last_name')
    list_filter = ('gender',)

@admin.register(Caste)
class CasteAdmin(admin.ModelAdmin):
    list_display = ('caste', 'caste_ta')
    search_fields = ('caste', 'caste_ta')

@admin.register(Koottam)
class KoottamAdmin(admin.ModelAdmin):
    list_display = ('subcaste', 'caste')
    search_fields = ('subcaste',)
    list_filter = ('caste',)

@admin.register(FamilyDetail)
class FamilyDetailAdmin(admin.ModelAdmin):
    list_display = ('profile', 'father_name', 'mother_name', 'caste', 'koottam')
    search_fields = ('profile__user__first_name', 'profile__user__last_name', 'father_name')

@admin.register(Rasi)
class RasiAdmin(admin.ModelAdmin):
    list_display = ('rasi', 'rasi_ta')

@admin.register(Star)
class StarAdmin(admin.ModelAdmin):
    list_display = ('star', 'rasi')
    list_filter = ('rasi',)

@admin.register(BirthDetail)
class BirthDetailAdmin(admin.ModelAdmin):
    list_display = ('profile', 'date_of_birth', 'time_of_birth', 'place_of_birth', 'rasi', 'star')
    search_fields = ('profile__user__first_name', 'profile__user__last_name')

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('education', 'education_ta')

@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    list_display = ('profession', 'profession_ta')

@admin.register(ProfessionalDetail)
class ProfessionalDetailAdmin(admin.ModelAdmin):
    list_display = ('profile', 'education', 'profession', 'monthly_income')
    search_fields = ('profile__user__first_name', 'profile__user__last_name')

# Register your models here.
