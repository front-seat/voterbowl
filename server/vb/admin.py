import typing as t
import zoneinfo

from django import forms
from django.contrib import admin
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.timezone import now as django_now

from server.admin import admin_site

from .components.logo import logo_specimen
from .models import (
    Contest,
    ContestEntry,
    EmailValidationLink,
    ImageMimeType,
    Logo,
    School,
    Student,
)

PACIFIC = zoneinfo.ZoneInfo("America/Los_Angeles")


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
        # XXX str(logo_specimen) returns markupsafe.Markup, lame.
        as_str = str(str(logo_specimen(obj)))
        return mark_safe(as_str)


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
        current_contest = obj.contests.current()
        if current_contest is None:
            return ""
        url = reverse("admin:vb_contest_change", args=[current_contest.pk])
        return mark_safe(f'<a href="{url}">{current_contest.name}</a>')

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
        "contest_entries",
        "gift_card_total",
        "created_at_pacific",
    )
    search_fields = ("school__name", "email", "first_name", "last_name")
    list_filter = (EmailValidatedListFilter, "school__name")
    readonly_fields = (
        "email_validated_at",
        "email_validated_at_pacific",
        "created_at_pacific",
        "updated_at_pacific",
    )

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

    @admin.display(description="Contest Entries")
    def contest_entries(self, obj: Student) -> int | str:
        """Return the number of contest entries the student has made."""
        count = obj.contest_entries.count()
        return count if count > 0 else ""

    @admin.display(description="Gift Card Total")
    def gift_card_total(self, obj: Student) -> str | None:
        """Return the total number of gift cards the student has received."""
        usd = (
            obj.contest_entries.aggregate(total=models.Sum("amount_won"))["total"] or 0
        )
        return f"${usd}" if usd > 0 else ""

    @admin.display(description="Email Validated At (Pacific)")
    def email_validated_at_pacific(self, obj: Student) -> str:
        """Return the student's email validated at time in the Pacific timezone."""
        return (
            obj.email_validated_at.astimezone(PACIFIC).strftime("%B %d, %Y @ %I:%M %p")
            if obj.email_validated_at
            else ""
        )

    @admin.display(description="Created At (Pacific)")
    def created_at_pacific(self, obj: Student) -> str:
        """Return the student's created at time in the Pacific timezone."""
        return obj.created_at.astimezone(PACIFIC).strftime("%B %d, %Y @ %I:%M %p")

    @admin.display(description="Updated At (Pacific)")
    def updated_at_pacific(self, obj: Student) -> str:
        """Return the student's updated at time in the Pacific timezone."""
        return obj.updated_at.astimezone(PACIFIC).strftime("%B %d, %Y @ %I:%M %p")


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


class InlineContestEntryAdmin(admin.TabularInline):
    """Inline contest entry admin."""

    model = ContestEntry
    extra = 0

    # These should be READONLY
    fields = (
        "student",
        "created_at_pacific",
        "show_winnings_issued",
        "amount_won",
        "roll",
    )
    readonly_fields = (
        "student",
        "created_at_pacific",
        "amount_won",
        "show_winnings_issued",
        "roll",
    )
    ordering = ("-amount_won", "creation_request_id")

    def created_at_pacific(self, obj: ContestEntry) -> str:
        """Return the contest entry's creation time in the Pacific timezone."""
        return obj.created_at.astimezone(PACIFIC).strftime("%B %d, %Y @ %I:%M %p")

    @admin.display(description="Issued?")
    def show_winnings_issued(self, obj: ContestEntry) -> str:
        """Return whether the contest entry's winnings have been issued."""
        if obj.has_issued:
            return "Yes"
        elif obj.is_winner:
            return "Not yet"
        else:
            return ""

    def has_delete_permission(self, *args, **kwargs) -> bool:
        """No permission to delete."""
        return False

    def has_add_permission(self, *args, **kwargs) -> bool:
        """No permission to add."""
        return False


class ContestAdmin(admin.ModelAdmin):
    """Contest admin."""

    list_display = (
        "id",
        "name",
        "status",
        "show_school",
        "start_at_pacific",
        "end_at_pacific",
    )
    search_fields = ("school__name", "school__short_name", "school__slug")
    list_filter = (StatusListFilter, "school__name")
    readonly_fields = ("status", "start_at_pacific", "end_at_pacific")
    inlines = [InlineContestEntryAdmin]

    @admin.display(description="Start At (Pacific)")
    def start_at_pacific(self, obj: Contest) -> str:
        """Return the contest's start time in the Pacific timezone."""
        return obj.start_at.astimezone(PACIFIC).strftime("%B %d, %Y @ %I:%M %p")

    @admin.display(description="End At (Pacific)")
    def end_at_pacific(self, obj: Contest) -> str:
        """Return the contest's end time in the Pacific timezone."""
        return obj.end_at.astimezone(PACIFIC).strftime("%B %d, %Y @ %I:%M %p")

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


