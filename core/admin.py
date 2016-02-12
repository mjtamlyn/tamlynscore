from django.contrib import admin

from custom_user.admin import EmailUserAdmin
from custom_user.forms import EmailUserCreationForm

from core.models import User, Country, Region, County, Club, Archer, Bowstyle, Round, Subround


class UserCreationForm(EmailUserCreationForm):
    class Meta(EmailUserCreationForm.Meta):
        fields = ('name', 'email')


class UserAdmin(EmailUserAdmin):
    list_display = ['name', 'email', 'is_staff']
    fieldsets = (
        (None, {'fields': ('name', 'email', 'password')}),
        ('Permissions', {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',
        )}),
        ('Important dates', {'fields': (
            'last_login', 'date_joined',
        )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'password1', 'password2')
        }),
    )
    add_form = UserCreationForm


class ArcherAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'club')
    list_filter = ('club',)


class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name')


class RoundAdmin(admin.ModelAdmin):
    filter_horizontal = ('subrounds',)
    list_display = ('name', 'total_arrows', 'subround_details', 'scoring_type')

    def get_queryset(self, request):
        return super(RoundAdmin, self).get_queryset(request).prefetch_related('subrounds')

    def total_arrows(self, instance):
        return sum(map(lambda s: s.arrows, instance.subrounds.all()))

    def subround_details(self, instance):
        return ', '.join(map(str, instance.subrounds.all()))


admin.site.register(Country)
admin.site.register(Region)
admin.site.register(County)
admin.site.register(Club, ClubAdmin)
admin.site.register(Archer, ArcherAdmin)
admin.site.register(Bowstyle)
admin.site.register(Round, RoundAdmin)
admin.site.register(Subround)
admin.site.register(User, UserAdmin)
