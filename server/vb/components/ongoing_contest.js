/**
 * Provide a countdown for an ongoing contest.
 * 
 * @param {HTMLElement} self 
 * @param {object} props
 * @param {string} props.endsAt
 */

function ongoingCountdown(self, props) {

  /**
   * 
   * @param {HTMLElement} self 
   * @param {object} props
   * @param {string} props.endsAt
   */
  function countdown(self, props) {
    // compute the deadline
    const { endsAt } = props;
    const deadline = new Date(endsAt);
    const deadlineTime = deadline.getTime();

    /** Update the countdown. */
    function updateCountdown() {
      const now = new Date().getTime();
      const diff = deadlineTime - now;

      if (diff <= 0) {
        clearInterval(interval);
        self.innerText = "Just ended!";
        return;
      }

      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      const h0digit = Math.floor(hours / 10);
      const h1digit = hours % 10;
      const m0digit = Math.floor(minutes / 10);
      const m1digit = minutes % 10;
      const s0digit = Math.floor(seconds / 10);
      const s1digit = seconds % 10;

      const endsIn = `Ends in ${h0digit}${h1digit}:${m0digit}${m1digit}:${s0digit}${s1digit}`;
      self.innerText = endsIn;
    }

    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);
  }

  onloadAdd(() => countdown(self, props));
}
