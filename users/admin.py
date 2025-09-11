from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from economy.models import StarBalance

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff', 'star_balance']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    
    def star_balance(self, obj):
        try:
            return obj.star_balance.balance
        except StarBalance.DoesNotExist:
            return 0
    star_balance.short_description = 'Stars Balance'