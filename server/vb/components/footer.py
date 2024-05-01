import htpy as h
from django.urls import reverse

from .logo import VOTER_BOWL_LOGO

_STYLE = """
me {
  background-color: black;
  color: #aaa;
  padding-top: 4rem;
  padding-bottom: 2rem;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
  width: 100%;
}

@media screen and (min-width: 768px) {
  me {
    padding-left: 2em;
    padding-right: 2rem;
  }
}

me div.center {
  margin-bottom: 2em;
  display: flex;
  justify-content: center;
  color: #fff;
}

me div.center svg {
  width: 120px !important;
}

me div.outer {
  display: flex;
  flex-direction: column-reverse;
  justify-content: space-between;
  align-items: center;
}

@media screen and (min-width: 768px) {
  me div.outer {
    flex-direction: row;
  }
}

me div.inner {
  display: flex;
  flex-direction: row;
  gap: 1em;
}

me a {
  color: #aaa;
  text-decoration: underline;
}

me a:hover {
  color: white;
}

me .colophon {
  text-align: center;
  color: #888;
  font-size: 0.8em;
  padding-top: 1em;
  padding-bottom: 3em;
}
"""


def footer() -> h.Element:
    """Render the site-wide footer."""
    return h.footer[
        h.style[_STYLE],
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
