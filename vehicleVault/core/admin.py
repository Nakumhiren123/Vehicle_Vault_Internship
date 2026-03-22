from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User
# Register your models here.
# admin.site.register(User)
def make_staff_admin(modeladmin, request, queryset):
    """Admin action: promote selected users to admin + grant staff access."""
    queryset.update(role='admin', is_staff=True, is_admin=True, is_active=True)
make_staff_admin.short_description = '⬆ Promote to Admin (grant /admin/ access)'
 
 
def revoke_admin(modeladmin, request, queryset):
    """Admin action: demote selected users back to regular users."""
    queryset.update(role='user', is_staff=False, is_admin=False)
revoke_admin.short_description = '⬇ Demote to User (revoke /admin/ access)'
 
 
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display   = ['email', 'first_name', 'last_name', 'role',
                      'gender', 'is_active', 'staff_badge', 'created_at']
    list_filter    = ['role', 'gender', 'is_active', 'is_staff']
    search_fields  = ['email', 'first_name', 'last_name']
    ordering       = ['-created_at']
    list_editable  = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    actions        = [make_staff_admin, revoke_admin]
 
    fieldsets = (
        ('Login',       {'fields': ('email', 'password')}),
        ('Personal',    {'fields': ('first_name', 'last_name', 'gender')}),
        ('Role & Access', {
            'fields': ('role', 'is_active', 'is_staff', 'is_admin', 'is_superuser'),
            'description': 'Set is_staff=True to allow this user to access /admin/'
        }),
        ('OTP',         {'fields': ('otp', 'otp_created_at'), 'classes': ('collapse',)}),
        ('Timestamps',  {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
 
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role',
                       'gender', 'is_staff', 'password1', 'password2'),
        }),
    )
 
    filter_horizontal = ()
 
    def staff_badge(self, obj):
        if obj.is_staff:
            return format_html(
                '<span style="background:#16a34a;color:#fff;padding:2px 8px;'
                'border-radius:10px;font-size:11px;">Admin</span>'
            )
        return format_html(
            '<span style="background:#e2e8f0;color:#64748b;padding:2px 8px;'
            'border-radius:10px;font-size:11px;">User</span>'
        )
    staff_badge.short_description = 'Admin Panel'
    