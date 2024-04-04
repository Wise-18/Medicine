from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User

# Модели отображают информацию о данных, с которыми вы работаете.
# Они содержат поля и поведение ваших данных.
# Обычно одна модель представляет одну таблицу в базе данных.
# Каждая модель это класс унаследованный от django.db.models.Model.
# Атрибут модели представляет поле в базе данных.
# Django предоставляет автоматически созданное API для доступа к данным

# choices (список выбора). Итератор (например, список или кортеж) 2-х элементных кортежей,
# определяющих варианты значений для поля.
# При определении, виджет формы использует select вместо стандартного текстового поля
# и ограничит значение поля указанными значениями.

# Читабельное имя поля (метка, label). Каждое поле, кроме ForeignKey, ManyToManyField и OneToOneField,
# первым аргументом принимает необязательное читабельное название.
# Если оно не указано, Django самостоятельно создаст его, используя название поля, заменяя подчеркивание на пробел.
# null - Если True, Django сохранит пустое значение как NULL в базе данных. По умолчанию - False.
# blank - Если True, поле не обязательно и может быть пустым. По умолчанию - False.
# Это не то же что и null. null относится к базе данных, blank - к проверке данных.
# Если поле содержит blank=True, форма позволит передать пустое значение.
# При blank=False - поле обязательно.


# Клиенты 
class Client(models.Model):
    SEX_CHOICES = (
        ('М','М'),
        ('Ж', 'Ж'),
    )    
    full_name = models.CharField(_('full_name'), max_length=128)
    birthday = models.DateTimeField(_('birthday'))
    sex = models.CharField(_('sex'), max_length=1, choices=SEX_CHOICES, default='М')
    address = models.CharField(_('address'), max_length=96)   
    phone = models.CharField(_('phone'), max_length=64)    
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'client'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['full_name']),
        ]
        # Сортировка по умолчанию
        ordering = ['full_name']
    def __str__(self):
        # Вывод 
        return "{}, {}".format(self.full_name, self.birthday.strftime('%d.%m.%Y'))

# Диагноз
class Diagnosis(models.Model):
    date_diagnosis = models.DateTimeField(_('date_diagnosis'))
    client = models.ForeignKey(Client, related_name='diagnosis_client', on_delete=models.CASCADE)
    diagnosis_details = models.TextField(_('diagnosis_details'), blank=True, null=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'diagnosis'
        # Сортировка по умолчанию
        ordering = ['client']
    def __str__(self):
        # Вывод удобочитаемой строки
        return "{}: {}".format(self.date_diagnosis.strftime('%d.%m.%Y'), self.diagnosis_details)

# Тип услуги
class Kind(models.Model):
    kind_title = models.CharField(_('kind_title'), max_length=128, unique=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'kind'
        # Сортировка по умолчанию
        ordering = ['kind_title']
    def __str__(self):
        # Вывод удобочитаемой строки
        return "{}".format(self.kind_title)

# Услуги 
class Service(models.Model):
    kind = models.ForeignKey(Kind, related_name='service_kind', on_delete=models.CASCADE)
    service_title = models.CharField(_('service_title'), max_length=256)
    price = models.DecimalField(_('service_price'), max_digits=9, decimal_places=2)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'service'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['kind', 'service_title']),
        ]
        # Сортировка по умолчанию
        ordering = ['service_title']
    def __str__(self):
        # Вывод удобочитаемой строки 
        return "{}: {}".format(self.service_title, self.price)

# Категория врачей (вторая, первая и высшая)
class Category(models.Model):
    category_title = models.CharField(_('category_title'), max_length=255, unique=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'category'
        # Сортировка по умолчанию
        ordering = ['category_title']
    def __str__(self):
        # Вывод удобочитаемой строки
        return "{}".format(self.category_title)

# Отделение (травматология, хирургия...)
class Branch(models.Model):
    branch_title = models.CharField(_('branch_title'), max_length=255, unique=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'branch'
        # Сортировка по умолчанию
        ordering = ['branch_title']
    def __str__(self):
        # Вывод удобочитаемой строки
        return "{}".format(self.branch_title)

# Специализация врачей (кардиолог, отоларинголог, терапевт)
class Specialization(models.Model):
    specialization_title = models.CharField(_('specialization_title'), max_length=255, unique=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'specialization'
        # Сортировка по умолчанию
        ordering = ['specialization_title']
    def __str__(self):
        # Вывод удобочитаемой строки
        return "{}".format(self.specialization_title)

# Врачи 
class Doctor(models.Model):
    full_name = models.CharField(_('full_name'), max_length=128)
    category = models.ForeignKey(Category, related_name='doctor_category', on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, related_name='branch_category', on_delete=models.CASCADE)
    specialization = models.ForeignKey(Specialization, related_name='doctor_specialization', on_delete=models.CASCADE)
    user = models.OneToOneField(User, related_name='doctor_user', on_delete=models.PROTECT) 
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'doctor'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['full_name']),
        ]
        # Сортировка по умолчанию
        ordering = ['full_name']
    def __str__(self):
        # Вывод удобочитаемой строки 
        return "{}, {}".format(self.full_name, self.specialization)

# Расписание приема пациентов
class Schedule(models.Model):
    WEEK_DAY_CHOICES = (
        (_('monday') ,_('monday')),
        (_('tuesday') ,_('tuesday')),
        (_('wednesday') ,_('wednesday')),
        (_('thursday') ,_('thursday')),
        (_('friday') ,_('friday')),
        (_('saturday') ,_('saturday')),
        (_('sunday') ,_('sunday')),
    )           
    week_day = models.CharField(_('week_day'), max_length=16, choices=WEEK_DAY_CHOICES, default=_('monday'))
    time_schedule = models.CharField(_('time_schedule'), max_length=64)
    doctor = models.ForeignKey(Doctor, related_name='schedule_doctor', on_delete=models.CASCADE)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'schedule'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['doctor']),
        ]
        # Сортировка по умолчанию
        ordering = ['week_day']
    def __str__(self):
        # Вывод удобочитаемой строки 
        return "{}: {}, {}".format(self.doctor, self.week_day, self.time_schedule)

# Планируемые посещения
class Visit(models.Model):
    date_visit = models.DateTimeField(_('date_visit'))
    client = models.ForeignKey(Client, related_name='visit_client', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='visit_doctor', on_delete=models.CASCADE)
    visit_details = models.TextField(_('visit_details'), blank=True, null=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'visit'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['client']),
            models.Index(fields=['doctor']),
        ]
        # Сортировка по умолчанию
        ordering = ['date_visit']
    def __str__(self):
        # Вывод удобочитаемой строки 
        return "{}: {}, {}".format(self.date_visit.strftime('%d.%m.%Y'), self.client, self.doctor)


# Продажа услуг
class Sale(models.Model):
    visit = models.ForeignKey(Visit, related_name='sale_visit', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, related_name='sale_service', on_delete=models.CASCADE)
    price = models.DecimalField(_('sale_price'), max_digits=9, decimal_places=2)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'sale'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['visit']),
            models.Index(fields=['service']),
        ]
        # Сортировка по умолчанию
        ordering = ['service']
    def __str__(self):
        # Вывод в тег SELECT 
        return "{}: {}".format(self.service, self.client)


