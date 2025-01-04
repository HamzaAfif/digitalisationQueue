from django.urls import path
from . import views

urlpatterns = [
    path('admin/login/', views.admin_login, name='admin_login'),  
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),  
    path('admin/logout/', views.admin_logout, name='admin_logout'),  
    path('admin/companies/', views.list_companies, name='list_companies'),
    path('admin/companies/add/', views.add_company, name='add_company'),
    path('admin/companies/edit/<int:company_id>/', views.edit_company, name='edit_company'),
    path('register/', views.student_register, name='student_register'),
    path('login/', views.student_login, name='student_login'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('get-company-availability/', views.get_company_availability, name='get_company_availability'),
    path('get-student-queue-status/', views.get_student_queue_status, name='get_student_queue_status'),
    #path('logout/', views.student_logout, name='student_logout'),
]


