import htpy as h
from django.urls import reverse

from .logo import VOTER_BOWL_LOGO


def footer() -> h.Element:
    """Render the site-wide footer."""
    return h.footer[
        h.div(".center")[VOTER_BOWL_LOGO],
        h.div(".outer")[
            h.p(".copyright")["© 2024 The Voter Bowl"],
            h.div(".inner")[
                h.a(href=reverse("vb:rules"), target="_blank")["Rules"],
                h.a(href="https://about.voteamerica.com/privacy", target="_blank")[
                    "Privacy"
                ],
                h.a(href="https://about.voteamerica.com/terms", target="_blank")[
                    "Terms"
                ],
                h.a(href="mailto:info@voterbowl.org")["Contact Us"],
            ],
        ],
        h.div(".colophon container")[
            h.p[
                "The Voter Bowl is a project of VoteAmerica, a 501(c)3 registered non-profit organization, and does not support or oppose any political candidate or party. Our EIN is 84-3442002. Donations are tax-deductible."
            ]
        ],
    ]
