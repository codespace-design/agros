import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agros.settings')
django.setup()

from django.db import transaction
from django.utils import timezone
from users.models import User, SystemSetting
from estates.models import Estate
from plots.models import Plot
from labor.models import Labor, Attendance, Payment
from activities.models import ActivityCategory, Activity, TaskAssignment
from production.models import Production
from django.contrib.admin.models import LogEntry

def clear_data():
    print("Clearing existing data...")
    with transaction.atomic():
        LogEntry.objects.all().delete()
        Production.objects.all().delete()
        TaskAssignment.objects.all().delete()
        Activity.objects.all().delete()
        ActivityCategory.objects.all().delete()
        Attendance.objects.all().delete()
        Payment.objects.all().delete()
        Labor.objects.all().delete()
        Plot.objects.all().delete()
        Estate.objects.all().delete()
        User.objects.all().delete()
        SystemSetting.objects.all().delete()

def seed_data():
    print("Starting data seeding...")
    with transaction.atomic():
        # 1. Create Admin and Manager
        admin = User.objects.create_superuser(username='admin', email='admin@agros.com', password='adminpassword')
        admin.role = 'ADMIN'
        admin.save()
        
        manager = User.objects.create_user(username='manager', email='manager@agros.com', password='managerpassword')
        manager.role = 'MANAGER'
        manager.save()
        
        # 2. System Settings
        SystemSetting.objects.create(key="BASE_WAGE", value="650", description="Daily base wage for workers")
        SystemSetting.objects.create(key="COMPANY_NAME", value="Agros Cardamom Estates", description="Company Name")
        SystemSetting.objects.create(key="WORKING_HOURS", value="8", description="Standard working hours")

        # 3. Estates
        estates_data = [
            ("Green Valley", "Munnar, Kerala", 45.5),
            ("Highlands Estate", "Idukki, Kerala", 32.0),
            ("Misty Peaks", "Sakleshpur, Karnataka", 28.5),
            ("Emerald Plantation", "Coorg, Karnataka", 55.0),
        ]
        estates = []
        for name, loc, area in estates_data:
            estates.append(Estate.objects.create(estate_name=name, location=loc, total_area=area))

        # 4. Plots
        plots = []
        for estate in estates:
            for i in range(1, 4): # 3 plots per estate
                plots.append(Plot.objects.create(
                    estate=estate, 
                    plot_name=f"Plot {chr(64+i)}", 
                    plant_count=random.randint(500, 1500)
                ))

        # 5. Labor & Categories
        categories_data = [
            ("Weeding", "Removing unwanted plants."),
            ("Fertilizing", "Applying nutrients to soil."),
            ("Pruning", "Cutting back branches for growth."),
            ("Pesticide Application", "Controlling pests."),
            ("Irrigation", "Watering plants."),
            ("Harvesting", "Picking mature cardamom pods.")
        ]
        cat_objs = [ActivityCategory.objects.create(category_name=cat, description=desc) for cat, desc in categories_data]
        harvest_cat = [c for c in cat_objs if c.category_name == "Harvesting"][0]

        worker_names = [
            "Ravi Kumar", "Suresh Raina", "Lakshmi Devi", "Priya Mani", "Anand Singh",
            "Meena Kumari", "Rajesh V", "Kavita S", "Arjun Das", "Sita Ram",
            "Vikram Seth", "Maya Rao", "Gopal K", "Sneha L", "Rahul M",
            "Deepak P", "Anita J", "Karthik R", "Shanti B", "Mohan L"
        ]
        workers = []
        for name in worker_names:
            u_name = name.lower().replace(" ", "_")
            user = User.objects.create_user(username=u_name, password='workerpassword')
            user.role = 'WORKER'
            user.save()
            workers.append(Labor.objects.create(user=user, name=name, phone=f"98765{random.randint(10000, 99999)}", address="Estate Housing Block A"))

        # 6. Historical Data (5 Years)
        print("Generating 5 years of historical data (this may take a minute)...")
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=5*365)
        
        current_date = start_date
        
        while current_date <= end_date:
            # Attendance (80-100% present)
            present_count = random.randint(int(len(workers)*0.8), len(workers))
            present_workers = random.sample(workers, k=present_count)
            
            attendance_list = []
            for worker in workers:
                status = 'PRESENT' if worker in present_workers else random.choice(['ABSENT', 'ABSENT', 'HALF_DAY'])
                attendance_list.append(Attendance(worker=worker, date=current_date, status=status))
            Attendance.objects.bulk_create(attendance_list)
                
            # Activities & Tasks (Mon-Sat)
            if current_date.weekday() < 6:
                for _ in range(random.randint(1, 3)):
                    plot = random.choice(plots)
                    category = random.choice(cat_objs)
                    activity = Activity.objects.create(
                        plot=plot,
                        category=category,
                        activity_date=current_date,
                        description=f"Standard {category.category_name} maintenance for {plot.plot_name}."
                    )
                    
                    # Task Assignments (2-4 workers)
                    assigned_workers = random.sample(present_workers, k=min(len(present_workers), random.randint(2, 4)))
                    for worker in assigned_workers:
                        TaskAssignment.objects.create(
                            worker=worker,
                            plot=plot,
                            activity=activity,
                            task_date=current_date,
                            wage=Decimal("650.00"),
                            status='COMPLETED',
                            completed_at=timezone.make_aware(datetime.combine(current_date, datetime.min.time()))
                        )
                    
                    # Production (Harvesting)
                    if category == harvest_cat:
                        Production.objects.create(
                            plot=plot,
                            harvest_date=current_date,
                            quantity=Decimal(random.uniform(20.0, 150.0)).quantize(Decimal('0.01'))
                        )

            # Monthly Payments
            if current_date.day == 10:
                prev_month = (current_date.replace(day=1) - timedelta(days=1))
                for worker in workers:
                    days_worked = Attendance.objects.filter(
                        worker=worker, 
                        date__year=prev_month.year, 
                        date__month=prev_month.month, 
                        status='PRESENT'
                    ).count()
                    if days_worked > 0:
                        Payment.objects.create(
                            worker=worker,
                            manager=manager,
                            amount=Decimal(days_worked * 650.00),
                            date=current_date,
                            notes=f"Salary for {prev_month.strftime('%B %Y')}"
                        )

            if current_date.day == 1 and current_date.month == 1:
                print(f"Reached year {current_date.year}...")
                
            current_date += timedelta(days=1)

    print("\nData seeding completed successfully!")
    print(f"Total Attendance records: {Attendance.objects.count()}")
    print(f"Total Tasks: {TaskAssignment.objects.count()}")
    print(f"Total Production records: {Production.objects.count()}")

if __name__ == "__main__":
    clear_data()
    seed_data()
