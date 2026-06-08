import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Assignment, Notice, Student

HX = {"HTTP_HX_REQUEST": "true"}
STATIC_REF = re.compile(r'(?:src|href)="/static/([^"]+)"')


class BaseCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.staff = User.objects.create_user("staff", password="pw-staff-123", is_staff=True)
        cls.student = User.objects.create_user("stu", password="pw-stu-123")
        now = timezone.now()
        Assignment.objects.create(title="Lab Report", course_code="EC110", due_date=now + timedelta(days=1))
        Assignment.objects.create(title="Old Task", course_code="CS201", due_date=now - timedelta(days=1))
        Notice.objects.create(title="Exam timetable", body="Details", priority="high")


class AssetTests(BaseCase):
    """Every page must reference only local, existing static files - no CDN."""

    def _check_page(self, url, login=None):
        if login:
            self.client.force_login(login)
        html = self.client.get(url, follow=True).content.decode()
        self.assertNotIn("cdn.tailwindcss.com", html)
        self.assertNotRegex(html, r'(?:src|href)="https?://')  # no external assets at all
        refs = STATIC_REF.findall(html)
        self.assertTrue(refs, f"{url} references no static files")
        for ref in refs:
            self.assertIsNotNone(finders.find(ref), f"{url}: missing static file {ref}")
        return html

    def test_login_page(self):
        html = self._check_page(reverse("login"))
        self.assertIn("css/output.css", html)

    def test_dashboard(self):
        html = self._check_page(reverse("tracker:dashboard"), self.student)
        for name in ("htmx.min.js", "alpine.min.js", "chart.umd.js", "dashboard-charts.js", "toast.js"):
            self.assertIn(name, html)

    def test_assignment_list(self):
        self._check_page(reverse("tracker:assignment_list"), self.staff)

    def test_student_register(self):
        self._check_page(reverse("tracker:student_register"), self.staff)

    def test_compiled_css_contains_design_classes(self):
        path = finders.find("css/output.css")
        css = open(path, encoding="utf-8").read()
        for needle in (".dark\\:bg-slate-900", ".bg-indigo-600", ".lg\\:pl-64", ".cp-form", "font-family:Inter"):
            self.assertIn(needle, css)


class AccessTests(BaseCase):
    def test_anonymous_redirected_to_login(self):
        r = self.client.get(reverse("tracker:dashboard"))
        self.assertRedirects(r, f"{reverse('login')}?next=/")

    def test_student_is_read_only(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse("tracker:dashboard")).status_code, 200)
        self.assertEqual(self.client.get(reverse("tracker:assignment_list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("tracker:student_register")).status_code, 302)
        self.assertEqual(self.client.post(reverse("tracker:assignment_create"), {}).status_code, 302)

    def test_login_works(self):
        r = self.client.post(reverse("login"), {"username": "staff", "password": "pw-staff-123"})
        self.assertRedirects(r, reverse("tracker:dashboard"))


class HtmxTests(BaseCase):
    def setUp(self):
        self.client.force_login(self.staff)

    def test_search_returns_rows_only(self):
        r = self.client.get(reverse("tracker:assignment_list"), {"q": "lab"}, **HX)
        body = r.content.decode()
        self.assertNotIn("<html", body)
        self.assertIn("Lab Report", body)
        self.assertNotIn("Old Task", body)

    def test_status_filter(self):
        r = self.client.get(reverse("tracker:assignment_list"), {"status": "danger"}, **HX)
        self.assertIn("Old Task", r.content.decode())
        self.assertNotIn("Lab Report", r.content.decode())

    def test_history_restore_returns_full_page(self):
        r = self.client.get(reverse("tracker:assignment_list"), HTTP_HX_REQUEST="true",
                            HTTP_HX_HISTORY_RESTORE_REQUEST="true")
        self.assertIn("<html", r.content.decode())

    def test_student_register_success_and_toast(self):
        r = self.client.post(reverse("tracker:student_register"), {
            "roll_no": "cs1", "semester": 3, "full_name": "Test", "email": "T@X.com", "department": "CS"}, **HX)
        self.assertEqual(r.status_code, 200)
        self.assertIn("show-toast", r["HX-Trigger"])
        s = Student.objects.get(roll_no="CS1")
        self.assertEqual(s.email, "t@x.com")
        self.assertEqual(s.created_by, self.staff)

    def test_student_register_validation_errors(self):
        r = self.client.post(reverse("tracker:student_register"), {
            "roll_no": "cs1", "semester": 30, "full_name": "T", "email": "bad", "department": "CS"}, **HX)
        self.assertEqual(r.status_code, 200)
        self.assertIn('"level": "error"', r["HX-Trigger"])
        self.assertEqual(Student.objects.count(), 0)

    def test_assignment_create_triggers_refresh(self):
        due = (timezone.localtime() + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M")
        r = self.client.post(reverse("tracker:assignment_create"), {
            "title": "A", "course_code": "cs1", "max_marks": 50, "due_date": due, "description": ""}, **HX)
        self.assertIn("assignments-changed", r["HX-Trigger"])
        self.assertTrue(Assignment.objects.filter(course_code="CS1").exists())


class ModelTests(BaseCase):
    def test_deadline_status_levels(self):
        now = timezone.now()
        mk = lambda d: Assignment(title="x", course_code="c", due_date=now + d)
        self.assertEqual(mk(timedelta(days=-1)).deadline_status, "danger")
        self.assertEqual(mk(timedelta(hours=12)).deadline_status, "warning")
        self.assertEqual(mk(timedelta(days=4)).deadline_status, "info")
        self.assertEqual(mk(timedelta(days=10)).deadline_status, "success")


class TemplateHygieneTests(TestCase):
    def test_no_multiline_hash_comments(self):
        """Django's {# #} comment is single-line only; multi-line ones leak into the HTML."""
        from pathlib import Path
        root = Path(__file__).parent / "templates"
        bad = []
        for f in root.rglob("*.html"):
            for m in re.finditer(r"\{#(.*?)#\}", f.read_text(encoding="utf-8"), flags=re.S):
                if "\n" in m.group(1):
                    bad.append(str(f.relative_to(root)))
        self.assertEqual(bad, [], f"Use {{% comment %}} for multi-line comments: {bad}")
