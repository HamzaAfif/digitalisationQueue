from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Company
from .models import Volunteer
from .models import Student
from .models import Queue
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.db.models import Max
import json

def admin_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_superuser:  
                login(request, user)
                return redirect('admin_dashboard') 
            else:
                return render(request, 'admin_login.html', {'error': 'You are not authorized to access this page.'})
        else:
            return render(request, 'admin_login.html', {'error': 'Invalid credentials. Please try again.'})
    return render(request, 'admin_login.html')

@login_required
def admin_dashboard(request):

    if not request.user.is_superuser:
        return redirect('admin_login')  # Restrict access to superusers only

    companies = Company.objects.all()
    volunteers = Volunteer.objects.all()
    queues = {}
    
    for company in companies:
        queues[company.id] = Queue.objects.filter(company=company).order_by('position')

    # Handle POST request for adding or editing companies
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_company':
            name = request.POST.get('name')
            espace = request.POST.get('espace')
            competences_requises = request.POST.get('competences_requises')
            profils_recherches = request.POST.get('profils_recherches')

            Company.objects.create(
                name=name,
                espace=espace,
                competences_requises=competences_requises,
                profils_recherches=profils_recherches
            )
            return redirect('admin_dashboard')

        elif action == 'edit_company':
            company_id = request.POST.get('company_id')
            company = get_object_or_404(Company, id=company_id)
            company.name = request.POST.get('name')
            company.espace = request.POST.get('espace')
            company.competences_requises = request.POST.get('competences_requises')
            company.profils_recherches = request.POST.get('profils_recherches')
            company.save()
            return redirect('admin_dashboard')

        elif action == 'delete_company':
            company_id = request.POST.get('company_id')
            company = get_object_or_404(Company, id=company_id)
            company.delete()
            return redirect('admin_dashboard')
        
        elif action == 'add_volunteer':
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            assigned_task = request.POST.get('assigned_task')

            Volunteer.objects.create(
                name=name,
                email=email,
                phone=phone,
                assigned_task=assigned_task
            )
            return redirect('admin_dashboard')

        elif action == 'edit_volunteer':
            volunteer_id = request.POST.get('volunteer_id')
            volunteer = get_object_or_404(Volunteer, id=volunteer_id)
            volunteer.name = request.POST.get('name')
            volunteer.email = request.POST.get('email')
            volunteer.phone = request.POST.get('phone')
            volunteer.assigned_task = request.POST.get('assigned_task')
            volunteer.save()
            return redirect('admin_dashboard')

        elif action == 'delete_volunteer':
            volunteer_id = request.POST.get('volunteer_id')
            volunteer = get_object_or_404(Volunteer, id=volunteer_id)
            volunteer.delete()
            return redirect('admin_dashboard')
        
        if action == 'toggle_availability':
            company_id = request.POST.get('company_id')
            company = get_object_or_404(Company, id=company_id)
            company.available = not company.available 
            company.save()
            return redirect('admin_dashboard')
        
        if action == 'update_queue_status':
            queue_id = request.POST.get('queue_id')
            new_status = request.POST.get('status')

            try:
                queue = Queue.objects.get(id=queue_id)
                
                queue.status = new_status
                queue.save()

                student = queue.student  

                if new_status == 'completed':
                    # Remove only active queues (exclude both completed and withdrawn)
                    Queue.objects.filter(student=student).exclude(status__in=['completed', 'withdrawn']).exclude(id=queue_id).delete()
                    messages.info(request, f"Student {student.first_name} has been removed from all other active queues.")
                
                messages.success(request, f"Updated status for {queue.student.first_name} in {queue.company.name}.")
            except Queue.DoesNotExist:
                messages.error(request, "Queue entry not found.")
                
            return redirect('admin_dashboard')




    return render(request, 'admin_dashboard.html', {'companies': companies, 'volunteers': volunteers, 'queues': queues})




def admin_logout(request):

    logout(request)
    return redirect('admin_login')



@login_required
def list_companies(request):
    
    if not request.user.is_superuser:
        return redirect('admin_login')
    companies = Company.objects.all()
    return render(request, 'list_companies.html', {'companies': companies})


