import dataclasses


@dataclasses.dataclass(frozen=True)
class Domains:
    """A set of email domains for a school."""

    primary: str
    aliases: tuple[str, ...]


def normalize_email(
    address: str,
    tag: str | None = "+",
    dots: bool = True,
    domains: Domains | None = None,
) -> str:
    """
    Normalize an email address.

    - Remove leading and trailing whitespace
    - Convert the address to lowercase
    - If provided, remove the `tag` character (+) and everything after it
    - If requested, remove dots (.) from the address
    - If provided, replace the domain with the primary domain if it is an alias

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
    if domains and domain in domains.aliases:
        domain = domains.primary
    # FORCE ascii for now (yes, this is absurd).
    local = local.encode("ascii", "ignore").decode("ascii")
    domain = domain.encode("ascii", "ignore").decode("ascii")
    return f"{local}@{domain}"
