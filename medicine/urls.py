"""
URL configuration for medicine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings 
from django.conf.urls import include
from django.conf.urls.static import static 


from center import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index),
    path('index/', views.index, name='index'),
    path('admin/', admin.site.urls),

    path('i18n/', include('django.conf.urls.i18n')),

    path('client/index/', views.client_index, name='client_index'),
    path('client/list/', views.client_list, name='client_list'),
    path('client/create/', views.client_create, name='client_create'),
    path('client/edit/<int:id>/', views.client_edit, name='client_edit'),
    path('client/delete/<int:id>/', views.client_delete, name='client_delete'),
    path('client/read/<int:id>/', views.client_read, name='client_read'),

    path('diagnosis/index/<int:client_id>/', views.diagnosis_index, name='diagnosis_index'),
    path('diagnosis/create/<int:client_id>/', views.diagnosis_create, name='diagnosis_create'),
    path('diagnosis/edit/<int:id>/<int:client_id>/', views.diagnosis_edit, name='diagnosis_edit'),
    path('diagnosis/delete/<int:id>/<int:client_id>/', views.diagnosis_delete, name='diagnosis_delete'),
    path('diagnosis/read/<int:id>/<int:client_id>/', views.diagnosis_read, name='diagnosis_read'),

    path('kind/index/', views.kind_index, name='kind_index'),
    path('kind/create/', views.kind_create, name='kind_create'),
    path('kind/edit/<int:id>/', views.kind_edit, name='kind_edit'),
    path('kind/delete/<int:id>/', views.kind_delete, name='kind_delete'),
    path('kind/read/<int:id>/', views.kind_read, name='kind_read'),
    
    path('service/index/', views.service_index, name='service_index'),
    path('service/create/', views.service_create, name='service_create'),
    path('service/edit/<int:id>/', views.service_edit, name='service_edit'),
    path('service/delete/<int:id>/', views.service_delete, name='service_delete'),
    path('service/read/<int:id>/', views.service_read, name='service_read'),
    
    path('sale/index/<int:visit_id>/', views.sale_index, name='sale_index'),
    path('sale/list/', views.sale_list, name='sale_list'),
    path('sale/create/<int:visit_id>/', views.sale_create, name='sale_create'),
    path('sale/edit/<int:id>/<int:visit_id>/', views.sale_edit, name='sale_edit'),
    path('sale/delete/<int:id>/<int:visit_id>/', views.sale_delete, name='sale_delete'),
    path('sale/read/<int:id>/<int:visit_id>/', views.sale_read, name='sale_read'),
    
    path('category/index/', views.category_index, name='category_index'),
    path('category/create/', views.category_create, name='category_create'),
    path('category/edit/<int:id>/', views.category_edit, name='category_edit'),
    path('category/delete/<int:id>/', views.category_delete, name='category_delete'),
    path('category/read/<int:id>/', views.category_read, name='category_read'),

    path('branch/index/', views.branch_index, name='branch_index'),
    path('branch/create/', views.branch_create, name='branch_create'),
    path('branch/edit/<int:id>/', views.branch_edit, name='branch_edit'),
    path('branch/delete/<int:id>/', views.branch_delete, name='branch_delete'),
    path('branch/read/<int:id>/', views.branch_read, name='branch_read'),

    path('specialization/index/', views.specialization_index, name='specialization_index'),
    path('specialization/create/', views.specialization_create, name='specialization_create'),
    path('specialization/edit/<int:id>/', views.specialization_edit, name='specialization_edit'),
    path('specialization/delete/<int:id>/', views.specialization_delete, name='specialization_delete'),
    path('specialization/read/<int:id>/', views.specialization_read, name='specialization_read'),

    path('doctor/index/', views.doctor_index, name='doctor_index'),
    path('doctor/create/', views.doctor_create, name='doctor_create'),
    path('doctor/edit/<int:id>/', views.doctor_edit, name='doctor_edit'),
    path('doctor/delete/<int:id>/', views.doctor_delete, name='doctor_delete'),
    path('doctor/read/<int:id>/', views.doctor_read, name='doctor_read'),

    path('schedule/index/', views.schedule_index, name='schedule_index'),
    path('schedule/list/', views.schedule_list, name='schedule_list'),
    path('schedule/create/', views.schedule_create, name='schedule_create'),
    path('schedule/edit/<int:id>/', views.schedule_edit, name='schedule_edit'),
    path('schedule/delete/<int:id>/', views.schedule_delete, name='schedule_delete'),
    path('schedule/read/<int:id>/', views.schedule_read, name='schedule_read'),

    path('visit/index/', views.visit_index, name='visit_index'),
    path('visit/list/', views.visit_list, name='visit_list'),
    path('visit/create/', views.visit_create, name='visit_create'),
    path('visit/edit/<int:id>/', views.visit_edit, name='visit_edit'),
    path('visit/delete/<int:id>/', views.visit_delete, name='visit_delete'),
    path('visit/read/<int:id>/', views.visit_read, name='visit_read'),

    path('report/report_1/', views.report_1, name='report_1'),
    path('report/report_2/', views.report_2, name='report_2'),
    path('report/report_3/', views.report_3, name='report_3'),
    path('report/report_4/', views.report_4, name='report_4'),

    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    #path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logout/', views.logoutUser, name="logout"),
    path('settings/account/', views.UserUpdateView.as_view(), name='my_account'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
