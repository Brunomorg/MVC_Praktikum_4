from django.contrib import admin
from .models import Person, Expense

admin.site.register(Person)
admin.site.register(Expense)