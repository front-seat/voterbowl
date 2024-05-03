import htpy as h
from django.templatetags.static import static
from markupsafe import Markup

from ..models import Contest, School
from .base_page import base_page
from .countdown import countdown
from .logo import school_logo

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