class ContestWinnerListFilter(admin.SimpleListFilter):
    """Contest winner list filter."""

    title = "Winner?"
    parameter_name = "winner"

    def lookups(self, request, model_admin):
        """Return the state lookups."""
        return (
            ("winner", "Winner"),
            ("loser", "Loser"),
        )

    def queryset(self, request, queryset):
        """Filter the queryset by state."""
        if self.value() == "winner":
            return queryset.filter(roll=0)
        if self.value() == "loser":
            return queryset.exclude(roll=0)
        return queryset


class ContestWinningsIssuedListFilter(admin.SimpleListFilter):
    """Contest winnings issued list filter."""

    title = "Winnings Issued?"
    parameter_name = "winnings_issued"

    def lookups(self, request, model_admin):
        """Return the state lookups."""
        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, request, queryset):
        """Filter the queryset by state."""
        if self.value() == "yes":
            return queryset.exclude(creation_request_id="")
        if self.value() == "no":
            return queryset.filter(creation_request_id="")
        return queryset


class ContestEntryAdmin(admin.ModelAdmin):
    """Contest Entry admin."""

    list_display = (
        "id",
        "created_at",
        "show_is_winner",
        "show_winnings",
        "show_winnings_issued",
        "show_student",
        "show_school",
        "show_contest",
        "roll",
    )
    search_fields = ("id", "created_at", "student__email")
    list_filter = (
        ContestWinnerListFilter,
        ContestWinningsIssuedListFilter,
        "contest__school__name",
        "contest",
    )

    @admin.display(description="Winner?", boolean=True)
    def show_is_winner(self, obj: ContestEntry) -> bool:
        """Return whether the contest entry is a winner."""
        return obj.is_winner

    @admin.display(description="Winnings")
    def show_winnings(self, obj: ContestEntry) -> str:
        """Return the contest entry's winnings, if any, if any."""
        return f"${obj.amount_won}" if obj.is_winner else ""

    @admin.display(description="Issued?")
    def show_winnings_issued(self, obj: ContestEntry) -> str:
        """Return whether the contest entry's winnings have been issued."""
        if obj.has_issued:
            return "Yes"
        elif obj.is_winner:
            return "Not yet"
        else:
            return ""

    @admin.display(description="Student")
    def show_student(self, obj: ContestEntry) -> str:
        """Return the contest entry's student."""
        url = reverse("admin:vb_student_change", args=[obj.student.pk])
        return mark_safe(f'<a href="{url}">{obj.student.name}</a>')

    @admin.display(description="School")
    def show_school(self, obj: ContestEntry) -> str:
        """Return the contest entry's school."""
        url = reverse("admin:vb_school_change", args=[obj.student.school.pk])
        return mark_safe(f'<a href="{url}">{obj.student.school.name}</a>')

    @admin.display(description="Contest")
    def show_contest(self, obj: ContestEntry) -> str:
        """Return the contest entry's contest."""
        url = reverse("admin:vb_contest_change", args=[obj.contest.pk])
        return mark_safe(f'<a href="{url}">{obj.contest.name}</a>')


class EmailValidationLinkAdmin(admin.ModelAdmin):
    """Email validation link admin."""

    list_display = (
        "id",
        "email",
        "show_student",
        "show_school",
        "show_contest_entry",
        "token",
        "is_consumed",
    )
    search_fields = ("email", "token")

    @admin.display(description="Student")
    def show_student(self, obj: EmailValidationLink) -> str:
        """Return the validation link's student."""
        if obj.student is None:
            return ""
        url = reverse("admin:vb_student_change", args=[obj.student.pk])
        return mark_safe(f'<a href="{url}">{obj.student.name}</a>')

    @admin.display(description="School")
    def show_school(self, obj: EmailValidationLink) -> str:
        """Return the validation link's school."""
        if obj.student is None or obj.student.school is None:
            return ""
        url = reverse("admin:vb_school_change", args=[obj.student.school.pk])
        return mark_safe(f'<a href="{url}">{obj.student.school.name}</a>')

    @admin.display(description="Contest Entry")
    def show_contest_entry(self, obj: EmailValidationLink) -> str:
        """Return the gift card's contest entry."""
        if obj.contest_entry is None:
            return ""
        url = reverse("admin:vb_contestentry_change", args=[obj.contest_entry.pk])
        return mark_safe(f'<a href="{url}">{str(obj.contest_entry)}</a>')

    @admin.display(description="Is Consumed", boolean=True)
    def is_consumed(self, obj: EmailValidationLink) -> bool:
        """Return whether the email validation link is consumed."""
        return obj.is_consumed()


admin_site.register(School, SchoolAdmin)
admin_site.register(Student, StudentAdmin)
admin_site.register(Contest, ContestAdmin)
admin_site.register(ContestEntry, ContestEntryAdmin)
admin_site.register(EmailValidationLink, EmailValidationLinkAdmin)
