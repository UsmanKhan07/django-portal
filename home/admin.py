from django.contrib import admin
from home.models import Contact
from home.models import Questions
from home.models import Test

# Register your models here.
admin.site.register(Contact)
admin.site.register(Questions)
admin.site.register(Test)