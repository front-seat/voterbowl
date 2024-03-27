from typing import Any

from django import forms
from django.contrib import admin
from django.core.files.uploadedfile import UploadedFile
from django.utils.html import format_html

from server.admin import admin_site

from .models import School, Student


def validate_file_is_image(file: UploadedFile) -> None:
    """Validate that the file is an image."""
    if file.content_type is None:
        raise forms.ValidationError("File has no content type.")
    if not file.content_type.startswith("image/"):
        raise forms.ValidationError("File is not an image.")


class SchoolForm(forms.ModelForm):
    """School form."""

    # ImageField doesn't accept SVGs, apparently
    logo_image = forms.FileField(validators=[validate_file_is_image], required=False)

    class Meta:
        """Meta options."""

        model = School
        exclude = ["logo_mime", "logo"]

    def save(self, *args: Any, **kwargs: Any) -> Any:
        """Set the `logo` and `logo_mime` fields."""
        logo_image = self.cleaned_data.get("logo_image")
        if logo_image:
            self.instance.logo = logo_image.read()
            self.instance.logo_mime = logo_image.content_type
        return super().save(*args, **kwargs)


class SchoolAdmin(admin.ModelAdmin):
    """School admin."""

    form = SchoolForm

    list_display = (
        "name",
        "short_name",
        "logo_display",
        "slug",
        "mascot",
        "mail_domains",
    )
    search_fields = ("name", "short_name", "slug")
    readonly_fields = ("logo_data_url", "logo_mime")

    def logo_display(self, obj):
        """Return the logo as an image."""
        return format_html(
            '<img src="{}" width="100" height="100" />',
            obj.logo_data_url(),
        )

    logo_display.short_description = "Logo"


class StudentAdmin(admin.ModelAdmin):
    """Student admin."""

    list_display = ("school", "email", "first_name", "last_name")
    search_fields = ("school__name", "email", "first_name", "last_name")


admin_site.register(School, SchoolAdmin)
admin_site.register(Student, StudentAdmin)
