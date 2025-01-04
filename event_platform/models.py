from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=255)
    espace = models.CharField(max_length=255)  
    competences_requises = models.TextField()  
    profils_recherches = models.TextField() 
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

class Volunteer(models.Model):
    name = models.CharField(max_length=255)  
    email = models.EmailField(unique=True)   
    phone = models.CharField(max_length=20)  
    assigned_task = models.TextField(blank=True, null=True)  

    def __str__(self):
        return self.name
    

class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    school = models.CharField(max_length=100)
    major = models.CharField(max_length=100)
    year = models.CharField(max_length=100) 
    address = models.TextField()
    email = models.EmailField(unique=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    password = models.CharField(max_length=128)
    available_slots = models.PositiveIntegerField(default=1) 

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class Queue(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('called', 'Called'),
        ('passing', 'Passing Interview'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
        ('withdrawn', 'Withdrawn'), 
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)  # Reference your custom Student model
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # Reference the company
    position = models.PositiveIntegerField()  # Position in the queue
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')  # Status in the queue

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.company.name} - {self.status}"
