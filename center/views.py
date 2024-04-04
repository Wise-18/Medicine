from django.shortcuts import render, redirect

# Класс HttpResponse из пакета django.http, который позволяет отправить текстовое содержимое.
from django.http import HttpResponse, HttpResponseNotFound
# Конструктор принимает один обязательный аргумент – путь для перенаправления. Это может быть полный URL (например, 'https://www.yahoo.com/search/') или абсолютный путь без домена (например, '/search/').
from django.http import HttpResponseRedirect

from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

#from django.db.models import Max
#from django.db.models import Q

from datetime import datetime, timedelta

# Подключение моделей
from .models import Client, Diagnosis, Kind, Service, Sale, Category, Branch, Specialization, Doctor, Schedule, Visit
# Подключение форм
from .forms import ClientForm, DiagnosisForm, KindForm, ServiceForm, SaleForm, CategoryForm, BranchForm, SpecializationForm, DoctorForm, ScheduleForm, VisitForm, SignUpForm

from django.db.models import Sum
#from django.db import models

#import sys

#import math

from django.utils.translation import gettext_lazy as _

from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy

from django.contrib.auth import login as auth_login

#from django.db.models.query import QuerySet

from django.contrib.auth.decorators import user_passes_test

# Create your views here.
# Групповые ограничения
def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups, login_url='403')

###################################################################################################

