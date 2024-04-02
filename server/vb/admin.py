import typing as t

from django import forms
from django.contrib import admin
from django.core.files.uploadedfile import UploadedFile
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from server.admin import admin_site

from .models import Action, Contest, ImageMimeType, Logo, School, Student


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
        "logo_display",
        "slug_display",
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


class StudentAdmin(admin.ModelAdmin):
    """Student admin."""

    list_display = ("school", "email", "first_name", "last_name")
    search_fields = ("school__name", "email", "first_name", "last_name")


class ContestAdmin(admin.ModelAdmin):
    """Contest admin."""

    list_display = ("id", "name", "school", "start_at", "end_at")
    search_fields = ("name", "school__name")


class ActionAdmin(admin.ModelAdmin):
    """Action admin."""

    list_display = ("taken_at", "kind", "student", "contest")
    search_fields = (
        "student__email",
        "student__first_name",
        "student__last_name",
        "contest__name",
    )


admin_site.register(School, SchoolAdmin)
admin_site.register(Student, StudentAdmin)
admin_site.register(Contest, ContestAdmin)
admin_site.register(Action, ActionAdmin)
