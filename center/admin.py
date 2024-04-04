from django.contrib import admin

from .models import Client, Diagnosis, Kind, Service, Sale, Category, Branch, Specialization, Doctor, Schedule, Visit

# Добавление модели на главную страницу интерфейса администратора
admin.site.register(Client)
admin.site.register(Diagnosis)
admin.site.register(Kind)
admin.site.register(Service)
admin.site.register(Sale)
admin.site.register(Category)
admin.site.register(Branch)
admin.site.register(Specialization)
admin.site.register(Doctor)
admin.site.register(Schedule)
admin.site.register(Visit)

