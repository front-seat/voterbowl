/**
 * Implement the check page component.
 * 
 * @param {HTMLElement} self
 */

function checkPage(self) {
  /** 
    * Finalize a verify and, possibly, mint a new gift card if all is well.
    *
    * @param {string} firstName
    * @param {string} lastName
    * @param {string} email           
    */
  const finishVerify = (firstName, lastName, email) => {
    /** @type {HTMLElement} */
    const urgency = self.querySelector(".urgency");
    htmx.ajax("POST", "./finish/", {
      target: urgency,
      values: {
        first_name: firstName,
        last_name: lastName,
        email: email
      }
    });
  };

  window.addEventListener('VoteAmericaEvent', (event) => {
    // @ts-ignore-next-line
    const { data } = event.detail;
    if (data?.tool === "verify" && data?.event === "action-finish") {
      setTimeout(() => {
        finishVerify(data.first_name, data.last_name, data.email);
      }, 500);
    }
  });
}
