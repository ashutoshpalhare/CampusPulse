from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from tracker.models import Assignment, Notice, Student


class Command(BaseCommand):
    help = "Create demo users and sample data (DEV ONLY - uses weak passwords)."

    def handle(self, *args, **options):
        User = get_user_model()
        admin, _ = User.objects.get_or_create(username="admin", defaults={"is_staff": True, "is_superuser": True})
        admin.set_password("admin12345"); admin.is_staff = True; admin.is_superuser = True; admin.save()
        stu, _ = User.objects.get_or_create(username="student")
        stu.set_password("student12345"); stu.save()

        now = timezone.now()
        for i, (name, dept) in enumerate([("Aarav Sharma", "Computer Science"), ("Diya Patil", "Electronics"),
                                          ("Kabir Singh", "Mechanical"), ("Meera Joshi", "Civil")], start=1):
            Student.objects.get_or_create(roll_no=f"CS2025-{i:03d}", defaults=dict(
                full_name=name, email=f"student{i}@college.edu", department=dept,
                semester=(i % 8) + 1, created_by=admin))

        for title, code, days in [("Problem Set 1", "CS201", -3), ("Lab Report", "EC110", 1),
                                  ("Mid-term Project", "ME305", 5), ("Case Study", "CE220", 14)]:
            Assignment.objects.get_or_create(title=title, course_code=code, defaults=dict(
                due_date=now + timedelta(days=days), description="Demo assignment.", created_by=admin))

        for title, prio in [("Exam timetable released", "high"), ("Library hours extended", "low"),
                            ("Guest lecture on AI", "medium")]:
            Notice.objects.get_or_create(title=title, defaults=dict(
                body="Demo notice body text for CampusPulse.", priority=prio, created_by=admin))

        self.stdout.write(self.style.SUCCESS("Seeded. Login: admin/admin12345 (staff) or student/student12345"))
