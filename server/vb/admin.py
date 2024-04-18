import typing as t

from django import forms
from django.contrib import admin
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.timezone import now as django_now

from server.admin import admin_site

from .models import (
    Contest,
    EmailValidationLink,
    GiftCard,
    ImageMimeType,
    Logo,
    School,
    Student,
)


def validate_file_is_image(file: UploadedFile) -> None:
    """Validate that the file is an image."""
    if file.content_type is None:
        raise forms.ValidationError("File has no content type.")
    if file.content_type not in ImageMimeType.values:
        raise forms.ValidationError("File is not an image.")


class LogoForm(forms.ModelForm):
    """Logo form."""

    class Meta:
        """Meta class."""

        model = Logo
        fields = ("choose_image", "bg_color", "action_color")

    choose_image = forms.FileField(validators=[validate_file_is_image], required=False)

    def save(self, *args: t.Any, **kwargs: t.Any):
        """Save the form."""
        choose_image = self.cleaned_data.pop("choose_image", None)
        if choose_image is not None:
            self.instance.data = choose_image.read()
            self.instance.content_type = choose_image.content_type
        return super().save(*args, **kwargs)


class RenderLogoSpecimenMixin:
    """Logo display mixin."""

    def render_logo_specimen(self, obj: Logo):
        """Return the logo as an image."""
        if obj is None:
            return None

        context = {
            "logo": obj,
            "width": "48px",
            "height": "48px",
        }
        return mark_safe(render_to_string("components/logo_specimen.dhtml", context))


class LogoAdmin(admin.TabularInline, RenderLogoSpecimenMixin):
    """Logo admin."""

    model = Logo
    form = LogoForm
    fields = ("logo_display", "choose_image", "bg_color", "action_color")
    readonly_fields = ("logo_display",)
    extra = 0

    @admin.display(description="Logo")
    def logo_display(self, obj: Logo):
        """Return the logo as an bubble image."""
        if not obj.data:
            return None
        return self.render_logo_specimen(obj)


class InlineContestAdmin(admin.TabularInline):
    """Inline contest admin."""

    model = Contest
    extra = 0


class SchoolAdmin(admin.ModelAdmin, RenderLogoSpecimenMixin):
    """School admin."""

    list_display = (
        "name",
        "short_name",
        "slug_display",
        "logo_display",
        "active_contest",
        "student_count",
        "mascot",
        "mail_domains",
    )
    search_fields = ("name", "short_name", "slug")
    inlines = [LogoAdmin, InlineContestAdmin]

    @admin.display(description="Logo")
    def logo_display(self, obj: School):
        """Return the logo as an bubble image."""
        try:
            logo = obj.logo
        except Logo.DoesNotExist:
            return None
        return self.render_logo_specimen(logo)

    @admin.display(description="Landing Page")
    def slug_display(self, obj: School):
        """Return the school's landing page."""
        return mark_safe(f'<a href="/{obj.slug}/" target="_blank">/{obj.slug}/</a>')

    @admin.display(description="active contest")
    def active_contest(self, obj: School):
        """Return whether the school has an active contest."""
        current = obj.contests.current()
        if current is None:
            return ""
        url = reverse("admin:vb_contest_change", args=[current.pk])
        return mark_safe(f'<a href="{url}">{current.name}</a>')

    @admin.display(description="Students")
    def student_count(self, obj: School):
        """Return the number of students at the school."""
        count = obj.students.count()
        return count if count > 0 else ""


class EmailValidatedListFilter(admin.SimpleListFilter):
    """Email validated list filter."""

    title = "Email Validated"
    parameter_name = "email_validated"

    def lookups(self, request, model_admin):
        """Return the email validated lookups."""
        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, request, queryset):
        """Filter the queryset by email validated."""
        if self.value() == "yes":
            return queryset.filter(email_validated_at__isnull=False)
        if self.value() == "no":
            return queryset.filter(email_validated_at__isnull=True)
        return queryset


class StudentAdmin(admin.ModelAdmin):
    """Student admin."""

    list_display = (
        "name",
        "show_school",
        "email",
        "show_is_validated",
        "gift_card_total",
    )
    search_fields = ("school__name", "email", "first_name", "last_name")
    list_filter = (EmailValidatedListFilter, "school__name")

    @admin.display(description="School")
    def show_school(self, obj: Student) -> str:
        """Return the student's school."""
        # Get the link to the school admin page.
        school_admin_link = reverse("admin:vb_school_change", args=[obj.school.pk])
        return mark_safe(f'<a href="{school_admin_link}">{obj.school.name}</a>')

    @admin.display(description="Email Validated", boolean=True)
    def show_is_validated(self, obj: Student) -> bool:
        """Return whether the student's email is validated."""
        return obj.is_validated

    @admin.display(description="Gift Card Total")
    def gift_card_total(self, obj: Student) -> str | None:
        """Return the total number of gift cards the student has received."""
        usd = obj.gift_cards.aggregate(total=models.Sum("amount"))["total"] or 0
        return f"${usd}" if usd > 0 else None


