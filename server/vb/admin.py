from typing import Any

from django import forms
from django.contrib import admin
from django.core.files.uploadedfile import UploadedFile
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from server.admin import admin_site

from .models import Logo, School, Student


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
    logo_bg_color = forms.CharField(
        required=False, help_text="Bubble bg color (default: transparent)"
    )

    class Meta:
        """Meta options."""

        model = School
        exclude = ["logo_json"]

    def save(self, *args: Any, **kwargs: Any) -> Any:
        """Set the `logo` and `logo_mime` fields."""
        logo_image = self.cleaned_data.get("logo_image")
        bg_color = self.cleaned_data.get("logo_bg_color") or "transparent"
        if logo_image:
            self.instance.logo = Logo.from_bytes(
                bytes_=logo_image.read(),
                mime=logo_image.content_type,
                bg_color=bg_color,
            )
        elif bg_color != "transparent":
            self.instance.logo = self.instance.logo.replace(bg_color=bg_color)
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
    readonly_fields = ("logo_json",)

    @admin.display(description="Logo")
    def logo_display(self, obj: School):
        """Return the logo as an bubble image."""
        context = {
            "logo": obj.logo,
            "width": "48px",
            "height": "48px",
        }

        return mark_safe(render_to_string("components/logo.dhtml", context))


class StudentAdmin(admin.ModelAdmin):
    """Student admin."""

    list_display = ("school", "email", "first_name", "last_name")
    search_fields = ("school__name", "email", "first_name", "last_name")


admin_site.register(School, SchoolAdmin)
admin_site.register(Student, StudentAdmin)
