from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'username', 'user_id','is_blocked','created_date','updated_date']
    list_filter = ['id', 'name', 'username', 'user_id','is_blocked']


# Register your models here.
admin.site.register(User, UserAdmin)
