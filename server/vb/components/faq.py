import typing as t

import htpy as h
import markdown
from markupsafe import Markup

from ..models import School

_STYLE = """
    me {
      display: flex;
      flex-direction: column;
    }

    me h2 {
      font-size: 36px;
      font-weight: 440;
      line-height: 130%;
      margin-bottom: 1rem;
    }

    me h3 {
      font-weight: 600;
      font-size: 18px;
      line-height: 28px;
      margin-top: 1rem;
    }

    me p {
      font-weight: 378;
      font-size: 18px;
      line-height: 28px;
      opacity: 0.7;
    }

    me a {
      color: white;
      cursor: pointer;
      text-decoration: underline;
      transition: opacity 0.2s;
    }

    me a:hover {
      opacity: 0.7;
      transition: opacity 0.2s;
    }
"""


def qa(q: str, a: t.Iterable[h.Node]) -> h.Element:
    """Render a question and answer."""
    return h.div(".qa")[
        h.h3[q],
        (h.p[aa] for aa in a),
    ]


FAQ = markdown.markdown("""
## F.A.Q.

### Why should I check my voter registration status now?

Check now to avoid any last-minute issues before the election.

### What is the Voter Bowl?

The Voter Bowl is a contest where college students win prizes by checking if they are registered to vote.

The Voter Bowl is a nonprofit, nonpartisan project of [VoteAmerica](https://www.voteamerica.com/), a national leader in voter registration and participation.

### How do I claim my gift card?

If you win, we'll send an Amazon gift card to your student email address.

You can redeem your gift card by typing the claim code into [Amazon.com](https://www.amazon.com/gc/redeem).

[Read the full contest rules here](/rules).
                        
### What is the goal of the Voter Bowl?
                        
In the 2020 presidential election, 33% of college students didn’t vote. We believe a healthy democracy depends on more students voting.
                        
### Who's behind the Voter Bowl?
                        
[VoteAmerica](https://www.voteamerica.com/) runs the Voter Bowl with the generous support of donors who are passionate about boosting student voter participation.
                        
[Donate to VoteAmerica](https://donorbox.org/voteamerica-website?utm_medium=website&utm_source=voterbowl&utm_campaign=voterbowl&source=voterbowl) to support projects like this.

### I have another question.

[Contact us](mailto:info@voterbowl.org) and we'll be happy to answer it.                                 
""")


def faq(school: School | None) -> h.Element:
    """Render the frequently asked questions."""
    # check_now: list[h.Node] = [
    #     "Check now to avoid any last minute issues before the election."
    # ]
    # if school is not None:
    #     check_now = [
    #         h.a(href=reverse("vb:check", args=[school.slug]))["Check now"],
    #         " to avoid any last minute issues before the election.",
    #     ]

    return h.div[
        h.style[_STYLE],
        Markup(FAQ),
    ]
