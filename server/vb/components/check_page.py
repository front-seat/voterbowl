import htpy as h
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.templatetags.static import static
from django.urls import reverse
from markupsafe import Markup

from ..models import Contest, ContestEntry, School
from .base_page import base_page
from .countdown import countdown
from .logo import school_logo
from .utils import Fragment, fragment

_STYLE = """
me {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

me main {
  width: 100%;
  text-align: center;
  padding: 0.5rem 0;
}

me main img {
  height: 150px;
  margin-bottom: -1.75rem;
}

me main p {
  font-weight: 378;
  font-size: 20px;
  line-height: 130%;
}

me main h2 {
  font-weight: 500;
  font-size: 36px;
  line-height: 120%;
  text-transform: uppercase;
}

me .faq {
  width: 100%;
  color: white;
  padding: 2rem 0;
}

me .button-holder {
  display: flex;
  justify-content: center;
  margin: 1.5rem 0;
}

me .form {
  width: 100%;
  background-color: white;
  padding: 2rem 0;
}

me .urgency {
  flex-direction: column;
  gap: 1rem;
}

@media screen and (min-width: 768px) {
  me main {
    padding: 2rem 0;
  }

  me main img {
    height: 150px;
    margin: 1.5rem 0;
  }

  me .urgency {
    flex-direction: row;
    gap: 2rem;
  }
}

me main {
  position: relative;
  color: {main_color};
  background-color: {main_bg_color};
}

me main a {
  color: {main_color};
  transition: opacity 0.2s;
}

me main a:hover {
  opacity: 0.7;
  transition: opacity 0.2s;
}

me main .urgency {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

me main .fireworks {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  overflow: hidden;
}

me main .separate {
  padding-left: 1rem;
}

me main img {
  display: block;
}

@media screen and (min-width: 768px) {
  me main .urgency {
    flex-direction: row;
  }
}
"""

_SCRIPT = h.script[
    Markup("""
(function(self) {
    /** 
      * Finalize a verify and, possibly, mint a new gift card if all is well.
      *
      * @param {string} firstName
      * @param {string} lastName
      * @param {string} email           
      */
    const finishVerify = (firstName, lastName, email) => {
        htmx.ajax("POST", "./finish/", {
            target: self.querySelector(".urgency"),
            values: {
                first_name: firstName,
                last_name: lastName,
                email: email
            }
        });
    };

    window.addEventListener('VoteAmericaEvent', (event) => {
        const {
            data
        } = event.detail;
        if (data?.tool === "verify" && data?.event === "action-finish") {
            setTimeout(() => {
                finishVerify(data.first_name, data.last_name, data.email);
            }, 500);
        }
    });
})(me());""")
]


def _style(main_color: str, main_bg_color: str) -> h.Element:
    return h.style[
        _STYLE.replace("{main_color}", main_color).replace(
            "{main_bg_color}", main_bg_color
        )
    ]


def check_page(school: School, current_contest: Contest | None) -> h.Element:
    """Render a school-specific 'check voter registration' form page."""
    extra_head = [
        h.script(src=static("js/fireworks.js")),
        h.script(src="https://cdn.voteamerica.com/embed/tools.js", _async=True),
    ]
    return base_page(
        title=f"Voter Bowl x {school.name}",
        bg_color=school.logo.bg_color,
        extra_head=extra_head,
        show_faq=False,
        show_footer=False,
    )[
        h.div[
            _style(
                main_color=school.logo.bg_text_color, main_bg_color=school.logo.bg_color
            ),
            h.main[
                h.div(".container")[
                    h.div(".urgency")[
                        school_logo(school),
                        countdown(current_contest)
                        if current_contest
                        else h.div(".separate")[
                            h.p["Check your voter registraiton status below."]
                        ],
                    ]
                ],
                h.div(".fireworks"),
            ],
            h.div(".form")[
                h.div(".container")[
                    h.div(
                        ".voteamerica-embed",
                        data_subscriber="voterbowl",
                        data_tool="verify",
                        data_edition="college",
                    )
                ]
            ],
        ]
    ]


_FAIL_CHECK_SCRIPT = h.script[
    Markup("""
    (function (self) {
      const schoolName = "{{ school.short_name }}";
      const firstName = "{{ first_name }}";
      const lastName = "{{ last_name }}";
      let email = null;
      let count = 0; // give up after 3 tries
      while (email === null && count < 3) {
        email = prompt("Sorry, but we need your {{ school.short_name }} student email to continue. Please enter it below:");
        count++;
      }
      if (email) {
        htmx.ajax("POST", "./finish/", {
          target: document.querySelector(".urgency"),
          values: {
            email: email,
            first_name: firstName,
            last_name: lastName,
            school: schoolName
          }
        });
      }
    })(me());
""")
]


def fail_check_partial(
    school: School, first_name: str, last_name: str, current_contest: Contest | None
) -> Fragment:
    """Render a partial page for when the user's email is invalid."""
    return fragment[
        school_logo(school),
        h.p[
            _FAIL_CHECK_SCRIPT,
            h.b["We could not use your email"],
            f". Please use your { school.short_name } student email.",
        ],
    ]


_FINISH_CHECK_STYLE = """
    me {
      padding-top: 1rem;
      margin-left: 0;
    }

    @media screen and (min-width: 768px) {
      me {
        padding-top: 0;
        margin-left: 1rem;
      }
    }
"""

_FIREWORKS_SCRIPT = h.script[
    Markup(""" 
    (function(self) {
        const fireworks = new Fireworks.default(document.querySelector('.fireworks'));
        fireworks.start();
        setTimeout(() => fireworks.stop(), 10_000);
    })(me());
""")
]

_SCROLL_SCRIPT = h.script[
    Markup("""
      (function(self) {
          setTimeout(() => {
              // scroll entire window back to top, smoothly
              window.scrollTo({
                  top: 0,
                  behavior: 'smooth'
              });
          }, 100);
      })(me());
""")
]


def finish_check_partial(
    school: School,
    current_contest: Contest | None,
    contest_entry: ContestEntry | None,
    most_recent_winner: ContestEntry | None,
) -> Fragment:
    """Render a partial page for when the user has finished the check."""
    share_link: h.Node = [
        "Share this link: ",
        h.a(href=reverse("vb:school", args=[school.slug]))[
            settings.BASE_HOST, "/", school.slug
        ],
    ]

    description: h.Node
    if contest_entry and contest_entry.is_winner:
        description = [
            h.b["You win!"],
            f" We sent a ${contest_entry.amount_won} gift card to your school email. ",
            "(Check your spam folder.)",
            h.br,
            h.br,
            "Your friends can also win. ",
            share_link,
        ]
    elif contest_entry:
        description = [
            "Please register to vote if you haven't yet.",
            h.br,
            h.br,
            "You didn't win a gift card.",
            f" The last winner was {most_recent_winner.student.anonymized_name} {naturaltime(most_recent_winner.created_at)}"
            if most_recent_winner
            else None,
            "Your friends can still win! ",
            share_link,
        ]
    else:
        description = [
            "Thanks for checking your voter registraiton.",
            h.br,
            h.br,
            "Please register to vote if you haven't yet.",
        ]

    return fragment[
        school_logo(school),
        h.p[
            h.style[_FINISH_CHECK_STYLE],
            _FIREWORKS_SCRIPT if contest_entry and contest_entry.is_winner else None,
            _SCROLL_SCRIPT,
            description,
        ],
    ]
