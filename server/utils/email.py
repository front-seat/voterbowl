import dataclasses
import logging
import re
import typing as t

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class Domains:
    """A set of email domains for a school."""

    primary: str
    aliases: tuple[str, ...]


def subdomain_of(domain: str, parent: str) -> bool:
    """Check if the `domain` is a subdomain of `parent`."""
    return domain == parent or domain.endswith(f".{parent}")


def normalize_email(
    address: str,
    tag: str | None = "+",
    dots: bool = True,
    domains: Domains | None = None,
    allow_subdomains: bool = True,
) -> str:
    """
    Normalize an email address.

    - Remove leading and trailing whitespace
    - Convert the address to lowercase
    - If provided, remove the `tag` character (+) and everything after it
    - If requested, remove dots (.) from the address
    - If provided, replace the domain with the primary domain if it is an alias
    - If requested, remove subdomains from the domain

    You must have previously validated the email address.

    This will certainly fail with technically valid cases like quoted strings,
    comments, and internationalized domain names. It should suffice for
    VoterBowl's purposes.
    """
    address = address.strip().lower()
    local, domain = address.split("@", maxsplit=1)
    if tag and tag in local:
        local = local.split(tag, maxsplit=1)[0]
    if dots:
        local = local.replace(".", "")
    if domains:
        if allow_subdomains and any(
            subdomain_of(domain, d) for d in [domains.primary, *domains.aliases]
        ):
            domain = domains.primary
        elif not allow_subdomains and domain in domains.aliases:
            domain = domains.primary
    # FORCE ascii for now (yes, this is absurd).
    local = local.encode("ascii", "ignore").decode("ascii")
    domain = domain.encode("ascii", "ignore").decode("ascii")
    return f"{local}@{domain}"


def send_template_email(
    to: str | t.Sequence[str],
    template_base: str,
    context: dict | None = None,
    from_email: str | None = None,
) -> bool:
    """
    Send a templatized email.

    Send an email to the `to` address, using the template files found under
    the `template_base` to render contents.

    The following named templates must be found underneath `template_base`:

        - `subject.txt`: renders the subject line
        - `body.txt`: renders the plain-text body
        - `body.html`: renders the HTML body

    Django's template system is flexible and can load templates from just about
    anywhere, provided you write a plugin. But! By default, we're going to load
    them from the filesystem; `template_base` is simply the name of the
    directory that contains these three files, relative to the `templates`
    directory in the app.

    For instance, if we have `subject`/`body` templates in
    `server/assistant/templates/email/registration`, then `template_base` is
    `email/registration`.
    """
    to_array = [to] if isinstance(to, str) else to

    message = create_message(to_array, template_base, context, from_email)
    try:
        message.send()
        return True
    except Exception:
        logger.exception(f"failed to send email to {to}")
        return False
    else:
        logger.info(f"successfully sent email to {to}")


def create_message(
    to: t.Sequence[str],
    template_base: str,
    context: dict[str, t.Any] | None = None,
    from_email: str | None = None,
) -> EmailMultiAlternatives:
    """Create the underlying email message to send."""
    context = context or {}
    from_email = from_email or settings.DEFAULT_FROM_EMAIL
    context.setdefault("BASE_URL", settings.BASE_URL)
    context.setdefault("BASE_HOST", settings.BASE_HOST)

    subject = render_to_string(f"{template_base}/subject.txt", context).strip()
    text = render_to_string(f"{template_base}/body.txt", context)
    html = render_to_string(f"{template_base}/body.html", context)

    final_to = list(to)
    if settings.DEBUG_EMAIL_TO:
        for i, email in enumerate(final_to):
            if re.match(settings.DEBUG_EMAIL_REGEX, email):
                final_to[i] = settings.DEBUG_EMAIL_TO
                logger.info(
                    f"DEBUG_EMAIL rerouting email {email} to {settings.DEBUG_EMAIL_TO} with subject: {subject}"  # noqa
                )

    message = EmailMultiAlternatives(
        from_email=from_email, to=final_to, subject=subject, body=text
    )
    message.attach_alternative(html, "text/html")

    return message
