/**
 * Outer wrapper for countdown code.
 * 
 * @param {HTMLElement} self 
 * @param {object} props
 * @param {string} props.endAt
 */

function countdownOuter(self, props) {
  /**
   * Countdown to a deadline.
   * 
   * @param {HTMLElement} self element containing the countdown.
   * @param {object} props properties of the countdown.
   * @param {string} props.endAt deadline of the countdown.
   * @returns {void}
   */
  function countdown(self, props) {
    // compute the deadline
    const { endAt } = props;
    const deadline = new Date(endAt);
    const deadlineTime = deadline.getTime();

    /** Update the countdown. */
    function updateCountdown() {
      const now = new Date().getTime();
      const diff = deadlineTime - now;

      // get the number elements
      /** @type {HTMLElement} */
      const h0 = self.querySelector('[data-number=h0]');
      /** @type {HTMLElement} */
      const h1 = self.querySelector('[data-number=h1]');
      /** @type {HTMLElement} */
      const m0 = self.querySelector('[data-number=m0]');
      /** @type {HTMLElement} */
      const m1 = self.querySelector('[data-number=m1]');
      /** @type {HTMLElement} */
      const s0 = self.querySelector('[data-number=s0]');
      /** @type {HTMLElement} */
      const s1 = self.querySelector('[data-number=s1]');
      const numbers = [h0, h1, m0, m1, s0, s1];

      if (numbers.some(number => !number)) {
        return;
      }

      if (diff <= 0) {
        clearInterval(interval);
        numbers.forEach(number => number.textContent = '0');
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

      numbers[0].innerText = h0digit.toString();
      numbers[1].innerText = h1digit.toString();
      numbers[2].innerText = m0digit.toString();
      numbers[3].innerText = m1digit.toString();
      numbers[4].innerText = s0digit.toString();
      numbers[5].innerText = s1digit.toString();
    }

    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);
  }

  onloadAdd(() => countdown(self, props));
}
