from django.db import models
from django.utils import timezone

class Student(models.Model):
    DEPARTMENTS = [
        ("CSE", "Computer Science"),
        ("IT", "Information Technology"),
        ("ECE", "Electronics"),
        ("MECH", "Mechanical"),
    ]
    roll_no = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    department = models.CharField(max_length=10, choices=DEPARTMENTS)
    semester = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.roll_no} - {self.full_name}"


class Assignment(models.Model):
    title = models.CharField(max_length=150)
    course_code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    max_marks = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        return self.title

    @property
    def deadline_status(self):
        """Returns status tuple: (status_text, bootstrap_color_class)"""
        now = timezone.now()
        delta = self.due_date - now
        if delta.days < 0:
            return "Overdue", "danger"
        elif delta.days == 0:
            return "Due Today", "warning"
        elif delta.days <= 3:
            return "Coming Soon", "info"
        else:
            return "On Track", "success"


class Notice(models.Model):
    PRIORITY = [("LOW", "Low"), ("MEDIUM", "Medium"), ("HIGH", "High")]
    title = models.CharField(max_length=150)
    body = models.TextField()
    priority = models.CharField(max_length=6, choices=PRIORITY, default="MEDIUM")
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-posted_at"]

    def __str__(self):
        return self.title