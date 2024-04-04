from django import forms
from django.forms import ModelForm, TextInput, Textarea, DateInput, NumberInput, DateTimeInput, CheckboxInput
from .models import Client, Diagnosis, Kind, Service, Sale, Category, Branch, Specialization, Doctor, Schedule, Visit
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone

# При разработке приложения, использующего базу данных, чаще всего необходимо работать с формами, которые аналогичны моделям.
# В этом случае явное определение полей формы будет дублировать код, так как все поля уже описаны в модели.
# По этой причине Django предоставляет вспомогательный класс, который позволит вам создать класс Form по имеющейся модели
# атрибут fields - указание списка используемых полей, при fields = '__all__' - все поля
# атрибут widgets для указания собственный виджет для поля. Его значением должен быть словарь, ключами которого являются имена полей, а значениями — классы или экземпляры виджетов.

# Клиенты
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('full_name', 'birthday', 'sex', 'address', 'phone')
        widgets = {
            'full_name': TextInput(attrs={"size":"100"}),
            'birthday': DateInput(attrs={"type":"date"}),
            'address': TextInput(attrs={"size":"100"}),            
            'phone': TextInput(attrs={"size":"40", "type":"tel", "pattern": "+7-[0-9]{3}-[0-9]{3}-[0-9]{4}"}),            
        }
    # Метод-валидатор для поля birthday
    def clean_birthday(self):        
        if isinstance(self.cleaned_data['birthday'], datetime.date) == True:
            data = self.cleaned_data['birthday']
            # Проверка даты рождения не моложе 16 лет
            if data > timezone.now() - relativedelta(years=16):
                raise forms.ValidationError(_('Minimum age 16 years old'))
        else:
            raise forms.ValidationError(_('Wrong date and time format'))
        # Метод-валидатор обязательно должен вернуть очищенные данные, даже если не изменил их
        return data   

# Диагноз
class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = Diagnosis
        fields = ['diagnosis_details', 'date_diagnosis']
        widgets = {
            'date_diagnosis': DateInput(attrs={"type":"date"}),
            'diagnosis_details': Textarea(attrs={'cols': 100, 'rows': 8}),           
        }

# Тип услуги
class KindForm(forms.ModelForm):
    class Meta:
        model = Kind
        fields = ['kind_title',]
        widgets = {
            'kind_title': TextInput(attrs={"size":"100"}),            
        }

# Услуги
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ('kind', 'service_title', 'price')
        widgets = {
            'kind': forms.Select(),
            'service_title': TextInput(attrs={"size":"100"}),
            'price': NumberInput(attrs={"size":"10", "min": "1", "step": "1"}),
        }
        labels = {
            'kind': _('kind_title'),            
        }

# Продажа услуг
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ('service', 'price')
        widgets = {
            'service': forms.Select(),
            'price': NumberInput(attrs={"size":"10", "min": "1", "step": "1"}),
        }
        labels = {
            'service': _('service_title'),                        
        }

# Категория врачей (вторая, первая и высшая)
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_title',]
        widgets = {
            'category_title': TextInput(attrs={"size":"100"}),            
        }

# Отделение (травматология, хирургия...)
class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['branch_title',]
        widgets = {
            'branch_title': TextInput(attrs={"size":"100"}),            
        }

# Специализация врачей (кардиолог, отоларинголог, терапевт)
class SpecializationForm(forms.ModelForm):
    class Meta:
        model = Specialization
        fields = ['specialization_title',]
        widgets = {
            'specialization_title': TextInput(attrs={"size":"100"}),            
        }

# Врачи
class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ('full_name', 'category', 'branch', 'specialization', 'user')
        widgets = {
            'full_name': TextInput(attrs={"size":"100"}),
            'category': forms.Select(),            
            'branch': forms.Select(),            
            'specialization': forms.Select(),            
            'user': forms.Select(),            
        }
        labels = {
            'category': _('category_title'),            
            'branch': _('branch_title'),            
            'specialization': _('specialization_title'),            
            'user': _('email'),            
        }

# Расписание приема пациентов
class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ('week_day', 'time_schedule', 'doctor')
        widgets = {
            'time_schedule': TextInput(attrs={"size":"50"}),
            'doctor': forms.Select(),
        }
        labels = {
            'doctor': _('doctor'),            
        }

# Планируемые посещения
class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ('date_visit', 'client', 'doctor', 'visit_details')
        widgets = {
            'date_visit': DateTimeInput(format='%d/%m/%Y %H:%M:%S'),
            'client': forms.Select(),
            'doctor': forms.Select(),
            'visit_details': Textarea(attrs={'cols': 100, 'rows': 10}),                        
        }
        labels = {
            'client': _('schedule'),            
            'doctor': _('doctor'),            
        }

# Форма регистрации
class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')
