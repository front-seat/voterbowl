import htpy as h
import markdown
from markupsafe import Markup

from .base_page import base_page

_STYLE = Markup("""
me {
    font-size: 1.25em;
    line-height: 150%;
    font-family: ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
}
""")

_RULES = markdown.markdown("""
**OFFICIAL SWEEPSTAKES RULES: The Voter Bowl, a project of www.voteamerica.com**

BY ENTERING THIS SWEEPSTAKES, YOU AGREE TO THESE RULES AND REGULATIONS.

NO PURCHASE OR PAYMENT OF ANY KIND IS NECESSARY TO ENTER OR WIN.

OPEN TO ELIGIBLE LEGAL RESIDENTS OF THE 50 UNITED STATES AND DISTRICT OF COLUMBIA EXCEPT FOR THOSE RESIDING IN MISSISSIPPI OR OREGON, WHO, AS OF THE TIME OF ENTRY, ARE AT LEAST 18 YEARS OLD.

VOID IN PUERTO RICO, OREGON, MISSISSIPPI AND ALL JURISDICTIONS OTHER THAN THOSE STATED ABOVE AND WHERE PROHIBITED OR RESTRICTED BY LAW.

**Introduction.** Prizes of different values will be awarded to college students with verifiable email addresses at the school where they are currently enrolled who check their voter registration status using the VoteAmerica “Check your registration status” tool during the timeframe of the contest specified on the www.voterbowl.org. Methods of entry and Official Rules are described below.

**Sponsor.** VoteAmerica. 530 Divisadero Street PMB 126 San Francisco CA 94117 (“Sponsor”)

Any questions, comments or complaints regarding the Sweepstakes is to be directed to Sponsor, at the address above, and not any other party.

**Timing.** The Sweepstakes timing will be posted on the www.voterbowl.org website between April 4th, 2024 and November 6th 2024 (the “Entry Period”). Sponsor’s computer is the official time keeping device for the Sweepstakes. Mail-in entries must be postmarked on the day that a contest is running for a specific college and must include a verifiable .edu student email address. Postcards not received by the Mail-in Entry Deadline will be disqualified. Proof of mailing does not constitute proof of delivery.

**Eligibility.** The Sweepstakes is open only to legal residents of the fifty (50) United States and the District of Columbia except for those residing in Mississippi and Oregon, who, as of the time of entry, are at least eighteen (18) years of age. Void in Puerto Rico, Mississippi, Oregon, and all other jurisdictions other than those stated above and where prohibited or restricted by law. Employees, officers, directors, contractors, and representatives of Sponsor and their respective corporate parents, subsidiaries, affiliates, advertising and promotion agencies, agents, and any other entity involved in the development or administration of the Sweepstakes (collectively, with Sponsor “Sweepstakes Entities”) as well as the immediate family (defined as spouse, parents, children, siblings, grandparents, and “steps” of each) and household members of each, whether or not related, are not eligible to enter or win the Sweepstakes. By participating, you agree to abide by these official rules (the “Official Rules”) and the decisions of Sponsor in all matters relating to the Sweepstakes, which are final and binding in all respects. Notwithstanding the foregoing, Sponsor’s volunteers are eligible to enter the Sweepstakes.

**How to Enter.** NO PURCHASE NECESSARY AND NO ENTRY FEE, PAYMENT OR PROOF OF PURCHASE IS NECESSARY TO PARTICIPATE.

Taking civic actions, such as verifying your voter registration status, registering to vote, or requesting a mail in ballot, is NOT required for entry. Having a valid voter registration status or being eligible to register to vote is NOT required for entry.

There are two (2) ways to enter the Sweepstakes:

1. **INTERNET:** Visit the Sweepstakes Website on a web browser. Complete the form provided on the Sweepstakes Website to enter.
1. **MAIL:** Mail a 3 ½” x 5” card with your name, complete valid postal address (including zip code), date of birth, telephone number, and valid .edu verifiable school e-mail address legibly, hand printed in a #10 envelope with proper postage affixed to: 530 Divisadero Street PMB 126 San Francisco CA 94117, ATTN: Voter Bowl. Maximum one (1) entry card will be accepted per stamped outer mailing envelope. The Sweepstakes Entities assume no responsibility for lost, late, incomplete, stolen, misdirected, mutilated, illegible or postage-due entries or mail, all of which will be void. No mechanically reproduced entries permitted. Illegible/incomplete entries are void. All entries become the property of Sponsor, and none will be acknowledged or returned.

Maximum of one (1) entry per person by Internet or Mail methods, or by any combination of these methods.

The submission of an entry is solely the responsibility of the entrant. Only eligible entries actually postmarked/received by the deadlines specified in these Official Rules will be included in the Prize drawing. Any automated receipt does not constitute proof of actual receipt by Sponsor of an entry for purposes of these Official Rules.

Compliance with the entry requirements will be determined by Sponsor in its sole discretion. Entries that violate these entry requirements will be disqualified from the Sweepstakes.

**Odds of Winning:** Odds of winning depend on the number of eligible entries received.

The total ARV of all Prizes offered in this Sweepstakes is $250,000 (USD).

Winners are subject to verification, including verification of age and residency. The Prize is neither transferable nor redeemable in cash and it must be accepted as awarded. No substitutions will be available, except at the sole discretion of Sponsor, who reserves the right to award a prize of equal or greater financial value if any advertised Prize (or any component thereof) becomes unavailable. Prize does not include any other item or expense not specifically described in these Official Rules.

Sponsor has no responsibility for the winner’s inability or failure to accept or use any part of the Prize as described herein.

WINNERS AGREE TO ACCEPT THE PRIZE “AS IS”, AND YOU HEREBY ACKNOWLEDGE THAT SWEEPSTAKES ENTITIES HAVE NEITHER MADE NOR ARE IN ANY MANNER RESPONSIBLE OR LIABLE FOR ANY WARRANTY, REPRESENTATION, OR GUARANTEE, EXPRESS OR IMPLIED, IN FACT OR IN LAW, RELATIVE TO THE PRIZE, INCLUDING BUT NOT LIMITED TO (A) ANY EXPRESS WARRANTIES PROVIDED EXCLUSIVELY BY A PRIZE SUPPLIER THAT ARE SENT ALONG WITH THE PRIZE OR (B) THEIR QUALITY OR MECHANIC CONDITIONS. SPONSOR HEREBY DISCLAIMS ALL IMPLIED WARRANTIES, INCLUDING WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE, AND NONINFRINGEMENT.

Winner is solely responsible for all federal, state, local, or other applicable taxes associated with the acceptance and use of a Prize. All costs and expenses associated with Prize acceptance and use not specifically provided herein are the responsibility of each winner.

**Winner Selection and Notification.** Winners will be required to verify their .edu school email address and will be notified of winning via this email address. Prizes are administered electronically using Sponsor’s computer.

Winner is subject to verification of eligibility, including verification of age and residency. Winners under the age of 18 must receive permission from their parents or legal guardian to participate, and a parent or legal guardian must accompany them on the trip and to the concerts as the second person.

If a Winner (i) is determined to be ineligible or otherwise disqualified by Sponsor or (ii) fails to respond to Sponsor’s selection email or text within forty-eight (48) hours of such email or text, the Winner forfeits the Prize in its entirety and a substitute Winner will be selected based upon a random drawing from among all other eligible entries received.

Winner may be required to complete, sign, notarize and return an affidavit of eligibility/liability release and a publicity release, all of which must be properly executed and returned within three (3) days of issuance of Prize notification. If these documents are not returned properly executed, or are returned to Sponsor as undeliverable, or if any given Winner does not otherwise comply with the Officials Rules, the Prize will be forfeited and awarded to an alternate winner.

**LIMITATIONS OF LIABILITY.**

YOU ACKNOWLEDGE AND AGREE THAT YOU ACCESS AND USE THE SWEEPSTAKES WEBSITE AT YOUR OWN RISK. THE SWEEPSTAKES WEBSITE IS MADE AVAILABLE ON AN “AS IS” AND “WITH ALL FAULTS” BASIS, AND THE SWEEPSTAKES ENTITIES EXPRESSLY DISCLAIM ANY AND ALL WARRANTIES AND CONDITIONS OF ANY KIND, INCLUDING WITHOUT LIMITATION ALL WARRANTIES OR CONDITIONS OF MERCHANTABILITY, TITLE, QUIET ENJOYMENT, ACCURACY, NON-INFRINGEMENT, AND/OR FITNESS FOR A PARTICULAR PURPOSE. THE SWEEPSTAKES ENTITIES MAKE NO WARRANTY THAT THE SWEEPSTAKES WEBSITE WILL MEET YOUR REQUIREMENTS, WILL BE AVAILABLE ON AN UNINTERRUPTED, TIMELY, SECURE, OR ERROR-FREE BASIS, OR WILL BE ACCURATE, RELIABLE, FREE OF VIRUSES OR OTHER HARMFUL CODE, COMPLETE, LEGAL, OR SAFE. IF APPLICABLE LAW REQUIRES ANY WARRANTIES WITH RESPECT TO THE SWEEPSTAKES WEBSITE, ALL SUCH WARRANTIES ARE LIMITED IN DURATION TO NINETY (90) DAYS FROM THE DATE OF FIRST USE. SOME JURISDICTIONS DO NOT ALLOW THE EXCLUSION OF IMPLIED WARRANTIES, SO THE FOREGOING EXCLUSION MAY NOT APPLY TO YOU. SOME JURISDICTIONS DO NOT ALLOW LIMITATIONS ON HOW LONG AN IMPLIED WARRANTY LASTS, SO THE FOREGOING LIMITATION MAY NOT APPLY TO YOU.

TO THE MAXIMUM EXTENT PERMITTED BY LAW AND NOT WITHSTANDING ANYTHING TO THE CONTRARY CONTAINED HEREIN, YOU AGREE THAT (I) SPONSOR SHALL NOT BE LIABLE TO YOU OR ANY THIRD PARTY FOR ANY INDIRECT, INCIDENTAL, CONSEQUENTIAL, EXEMPLARY, PUNITIVE OR SPECIAL DAMAGES ARISING FROM OR RELATED TO: (A) THE SWEEPSTAKES, (B) ANY PRIZE AWARDED, OR (C) YOUR USE OF INABILITY TO USE THE SWEEPSTAKES WEBSITE (IN EACH CASE EVEN IF SPONSOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES) AND (II) SPONSOR’S LIABILITY TO YOU FOR ANY DAMAGES ARISING FROM OR RELATED TO THESE OFFICIAL RULES, THE SWEEPSTAKES, THE SWEEPSTAKES WEBSITE, OR ANY PRIZE WILL AT ALL TIMES BE LIMITED TO YOUR ACTUAL OUT-OF-POCKET EXPENSES OF PARTICIPATION IN THE SWEEPSTAKES (IF ANY). THE EXISTENCE OF MORE THAN ONE CLAIM WILL NOT ENLARGE THIS LIMIT. YOU AGREE THAT OUR SUPPLIERS WILL HAVE NO LIABILITY OF ANY KIND ARISING FROM OR RELATING TO THESE OFFICIAL RULES.

By participating in the Sweepstakes, you agree to release and hold harmless Sweepstakes Entities from any liability, claims, costs, injuries, losses or damages of any kind, directly or indirectly, whether caused by negligence or not, from (i) your participation in the Sweepstakes, including, without limitation, the unauthorized or illegal access to personally identifiable or sensitive information or acceptance, possession, use, misuse, or nonuse of the Prize or any portion thereof; (ii) technical failures of any kind, including but not limited to the malfunctioning of any computer, mobile device, cable, network, hardware or software; (iii) the unavailability or inaccessibility of any telephone or Internet service; (iv) unauthorized human intervention in any part of the entry process or the Sweepstakes, or (v) electronic or human error which may occur in the administration of the Sweepstakes or the processing of entries, including, without limitation, incorrect, delayed or inaccurate transmission of winner notifications, prize claims or other information or communications relating to the Sweepstakes. In the event of any ambiguity or error(s) in these Official Rules, Sponsor reserves the right to clarify or modify these Official Rules however it deems appropriate to correct any such ambiguity or error(s). If due to an error or for any other reason, more legitimate prize claims are received than the number of prizes stated in these Official Rules, Sponsor reserves the right to award only one (1) Prize from a random drawing from among all eligible entrants. In no event will more than the stated number of prizes (i.e. one (1) Prize) be awarded.

Sponsor reserves the right in its sole discretion to disqualify any entry or entrant from the Sweepstakes or from winning the Prize if it determines that said entrant is attempting to undermine the legitimate operation of the promotion by cheating, deception, or other unfair playing practices (including the use of automated quick entry programs) or intending to annoy, abuse, threaten or harass any other entrants or any Sweepstakes Entities.

ANY ATTEMPT BY AN ENTRANT OR ANY OTHER INDIVIDUAL TO DELIBERATELY DAMAGE THE SWEEPSTAKES WEBSITE, TAMPER WITH THE ENTRY PROCESS, OR OTHERWISE UNDERMINE THE LEGITIMATE OPERATION OF THE SWEEPSTAKES MAY BE A VIOLATION OF LAW AND, SHOULD SUCH AN ATTEMPT BE MADE, SPONSOR RESERVES THE RIGHT TO PURSUE ALL REMEDIES AGAINST ANY SUCH INDIVIDUAL TO THE FULLEST EXTENT PERMITTED BY LAW.

**Sponsor’s Reservation of Rights.** Sponsor’s failure to enforce any term of these Official Rules shall not constitute a waiver of that provision. If any provision of these Official Rules is held to be invalid or unenforceable, such provision shall be struck, and the remaining provisions shall be enforced. If for any reason the Sweepstakes is not capable of being safely executed as planned, including, without limitation, as a result of war, natural disasters or weather events, labor strikes, acts of terrorism, pandemic infection (including without limitation, events related to the COVID-19 virus), or other force majeure event, or any infection by computer virus, bugs, tampering, unauthorized intervention, fraud, technical failures or any other causes which in the opinion of and/or Sweepstakes Entities, corrupt or affect the administration, security, fairness, integrity, or proper conduct and fulfillment of this Sweepstakes, Sponsor reserves the right to cancel, terminate, modify or suspend the Sweepstakes. In the event of any cancellation, termination or suspension, Sponsor reserves the right to select a winner from a random drawing from among all eligible, non-suspect entries received as of the date of the termination, cancellation or suspension.

**DISPUTES AND JURISDICTION:** THE SWEEPSTAKES IS GOVERNED BY, AND WILL BE CONSTRUED IN ACCORDANCE WITH, THE LAWS OF THE STATE OF CALIFORNIA, WITHOUT REGARD TO ITS CONFLICTS OF LAW PRINCIPLES, AND THE FORUM AND VENUE FOR ANY DISPUTE RELATING TO THE SWEEPSTAKES SHALL BE IN A FEDERAL OR STATE COURT OF COMPETENT JURISDICTION IN CALIFORNIA, CALIFORNIA. EXCEPT WHERE PROHIBITED, ENTRANTS AGREE THAT ANY AND ALL DISPUTES, CLAIMS AND CAUSES OF ACTION ARISING OUT OF OR CONNECTED WITH THIS SWEEPSTAKES OR ANY PRIZE AWARDED SHALL BE RESOLVED INDIVIDUALLY, WITHOUT RESORT TO ANY FORM OF CLASS ACTION.

**Official Rules.** For a copy of the Official Rules, mail a self-addressed stamped envelope by first class mail to Voter Bowl, 530 Divisadero Street PMB 126 San Francisco CA 94117, Attention: Rules Department. Sweepstakes entrants are hereby authorized to copy these Official Rules on the condition that it will be for their personal use and not for any commercial purpose whatsoever.

**Privacy.** Any personally identifiable information collected during an entrant’s participation in the Sweepstakes will be collected and used by Sponsor and its designees for the administration and fulfillment of the Sweepstakes and as otherwise described in these Official Rules and Sponsor’s privacy policy available at https://about.voteamerica.com/privacy. Should entrant register to vote, their information will be shared, as noted on the user interface, with the individual state election board in entrant’s home state, and also be added to databases of registered voters used exclusively for non-profit purposes and the purpose of encouraging voter turnout.

**Winners List.** A winners list is available only within sixty (60) days after the end of the Entry Period. To receive a copy of the winners list, mail a request to Voter Bowl Sweepstakes Winners List, 530 Divisadero Street PMB 126 San Francisco CA 94117, Attention: Winners List. In order to obtain a winner’s list, where permitted by law, send your written request and a self-addressed, stamped envelope (residents of VT and WA may omit return postage).

**Intellectual Property Ownership; Access to Sweepstakes Website.** You acknowledge and agree that the Sweepstakes Website and all content thereof, and all the intellectual property rights, including copyrights, patents, trademarks, and trade secrets therein, are owned by Sponsor or its licensors. Neither these Official Rules (nor your access to the Sweepstakes Website) transfers to you or any third party any rights, title or interest in or to such intellectual property rights, except for the limited, non-exclusive right to access the Sweepstakes Website for your own personal, noncommercial use. Sponsor and its suppliers reserve all rights not granted in these Official Rules. There are no implied licenses granted under these Official Rules.

All trademarks, logos and service marks (“Marks”) displayed on the Sweepstakes Website are our property or the property of other third parties. You are not permitted to use these Marks without our prior written consent or the consent of such third party which may own the Marks.

""")


def rules_page() -> h.Element:
    """Render the rules page."""
    return base_page(title="Voter Bowl Rules", bg_color="white", show_faq=False)[
        h.div(".container")[
            h.style[_STYLE],
            Markup(_RULES),
        ]
    ]