class StatusListFilter(admin.SimpleListFilter):
    """Status list filter."""

    title = "Status"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        """Return the status lookups."""
        return (
            ("ongoing", "Ongoing"),
            ("upcoming", "Upcoming"),
            ("past", "Past"),
        )

    def queryset(self, request, queryset):
        """Filter the queryset by status."""
        when = django_now()
        if self.value() == "ongoing":
            return queryset.filter(start_at__lte=when, end_at__gt=when)
        if self.value() == "upcoming":
            return queryset.filter(start_at__gt=when)
        if self.value() == "past":
            return queryset.filter(end_at__lte=when)
        return queryset


class ContestAdmin(admin.ModelAdmin):
    """Contest admin."""

    list_display = (
        "id",
        "name",
        "status",
        "show_school",
        "start_at",
        "end_at",
    )
    search_fields = ("school__name", "school__short_name", "school__slug")
    list_filter = (StatusListFilter, "school__name")

    @admin.display(description="Status")
    def status(self, obj: Contest) -> str:
        """Return the contest's status."""
        if obj.is_ongoing():
            return "Ongoing"
        elif obj.is_upcoming():
            return "Upcoming"
        elif obj.is_past():
            return "Past"
        raise ValueError("Invalid contest status")

    @admin.display(description="School")
    def show_school(self, obj: Contest) -> str:
        """Return the student's school."""
        # Get the link to the school admin page.
        school_admin_link = reverse("admin:vb_school_change", args=[obj.school.pk])
        return mark_safe(f'<a href="{school_admin_link}">{obj.school.name}</a>')


class GiftCardAdmin(admin.ModelAdmin):
    """Gift card admin."""

    list_display = (
        "id",
        "created_at",
        "show_amount",
        "show_student",
        "show_school",
        "show_contest",
    )
    search_fields = ("id", "created_at", "student__email", "student__name")

    @admin.display(description="Amount")
    def show_amount(self, obj: GiftCard) -> str:
        """Return the gift card's amount."""
        return f"${obj.amount}"

    @admin.display(description="Student")
    def show_student(self, obj: GiftCard) -> str:
        """Return the gift card's student."""
        url = reverse("admin:vb_student_change", args=[obj.student.pk])
        return mark_safe(f'<a href="{url}">{obj.student.name}</a>')

    @admin.display(description="School")
    def show_school(self, obj: GiftCard) -> str:
        """Return the gift card's school."""
        url = reverse("admin:vb_school_change", args=[obj.student.school.pk])
        return mark_safe(f'<a href="{url}">{obj.student.school.name}</a>')

    @admin.display(description="Contest")
    def show_contest(self, obj: GiftCard) -> str:
        """Return the gift card's contest."""
        url = reverse("admin:vb_contest_change", args=[obj.contest.pk])
        return mark_safe(f'<a href="{url}">{obj.contest.name}</a>')


class EmailValidationLinkAdmin(admin.ModelAdmin):
    """Email validation link admin."""

    list_display = (
        "id",
        "email",
        "show_student",
        "show_school",
        "show_contest",
        "token",
        "is_consumed",
    )
    search_fields = ("email", "token")

    @admin.display(description="Student")
    def show_student(self, obj: GiftCard) -> str:
        """Return the gift card's student."""
        url = reverse("admin:vb_student_change", args=[obj.student.pk])
        return mark_safe(f'<a href="{url}">{obj.student.name}</a>')

    @admin.display(description="School")
    def show_school(self, obj: GiftCard) -> str:
        """Return the gift card's school."""
        url = reverse("admin:vb_school_change", args=[obj.student.school.pk])
        return mark_safe(f'<a href="{url}">{obj.student.school.name}</a>')

    @admin.display(description="Contest")
    def show_contest(self, obj: GiftCard) -> str:
        """Return the gift card's contest."""
        url = reverse("admin:vb_contest_change", args=[obj.contest.pk])
        return mark_safe(f'<a href="{url}">{obj.contest.name}</a>')

    @admin.display(description="Is Consumed", boolean=True)
    def is_consumed(self, obj: EmailValidationLink) -> bool:
        """Return whether the email validation link is consumed."""
        return obj.is_consumed()


admin_site.register(School, SchoolAdmin)
admin_site.register(Student, StudentAdmin)
admin_site.register(Contest, ContestAdmin)
admin_site.register(GiftCard, GiftCardAdmin)
admin_site.register(EmailValidationLink, EmailValidationLinkAdmin)
