from django.contrib import admin
from .models import User, Student, Teacher, Group

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Group)