@login_required
def add_company(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    if request.method == 'POST':
        name = request.POST.get('name')
        espace = request.POST.get('espace')
        competences_requises = request.POST.get('competences_requises')
        profils_recherches = request.POST.get('profils_recherches')
        
        Company.objects.create(
            name=name,
            espace=espace,
            competences_requises=competences_requises,
            profils_recherches=profils_recherches
        )
        return redirect('list_companies')
    return render(request, 'add_company.html')


@login_required
def edit_company(request, company_id):
    
    if not request.user.is_superuser:
        return redirect('admin_login')
    company = get_object_or_404(Company, id=company_id)
    if request.method == 'POST':
        company.name = request.POST.get('name')
        company.espace = request.POST.get('espace')
        company.competences_requises = request.POST.get('competences_requises')
        company.profils_recherches = request.POST.get('profils_recherches')
        company.save()
        return redirect('list_companies')
    return render(request, 'edit_company.html', {'company': company})

def student_register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        school = request.POST.get('school')
        major = request.POST.get('major')
        year = request.POST.get('year')
        address = request.POST.get('address')
        email = request.POST.get('email')
        password = request.POST.get('password')
        resume = request.FILES.get('resume')

        student = Student.objects.create(
            first_name=first_name,
            last_name=last_name,
            school=school,
            major=major,
            year=year,
            address=address,
            email=email,
            password=password,
            resume=resume
        )
        student.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect('student_login')
    return render(request, 'student_register.html')

def student_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        print("haha", email)
        password = request.POST.get('password')
        print("haha", password)
        try:
            student = Student.objects.get(email=email, password=password)
            request.session['student_id'] = student.id
            return redirect('student_dashboard')
        except Student.DoesNotExist:
            print("Invalid email or password.")
            messages.error(request, "Invalid email or password.")
    return render(request, 'student_login.html')

def add_student_to_queue(student, company):
    # Check if the student is already in an active queue
    active_queue = Queue.objects.filter(student=student).exclude(status__in=['completed', 'withdrawn']).exists()
    if active_queue:
        raise ValueError("Student is already in an active queue.")

    # Check if the student has a withdrawn or completed entry for the same company
    existing_entry = Queue.objects.filter(student=student, company=company).first()
    if existing_entry:
        # Update the existing entry
        existing_entry.status = 'waiting'
        existing_entry.position = Queue.objects.filter(company=company).count() + 1
        existing_entry.save()
    else:
        # Create a new queue entry if none exists
        position = Queue.objects.filter(company=company).count() + 1
        Queue.objects.create(student=student, company=company, position=position, status='waiting')

    # Reorder the queue for the company
    reorder_queue(company)


def reorder_queue(company):
    # Fetch all entries for the company, excluding completed and withdrawn
    queue_entries = Queue.objects.filter(company=company).exclude(status__in=['completed', 'withdrawn']).order_by('id')
    for idx, entry in enumerate(queue_entries, start=1):
        entry.position = idx
        entry.save()


def student_dashboard(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')

    companies = Company.objects.all() 
    student = Student.objects.get(id=student_id)  
    
    active_queue = Queue.objects.filter(student=student).exclude(status__in=['completed', 'withdrawn']).first()

    
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'confirm_queue':
            if active_queue:
                messages.error(request, "You can only queue for one company at a time.")
            else:
                selected_company = request.POST.get('selected_company', '{}')
                selected_company = json.loads(selected_company)  # Parse JSON data
                print("Selected Company Received:", selected_company)

                if not selected_company:
                    messages.error(request, "No company selected.")
                else:
                    company_id = selected_company['id']
                    try:
                        company = Company.objects.get(id=company_id)
                        print(f"Adding to queue: {company.name}")
                        add_student_to_queue(student, company)
                        messages.success(request, f"You have been queued for {company.name}.")
                    except Company.DoesNotExist:
                        print(f"Company with ID {company_id} does not exist.")
                        messages.error(request, f"Company with ID {company_id} does not exist.")
                        
            return redirect('student_dashboard')
        
        elif action == 'withdraw_queue':
            # Fetch the active queue excluding 'withdrawn' and 'completed'
            active_queue = Queue.objects.filter(student=student).exclude(status__in=['completed', 'withdrawn']).first()
            
            if active_queue:
                active_queue.status = 'withdrawn'  # Mark the queue as withdrawn
                active_queue.save()
                messages.success(request, f"You have withdrawn from the queue for {active_queue.company.name}.")
            else:
                messages.error(request, "You are not in an active queue to withdraw from.")
            
            return redirect('student_dashboard')



    queued_companies = Queue.objects.filter(student=student).select_related('company')
    queued_company_ids = list(Queue.objects.filter(student=student).exclude(status__in=['completed', 'withdrawn']).values_list('company_id', flat=True))
    withdrawn_company_ids = list(Queue.objects.filter(student=student, status='withdrawn').values_list('company_id', flat=True))

    
    print("haha all queud", queued_companies)
    print("haha withdrawn_company_ids", withdrawn_company_ids)
    
    completed_company_ids = list(
    Queue.objects.filter(student=student, status='completed').values_list('company_id', flat=True)
)

    return render(request, 'student_dashboard.html', {
        'companies': companies,
        'active_queue': active_queue,
        'queued_companies': queued_companies,
        'queued_company_ids': queued_company_ids,
        'withdrawn_company_ids': withdrawn_company_ids,
        'completed_company_ids': completed_company_ids,
    })

def get_company_availability(request):
    companies = Company.objects.all()
    company_data = [
        {
            'id': company.id,
            'name': company.name,
            'available': company.available,
            'competences_requises': company.competences_requises,
        }
        for company in companies
    ]
    return JsonResponse({'companies': company_data})



def get_student_queue_status(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    student = Student.objects.get(id=student_id)
    active_queue_exists = Queue.objects.filter(student=student).exclude(status='completed').exists()

    queue_entries = Queue.objects.filter(student=student).select_related('company')

    queue_data = [
        {
            'company_id': entry.company.id,
            'company_name': entry.company.name,
            'position': entry.position,
            'status': entry.status,
        }
        for entry in queue_entries
    ]

    return JsonResponse({
        'queues': queue_data,
        'active_queue': active_queue_exists  is not None
    })