# Стартовая страница 
def index(request):
    try:
        kind = Kind.objects.all().order_by('kind_title')
        service = Service.objects.all().order_by('kind__kind_title', 'service_title')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по типу услуги
                selected_item_kind = request.POST.get('item_kind')
                #print(selected_item_kind)
                if selected_item_kind != '-----':
                    kind_query = Kind.objects.filter(kind_title = selected_item_kind).only('id').all()
                    service = service.filter(kind_id__in = kind_query)
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    service = service.filter(service_title__contains = title_search)                
                return render(request, "index.html", {"service": service, "kind": kind, "selected_item_kind": selected_item_kind,  "title_search": title_search })    
            else:          
                return render(request, "index.html", {"service": service, "kind": kind, })
        else:
            return render(request, "index.html", {"service": service, "kind": kind,  })           
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Отчет 1
@login_required
@user_passes_test(lambda u: u.is_superuser)
def report_1(request):
    try:
        report = Visit.objects.raw("""
SELECT 1 as id, visit.date_visit, client.full_name AS client_full_name, doctor.full_name AS doctor_full_name
FROM visit LEFT JOIN client ON visit.client_id=client.id
LEFT JOIN doctor ON visit.doctor_id=doctor.id
GROUP BY client.full_name, visit.date_visit
""")
        return render(request, "report/report_1.html", {"report": report,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Отчет 2
@login_required
@user_passes_test(lambda u: u.is_superuser)
def report_2(request):
    try:
        where = ""
        start_date = datetime(datetime.now().year, 1, 1, 0, 0).strftime('%Y-%m-%d') 
        finish_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0).strftime('%Y-%m-%d') 
        selected_item_client = None
        client = Client.objects.all().order_by('full_name')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по дате
                start_date = request.POST.get("start_date")
                #print(start_date)
                finish_date = request.POST.get("finish_date")
                finish_date = str(datetime.strptime(finish_date, "%Y-%m-%d") + timedelta(days=1))
                #print(finish_date)
                if where != "":
                    where = where + " AND "
                where = "visit.date_visit>='" + start_date + "' AND visit.date_visit<='" + finish_date + "'"
                #print(where)
                finish_date = request.POST.get("finish_date")
                # Поиск по пациенту
                selected_item_client = request.POST.get('item_client')
                #print(selected_item_client)
                if selected_item_client != '-----':
                    if where != "":
                        where = where + " AND "
                    where = where + "client.full_name = '" + selected_item_client + "'"
                # Добавить ключевое слово WHERE 
                if where != "":
                    where = " WHERE " + where + " "              
                print(where)
        report = Visit.objects.raw("""
SELECT 1 as id, client.full_name AS client_full_name, doctor.full_name AS doctor_full_name, SUM(sale.price) AS sum_price
FROM visit LEFT JOIN client ON visit.client_id=client.id
LEFT JOIN doctor ON visit.doctor_id=doctor.id
LEFT JOIN sale ON visit.id=sale.visit_id
""" + where +
"""
GROUP BY doctor.full_name, client.full_name
""")
        return render(request, "report/report_2.html", {"report": report, "start_date": start_date, "finish_date": finish_date, "client": client, "selected_item_client": selected_item_client,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Отчет 3
@login_required
@user_passes_test(lambda u: u.is_superuser)
def report_3(request):
    try:
        where = ""
        start_date = datetime(datetime.now().year, 1, 1, 0, 0).strftime('%Y-%m-%d') 
        finish_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0).strftime('%Y-%m-%d') 
        selected_item_doctor = None
        doctor = Doctor.objects.all().order_by('full_name')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по дате
                start_date = request.POST.get("start_date")
                #print(start_date)
                finish_date = request.POST.get("finish_date")
                finish_date = str(datetime.strptime(finish_date, "%Y-%m-%d") + timedelta(days=1))
                #print(finish_date)
                if where != "":
                    where = where + " AND "
                where = "visit.date_visit>='" + start_date + "' AND visit.date_visit<='" + finish_date + "'"
                #print(where)
                finish_date = request.POST.get("finish_date")
                # Поиск по дактору
                selected_item_doctor = request.POST.get('item_doctor')
                #print(selected_item_doctor)
                if selected_item_doctor != '-----':
                    if where != "":
                        where = where + " AND "
                    where = where + "doctor.full_name = '" + selected_item_doctor + "'"
                # Добавить ключевое слово WHERE 
                if where != "":
                    where = " WHERE " + where + " "              
                print(where)

        report = Visit.objects.raw("""
SELECT 1 as id, visit.date_visit, client.full_name AS client_full_name, doctor.full_name AS doctor_full_name
FROM visit LEFT JOIN client ON visit.client_id=client.id
LEFT JOIN doctor ON visit.doctor_id=doctor.id
""" + where +
"""
ORDER BY visit.date_visit, client.full_name
""")
        return render(request, "report/report_3.html", {"report": report, "start_date": start_date, "finish_date": finish_date, "doctor": doctor, "selected_item_doctor": selected_item_doctor,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Отчет 4
@login_required
@user_passes_test(lambda u: u.is_superuser)
def report_4(request):
    try:
        where = ""
        selected_item_doctor = None
        doctor = Doctor.objects.all().order_by('full_name')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по дактору
                selected_item_doctor = request.POST.get('item_doctor')
                #print(selected_item_doctor)
                if selected_item_doctor != '-----':
                    if where != "":
                        where = where + " AND "
                    where = where + "doctor.full_name = '" + selected_item_doctor + "'"
                # Добавить ключевое слово WHERE 
                if where != "":
                    where = " WHERE " + where + " "              
                print(where)
        report = Visit.objects.raw("""
SELECT 1 as id, client.full_name AS client_full_name, doctor.full_name AS doctor_full_name
FROM visit LEFT JOIN client ON visit.client_id=client.id
LEFT JOIN doctor ON visit.doctor_id=doctor.id
""" + where +
"""
GROUP BY doctor.full_name, client.full_name
""")
        return render(request, "report/report_4.html", {"report": report, "doctor": doctor, "selected_item_doctor": selected_item_doctor,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def client_index(request):
    try:
        client = Client.objects.all().order_by('full_name')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    client = client.filter(full_name__contains = title_search)                
                return render(request, "client/index.html", {"client": client,  "title_search": title_search })    
            else:          
                return render(request, "client/index.html", {"client": client, })
        else:
            return render(request, "client/index.html", {"client": client, })       
        return render(request, "client/index.html", {"client": client,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Список для просмотра
@login_required
def client_list(request):
    try:
        # Получить id клиента, посетившего данного доктора
        doctor = Doctor.objects.get(user_id=request.user.id)        
        client_query = Visit.objects.filter(doctor_id=doctor.id).only('client_id').all()
        # Получить только данных лиентов
        client = Client.objects.filter(id__in = client_query).order_by('full_name')
        #client = Client.objects.all().order_by('full_name')
        return render(request, "client/list.html", {"client": client,})
    except Exception as exception:
        print(exception)
        return render(request, "client/list.html", {"client": None,})
        #return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def client_create(request):
    try:
        if request.method == "POST":
            client = Client()
            client.full_name = request.POST.get("full_name")
            client.birthday = request.POST.get("birthday")
            client.sex = request.POST.get("sex")
            client.address = request.POST.get("address")
            client.phone = request.POST.get("phone")
            clientform = ClientForm(request.POST)
            if clientform.is_valid():
                client.save()
                return HttpResponseRedirect(reverse('client_index'))
            else:
                return render(request, "client/create.html", {"form": clientform})
        else:        
            clientform = ClientForm(initial={ 'birthday': datetime.now().strftime('%Y-%m-%d')})
            return render(request, "client/create.html", {"form": clientform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def client_edit(request, id):
    try:
        client = Client.objects.get(id=id)
        if request.method == "POST":
            client.full_name = request.POST.get("full_name")
            client.birthday = request.POST.get("birthday")
            client.sex = request.POST.get("sex")
            client.address = request.POST.get("address")
            client.phone = request.POST.get("phone")
            clientform = ClientForm(request.POST)
            if clientform.is_valid():
                client.save()
                return HttpResponseRedirect(reverse('client_index'))
            else:
                return render(request, "client/edit.html", {"form": clientform})
        else:
            # Загрузка начальных данных
            clientform = ClientForm(initial={'full_name': client.full_name, 'birthday': client.birthday.strftime('%Y-%m-%d'), 'sex': client.sex, 'address': client.address, 'phone': client.phone, })
            return render(request, "client/edit.html", {"form": clientform})
    except Client.DoesNotExist:
        return HttpResponseNotFound("<h2>Client not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def client_delete(request, id):
    try:
        client = Client.objects.get(id=id)
        client.delete()
        return HttpResponseRedirect(reverse('client_index'))
    except Client.DoesNotExist:
        return HttpResponseNotFound("<h2>Client not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def client_read(request, id):
    try:
        client = Client.objects.get(id=id) 
        return render(request, "client/read.html", {"client": client})
    except Client.DoesNotExist:
        return HttpResponseNotFound("<h2>Client not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def diagnosis_index(request, client_id):
    try:
        client = Client.objects.get(id=client_id)
        diagnosis = Diagnosis.objects.filter(client_id=client_id)
        return render(request, "diagnosis/index.html", {"client": client, "diagnosis": diagnosis, "client_id": client_id,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def diagnosis_create(request, client_id):
    try:
        if request.method == "POST":
            diagnosis = Diagnosis()
            diagnosis.client_id = client_id
            diagnosis.date_diagnosis = request.POST.get("date_diagnosis")
            diagnosis.diagnosis_details = request.POST.get("diagnosis_details")
            diagnosisform = DiagnosisForm(request.POST)
            if diagnosisform.is_valid():
                diagnosis.save()
                return HttpResponseRedirect(reverse('diagnosis_index', args=(client_id,)))
            else:
                return render(request, "diagnosis/create.html", {"form": diagnosisform, "client_id": client_id})
        else:        
            diagnosisform = DiagnosisForm(initial={ 'date_diagnosis': datetime.now().strftime('%Y-%m-%d')})
            return render(request, "diagnosis/create.html", {"form": diagnosisform, "client_id": client_id})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def diagnosis_edit(request, id, client_id):
    try:
        diagnosis = Diagnosis.objects.get(id=id)
        if request.method == "POST":
            diagnosis.client_id = client_id
            diagnosis.date_diagnosis = request.POST.get("date_diagnosis")
            diagnosis.diagnosis_details = request.POST.get("diagnosis_details")
            diagnosisform = DiagnosisForm(request.POST)
            if diagnosisform.is_valid():
                diagnosis.save()
                return HttpResponseRedirect(reverse('diagnosis_index', args=(client_id,)))
            else:
                return render(request, "diagnosis/edit.html", {"form": diagnosisform, "client_id": client_id})
        else:
            # Загрузка начальных данных
            diagnosisform = DiagnosisForm(initial={'client': diagnosis.client, 'date_diagnosis': diagnosis.date_diagnosis.strftime('%Y-%m-%d'), 'diagnosis_details': diagnosis.diagnosis_details, })
            return render(request, "diagnosis/edit.html", {"form": diagnosisform, "client_id": client_id})
    except Diagnosis.DoesNotExist:
        return HttpResponseNotFound("<h2>Diagnosis not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def diagnosis_delete(request, id, client_id):
    try:
        diagnosis = Diagnosis.objects.get(id=id)
        diagnosis.delete()
        return HttpResponseRedirect(reverse('diagnosis_index', args=(client_id,)))
    except Diagnosis.DoesNotExist:
        return HttpResponseNotFound("<h2>Diagnosis not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def diagnosis_read(request, id, client_id):
    try:
        diagnosis = Diagnosis.objects.get(id=id) 
        return render(request, "diagnosis/read.html", {"diagnosis": diagnosis, "client_id": client_id})
    except Diagnosis.DoesNotExist:
        return HttpResponseNotFound("<h2>Diagnosis not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def kind_index(request):
    try:
        kind = Kind.objects.all().order_by('kind_title')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    kind = kind.filter(kind_title__contains = title_search)                
                return render(request, "kind/index.html", {"kind": kind,  "title_search": title_search })    
            else:          
                return render(request, "kind/index.html", {"kind": kind, })
        else:
            return render(request, "kind/index.html", {"kind": kind, })       
        return render(request, "kind/index.html", {"kind": kind,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def kind_create(request):
    try:
        if request.method == "POST":
            kind = Kind()
            kind.kind_title = request.POST.get("kind_title")
            kindform = KindForm(request.POST)
            if kindform.is_valid():
                kind.save()
                return HttpResponseRedirect(reverse('kind_index'))
            else:
                return render(request, "kind/create.html", {"form": kindform})
        else:        
            kindform = KindForm()
            return render(request, "kind/create.html", {"form": kindform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def kind_edit(request, id):
    try:
        kind = Kind.objects.get(id=id)
        if request.method == "POST":
            kind.kind_title = request.POST.get("kind_title")
            kindform = KindForm(request.POST)
            if kindform.is_valid():
                kind.save()
                return HttpResponseRedirect(reverse('kind_index'))
            else:
                return render(request, "kind/edit.html", {"form": kindform})
        else:
            # Загрузка начальных данных
            kindform = KindForm(initial={'kind_title': kind.kind_title, })
            return render(request, "kind/edit.html", {"form": kindform})
    except Kind.DoesNotExist:
        return HttpResponseNotFound("<h2>Kind not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def kind_delete(request, id):
    try:
        kind = Kind.objects.get(id=id)
        kind.delete()
        return HttpResponseRedirect(reverse('kind_index'))
    except Kind.DoesNotExist:
        return HttpResponseNotFound("<h2>Kind not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def kind_read(request, id):
    try:
        kind = Kind.objects.get(id=id) 
        return render(request, "kind/read.html", {"kind": kind})
    except Kind.DoesNotExist:
        return HttpResponseNotFound("<h2>Kind not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def service_index(request):
    try:
        service = Service.objects.all().order_by('service_title')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    service = service.filter(service_title__contains = title_search)                
                return render(request, "service/index.html", {"service": service,  "title_search": title_search })    
            else:          
                return render(request, "service/index.html", {"service": service, })
        else:
            return render(request, "service/index.html", {"service": service, })       
        return render(request, "service/index.html", {"service": service,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def service_create(request):
    try:
        if request.method == "POST":
            service = Service()
            service.kind = Kind.objects.filter(id=request.POST.get("kind")).first()
            service.service_title = request.POST.get("service_title")
            service.price = request.POST.get("price")
            serviceform = ServiceForm(request.POST)
            if serviceform.is_valid():
                service.save()
                return HttpResponseRedirect(reverse('service_index'))
            else:
                return render(request, "service/create.html", {"form": serviceform})
        else:        
            serviceform = ServiceForm()
            return render(request, "service/create.html", {"form": serviceform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def service_edit(request, id):
    try:
        service = Service.objects.get(id=id)
        if request.method == "POST":
            service.kind = Kind.objects.filter(id=request.POST.get("kind")).first()
            service.service_title = request.POST.get("service_title")
            service.price = request.POST.get("price")
            serviceform = ServiceForm(request.POST)
            if serviceform.is_valid():
                service.save()
                return HttpResponseRedirect(reverse('service_index'))
            else:
                return render(request, "service/edit.html", {"form": serviceform})
        else:
            # Загрузка начальных данных
            serviceform = ServiceForm(initial={'kind': service.kind, 'service_title': service.service_title, 'price': service.price, })
            return render(request, "service/edit.html", {"form": serviceform})
    except Service.DoesNotExist:
        return HttpResponseNotFound("<h2>Service not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def service_delete(request, id):
    try:
        service = Service.objects.get(id=id)
        service.delete()
        return HttpResponseRedirect(reverse('service_index'))
    except Service.DoesNotExist:
        return HttpResponseNotFound("<h2>Service not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def service_read(request, id):
    try:
        service = Service.objects.get(id=id) 
        return render(request, "service/read.html", {"service": service})
    except Service.DoesNotExist:
        return HttpResponseNotFound("<h2>Service not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def category_index(request):
    try:
        category = Category.objects.all().order_by('category_title')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    category = category.filter(category_title__contains = title_search)                
                return render(request, "category/index.html", {"category": category,  "title_search": title_search })    
            else:          
                return render(request, "category/index.html", {"category": category, })
        else:
            return render(request, "category/index.html", {"category": category, })       
        return render(request, "category/index.html", {"category": category,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def category_create(request):
    try:
        if request.method == "POST":
            category = Category()
            category.category_title = request.POST.get("category_title")
            categoryform = CategoryForm(request.POST)
            if categoryform.is_valid():
                category.save()
                return HttpResponseRedirect(reverse('category_index'))
            else:
                return render(request, "category/create.html", {"form": categoryform})
        else:        
            categoryform = CategoryForm()
            return render(request, "category/create.html", {"form": categoryform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def category_edit(request, id):
    try:
        category = Category.objects.get(id=id)
        if request.method == "POST":
            category.category_title = request.POST.get("category_title")
            categoryform = CategoryForm(request.POST)
            if categoryform.is_valid():
                category.save()
                return HttpResponseRedirect(reverse('category_index'))
            else:
                return render(request, "category/edit.html", {"form": categoryform})
        else:
            # Загрузка начальных данных
            categoryform = CategoryForm(initial={'category_title': category.category_title, })
            return render(request, "category/edit.html", {"form": categoryform})
    except Category.DoesNotExist:
        return HttpResponseNotFound("<h2>Category not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def category_delete(request, id):
    try:
        category = Category.objects.get(id=id)
        category.delete()
        return HttpResponseRedirect(reverse('category_index'))
    except Category.DoesNotExist:
        return HttpResponseNotFound("<h2>Category not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def category_read(request, id):
    try:
        category = Category.objects.get(id=id) 
        return render(request, "category/read.html", {"category": category})
    except Category.DoesNotExist:
        return HttpResponseNotFound("<h2>Category not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def branch_index(request):
    try:
        branch = Branch.objects.all().order_by('branch_title')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    branch = branch.filter(branch_title__contains = title_search)                
                return render(request, "branch/index.html", {"branch": branch,  "title_search": title_search })    
            else:          
                return render(request, "branch/index.html", {"branch": branch, })
        else:
            return render(request, "branch/index.html", {"branch": branch, })       
        return render(request, "branch/index.html", {"branch": branch,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def branch_create(request):
    try:
        if request.method == "POST":
            branch = Branch()
            branch.branch_title = request.POST.get("branch_title")
            branchform = BranchForm(request.POST)
            if branchform.is_valid():
                branch.save()
                return HttpResponseRedirect(reverse('branch_index'))
            else:
                return render(request, "branch/create.html", {"form": branchform})
        else:        
            branchform = BranchForm()
            return render(request, "branch/create.html", {"form": branchform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def branch_edit(request, id):
    try:
        branch = Branch.objects.get(id=id)
        if request.method == "POST":
            branch.branch_title = request.POST.get("branch_title")
            branchform = BranchForm(request.POST)
            if branchform.is_valid():
                branch.save()
                return HttpResponseRedirect(reverse('branch_index'))
            else:
                return render(request, "branch/edit.html", {"form": branchform})
        else:
            # Загрузка начальных данных
            branchform = BranchForm(initial={'branch_title': branch.branch_title, })
            return render(request, "branch/edit.html", {"form": branchform})
    except Branch.DoesNotExist:
        return HttpResponseNotFound("<h2>Branch not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def branch_delete(request, id):
    try:
        branch = Branch.objects.get(id=id)
        branch.delete()
        return HttpResponseRedirect(reverse('branch_index'))
    except Branch.DoesNotExist:
        return HttpResponseNotFound("<h2>Branch not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def branch_read(request, id):
    try:
        branch = Branch.objects.get(id=id) 
        return render(request, "branch/read.html", {"branch": branch})
    except Branch.DoesNotExist:
        return HttpResponseNotFound("<h2>Branch not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def specialization_index(request):
    try:
        specialization = Specialization.objects.all().order_by('specialization_title')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    specialization = specialization.filter(specialization_title__contains = title_search)                
                return render(request, "specialization/index.html", {"specialization": specialization,  "title_search": title_search })    
            else:          
                return render(request, "specialization/index.html", {"specialization": specialization, })
        else:
            return render(request, "specialization/index.html", {"specialization": specialization, })       
        return render(request, "specialization/index.html", {"specialization": specialization,})

    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def specialization_create(request):
    try:
        if request.method == "POST":
            specialization = Specialization()
            specialization.specialization_title = request.POST.get("specialization_title")
            specializationform = SpecializationForm(request.POST)
            if specializationform.is_valid():
                specialization.save()
                return HttpResponseRedirect(reverse('specialization_index'))
            else:
                return render(request, "specialization/create.html", {"form": specializationform})
        else:        
            specializationform = SpecializationForm()
            return render(request, "specialization/create.html", {"form": specializationform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def specialization_edit(request, id):
    try:
        specialization = Specialization.objects.get(id=id)
        if request.method == "POST":
            specialization.specialization_title = request.POST.get("specialization_title")
            specializationform = SpecializationForm(request.POST)
            if specializationform.is_valid():
                specialization.save()
                return HttpResponseRedirect(reverse('specialization_index'))
            else:
                return render(request, "specialization/edit.html", {"form": specializationform})
        else:
            # Загрузка начальных данных
            specializationform = SpecializationForm(initial={'specialization_title': specialization.specialization_title, })
            return render(request, "specialization/edit.html", {"form": specializationform})
    except Specialization.DoesNotExist:
        return HttpResponseNotFound("<h2>Specialization not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def specialization_delete(request, id):
    try:
        specialization = Specialization.objects.get(id=id)
        specialization.delete()
        return HttpResponseRedirect(reverse('specialization_index'))
    except Specialization.DoesNotExist:
        return HttpResponseNotFound("<h2>Specialization not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def specialization_read(request, id):
    try:
        specialization = Specialization.objects.get(id=id) 
        return render(request, "specialization/read.html", {"specialization": specialization})
    except Specialization.DoesNotExist:
        return HttpResponseNotFound("<h2>Specialization not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def doctor_index(request):
    try:
        doctor = Doctor.objects.all().order_by('full_name')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    doctor = doctor.filter(full_name__contains = title_search)                
                return render(request, "doctor/index.html", {"doctor": doctor,  "title_search": title_search })    
            else:          
                return render(request, "doctor/index.html", {"doctor": doctor, })
        else:
            return render(request, "doctor/index.html", {"doctor": doctor, })       
        return render(request, "doctor/index.html", {"doctor": doctor,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def doctor_create(request):
    try:
        if request.method == "POST":
            doctor = Doctor()
            doctor.full_name = request.POST.get("full_name")
            doctor.category = Category.objects.filter(id=request.POST.get("category")).first()
            doctor.branch = Branch.objects.filter(id=request.POST.get("branch")).first()
            doctor.specialization = Specialization.objects.filter(id=request.POST.get("specialization")).first()
            doctor.user = User.objects.filter(id=request.POST.get("user")).first()
            doctorform = DoctorForm(request.POST)
            if doctorform.is_valid():
                doctor.save()
                return HttpResponseRedirect(reverse('doctor_index'))
            else:
                return render(request, "doctor/create.html", {"form": doctorform})
        else:        
            doctorform = DoctorForm()
            return render(request, "doctor/create.html", {"form": doctorform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def doctor_edit(request, id):
    try:
        doctor = Doctor.objects.get(id=id)
        if request.method == "POST":
            doctor.full_name = request.POST.get("full_name")
            doctor.category = Category.objects.filter(id=request.POST.get("category")).first()
            doctor.branch = Branch.objects.filter(id=request.POST.get("branch")).first()
            doctor.specialization = Specialization.objects.filter(id=request.POST.get("specialization")).first()
            doctor.user = User.objects.filter(id=request.POST.get("user")).first()
            doctorform = DoctorForm(request.POST)
            if doctorform.is_valid():
                doctor.save()
                return HttpResponseRedirect(reverse('doctor_index'))
            else:
                return render(request, "doctor/edit.html", {"form": doctorform})
        else:
            # Загрузка начальных данных
            doctorform = DoctorForm(initial={'full_name': doctor.full_name, 'category': doctor.category, 'branch': doctor.branch, 'specialization': doctor.specialization, 'user': doctor.user, })
            return render(request, "doctor/edit.html", {"form": doctorform})
    except Doctor.DoesNotExist:
        return HttpResponseNotFound("<h2>Doctor not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def doctor_delete(request, id):
    try:
        doctor = Doctor.objects.get(id=id)
        doctor.delete()
        return HttpResponseRedirect(reverse('doctor_index'))
    except Doctor.DoesNotExist:
        return HttpResponseNotFound("<h2>Doctor not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def doctor_read(request, id):
    try:
        doctor = Doctor.objects.get(id=id) 
        return render(request, "doctor/read.html", {"doctor": doctor})
    except Doctor.DoesNotExist:
        return HttpResponseNotFound("<h2>Doctor not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def schedule_index(request):
    try:
        schedule = Schedule.objects.all()
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    doctor_query = Doctor.objects.filter(full_name__contains = title_search).only('id').all()
                    schedule = schedule.filter(doctor_id__in = doctor_query)
                return render(request, "schedule/index.html", {"schedule": schedule,  "title_search": title_search })    
            else:          
                return render(request, "schedule/index.html", {"schedule": schedule, })
        else:
            return render(request, "schedule/index.html", {"schedule": schedule, })       
        return render(request, "schedule/index.html", {"schedule": schedule,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Список для просмотра
@login_required
def schedule_list(request):
    try:
        #print(request.user.id)
        # Расписание только для текущего пользователя
        doctor = Doctor.objects.get(user_id=request.user.id)
        schedule = Schedule.objects.filter(doctor_id=doctor.id).order_by('week_day')
        return render(request, "schedule/list.html", {"schedule": schedule,})
    except Exception as exception:
        print(exception)
        return render(request, "schedule/list.html", {"schedule": None,})
        #return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def schedule_create(request):
    try:
        if request.method == "POST":
            schedule = Schedule()
            schedule.week_day = request.POST.get("week_day")
            schedule.time_schedule = request.POST.get("time_schedule")
            schedule.doctor = Doctor.objects.filter(id=request.POST.get("doctor")).first()
            scheduleform = ScheduleForm(request.POST)
            if scheduleform.is_valid():
                schedule.save()
                return HttpResponseRedirect(reverse('schedule_index'))
            else:
                return render(request, "schedule/create.html", {"form": scheduleform})
        else:        
            scheduleform = ScheduleForm()
            return render(request, "schedule/create.html", {"form": scheduleform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def schedule_edit(request, id):
    try:
        schedule = Schedule.objects.get(id=id)
        if request.method == "POST":
            schedule.week_day = request.POST.get("week_day")
            schedule.time_schedule = request.POST.get("time_schedule")
            schedule.doctor = Doctor.objects.filter(id=request.POST.get("doctor")).first()
            scheduleform = ScheduleForm(request.POST)
            if scheduleform.is_valid():
                schedule.save()
                return HttpResponseRedirect(reverse('schedule_index'))
            else:
                return render(request, "schedule/edit.html", {"form": scheduleform})
        else:
            # Загрузка начальных данных
            scheduleform = ScheduleForm(initial={'week_day': schedule.week_day, 'time_schedule': schedule.time_schedule, 'doctor': schedule.doctor, })
            return render(request, "schedule/edit.html", {"form": scheduleform})
    except Schedule.DoesNotExist:
        return HttpResponseNotFound("<h2>Schedule not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def schedule_delete(request, id):
    try:
        schedule = Schedule.objects.get(id=id)
        schedule.delete()
        return HttpResponseRedirect(reverse('schedule_index'))
    except Schedule.DoesNotExist:
        return HttpResponseNotFound("<h2>Schedule not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def schedule_read(request, id):
    try:
        schedule = Schedule.objects.get(id=id) 
        return render(request, "schedule/read.html", {"schedule": schedule})
    except Schedule.DoesNotExist:
        return HttpResponseNotFound("<h2>Schedule not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def visit_index(request):
    try:
        visit = Visit.objects.all().order_by('date_visit')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    from django.db.models import Q
                    doctor_query = Doctor.objects.filter(full_name__contains = title_search).only('id').all()
                    client_query = Client.objects.filter(full_name__contains = title_search).only('id').all()
                    visit = visit.filter(Q(client_id__in = client_query) | Q(doctor_id__in = doctor_query))
                return render(request, "visit/index.html", {"visit": visit,  "title_search": title_search })    
            else:          
                return render(request, "visit/index.html", {"visit": visit, })
        else:
            return render(request, "visit/index.html", {"visit": visit, })       
        return render(request, "visit/index.html", {"visit": visit,})

    except Exception as exception:
        print(exception)
        return HttpResponse(exception)
    
# Список для просмотра
@login_required
def visit_list(request):
    try:
        #print(request.user.id)
        # Посещение только для текущего пользователя
        doctor = Doctor.objects.get(user_id=request.user.id)
        visit = Visit.objects.filter(doctor_id=doctor.id).order_by('date_visit')
        return render(request, "visit/list.html", {"visit": visit,})
    except Exception as exception:
        print(exception)
        return render(request, "visit/list.html", {"visit": None,})
        #return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def visit_create(request):
    try:
        if request.method == "POST":
            visit = Visit()
            visit.date_visit = request.POST.get("date_visit")
            visit.client = Client.objects.filter(id=request.POST.get("client")).first()
            visit.doctor = Doctor.objects.filter(id=request.POST.get("doctor")).first()
            visit.visit_details = request.POST.get("visit_details")
            visitform = VisitForm(request.POST)
            if visitform.is_valid():
                visit.save()
                return HttpResponseRedirect(reverse('visit_index'))
            else:
                return render(request, "visit/create.html", {"form": visitform})
        else:        
            visitform = VisitForm(initial={ 'date_visit': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
            return render(request, "visit/create.html", {"form": visitform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def visit_edit(request, id):
    try:
        visit = Visit.objects.get(id=id)
        if request.method == "POST":
            visit.date_visit = request.POST.get("date_visit")
            visit.client = Client.objects.filter(id=request.POST.get("client")).first()
            visit.doctor = Doctor.objects.filter(id=request.POST.get("doctor")).first()
            visit.visit_details = request.POST.get("visit_details")
            visitform = VisitForm(request.POST)
            if visitform.is_valid():
                visit.save()
                return HttpResponseRedirect(reverse('visit_index'))
            else:
                return render(request, "visit/edit.html", {"form": visitform})
        else:
            # Загрузка начальных данных
            visitform = VisitForm(initial={'date_visit': visit.date_visit.strftime('%Y-%m-%d %H:%M:%S'), 'client': visit.client, 'doctor': visit.doctor, 'visit_details': visit.visit_details, })
            return render(request, "visit/edit.html", {"form": visitform})
    except Visit.DoesNotExist:
        return HttpResponseNotFound("<h2>Visit not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def visit_delete(request, id):
    try:
        visit = Visit.objects.get(id=id)
        visit.delete()
        return HttpResponseRedirect(reverse('visit_index'))
    except Visit.DoesNotExist:
        return HttpResponseNotFound("<h2>Visit not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def visit_read(request, id):
    try:
        visit = Visit.objects.get(id=id) 
        return render(request, "visit/read.html", {"visit": visit})
    except Visit.DoesNotExist:
        return HttpResponseNotFound("<h2>Visit not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def sale_index(request, visit_id):
    try:
        visit = Visit.objects.get(id=visit_id)
        sale = Sale.objects.filter(visit_id=visit_id)
        return render(request, "sale/index.html", {"sale": sale, "visit": visit, "visit_id": visit_id,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)
    
# Список для просмотра
@login_required
def sale_list(request):
    try:
        # Получить id визитов для данного доктора
        doctor = Doctor.objects.get(user_id=request.user.id)    
        visit_query = Visit.objects.filter(doctor_id=doctor.id).only('doctor_id').all()        
        # Получить соответствующие визитам продажи
        sale = Sale.objects.filter(visit_id__in = visit_query).order_by('visit__date_visit')
        for s in sale:
            print(s.visit)
            print(s.service)
            print(s.price)
        total = Sale.objects.filter(visit_id__in = visit_query).aggregate(Sum('price'))
        #print(total['price__sum'])
        return render(request, "sale/list.html", {"sale": sale, "total": total,})
    except Exception as exception:
        print(exception)
        return render(request, "sale/list.html", {"sale": None, "total": None,})
        #return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def sale_create(request, visit_id):
    try:
        if request.method == "POST":
            sale = Sale()
            sale.visit_id = visit_id
            sale.service = Service.objects.filter(id=request.POST.get("service")).first()
            sale.price = request.POST.get("price")
            saleform = SaleForm(request.POST)
            if saleform.is_valid():
                sale.save()
                return HttpResponseRedirect(reverse('sale_index', args=(visit_id,)))
            else:
                return render(request, "sale/create.html", {"form": saleform, "visit_id": visit_id})
        else:        
            saleform = SaleForm(initial={ 'date_sale': datetime.now().strftime('%Y-%m-%d')})
            return render(request, "sale/create.html", {"form": saleform, "visit_id": visit_id})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def sale_edit(request, id, visit_id):
    try:
        sale = Sale.objects.get(id=id)
        if request.method == "POST":
            sale.visit_id = visit_id
            sale.service = Service.objects.filter(id=request.POST.get("service")).first()
            sale.price = request.POST.get("price")
            saleform = SaleForm(request.POST)
            if saleform.is_valid():
                sale.save()
                return HttpResponseRedirect(reverse('sale_index', args=(visit_id,)))
            else:
                return render(request, "sale/edit.html", {"form": saleform, "visit_id": visit_id})
        else:
            # Загрузка начальных данных
            saleform = SaleForm(initial={'service': sale.service, 'price': sale.price, })
            return render(request, "sale/edit.html", {"form": saleform, "visit_id": visit_id})
    except Sale.DoesNotExist:
        return HttpResponseNotFound("<h2>Sale not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def sale_delete(request, id, visit_id):
    try:
        sale = Sale.objects.get(id=id)
        sale.delete()
        return HttpResponseRedirect(reverse('sale_index', args=(visit_id,)))
    except Sale.DoesNotExist:
        return HttpResponseNotFound("<h2>Sale not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def sale_read(request, id, visit_id):
    try:
        sale = Sale.objects.get(id=id) 
        return render(request, "sale/read.html", {"sale": sale, "visit_id": visit_id})
    except Sale.DoesNotExist:
        return HttpResponseNotFound("<h2>Sale not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Регистрационная форма 
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('index')
            #return render(request, 'registration/register_done.html', {'new_user': user})
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# Изменение данных пользователя
@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email',)
    template_name = 'registration/my_account.html'
    success_url = reverse_lazy('index')
    #success_url = reverse_lazy('my_account')
    def get_object(self):
        return self.request.user

# Выход
from django.contrib.auth import logout
def logoutUser(request):
    logout(request)
    return render(request, "index.html")

