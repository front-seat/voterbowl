import * as htmx from "./htmx.min.js";

/*-----------------------------------------------------------------
 * Countdown Timer
 * -----------------------------------------------------------------*/

/**
 * Return the time remaining until the given end time as a structure
 * containing separate digits.
 *
 * @typedef {object} RemainingTime
 * @property {number} h0 The tens digit of the hours.
 * @property {number} h1 The ones digit of the hours.
 * @property {number} m0 The tens digit of the minutes.
 * @property {number} m1 The ones digit of the minutes.
 * @property {number} s0 The tens digit of the seconds.
 * @property {number} s1 The ones digit of the seconds.
 *
 * @param {Date} endAt The end time.
 * @returns {RemainingTime|"ended"} The time remaining.
 */
const remainingTime = (endAt) => {
  const now = new Date().getTime();
  const diff = endAt.getTime() - now;

  if (diff <= 0) {
    return "ended";
  }

  const hours = Math.floor(diff / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diff % (1000 * 60)) / 1000);

  return {
    h0: Math.floor(hours / 10),
    h1: hours % 10,
    m0: Math.floor(minutes / 10),
    m1: minutes % 10,
    s0: Math.floor(seconds / 10),
    s1: seconds % 10,
  };
};

/**
 * @description A base class for countdown timers.
 */
class BaseCountdown extends HTMLElement {
  /** @type {number|null} */
  #interval = null;

  connectedCallback() {
    if (!this.#interval) {
      this.#interval = setInterval(() => this.tick(), 1000);
      this.tick();
    }
  }

  disconnectedCallback() {
    if (this.#interval) {
      clearInterval(this.#interval);
      this.#interval = null;
    }
  }

  /** @returns {Date} The end time of the countdown. */
  get endAt() {
    return new Date(this.dataset.endAt);
  }

  tick() {
    const remaining = remainingTime(this.endAt);
    if (remaining === "ended") {
      this.ended();
    } else {
      this.update(remaining);
    }
  }

  /**
   * Update the display with positive time remaining.
   *
   * @param {RemainingTime} remaining The time remaining.
   * @returns {void}
   */
  update(remaining) {
    throw new Error("Not implemented");
  }

  /**
   * Update the display with the countdown ended.
   *
   * @returns {void}
   */
  ended() {
    throw new Error("Not implemented");
  }
}

/**
 * @description A large-display countdown timer.
 *
 * The HTML structure is provided in the HTML itself; we don't
 * explicitly define it here.
 */
class BigCountdown extends BaseCountdown {
  /** @type {HTMLElement|null} */
  #h0 = null;
  /** @type {HTMLElement|null} */
  #h1 = null;
  /** @type {HTMLElement|null} */
  #m0 = null;
  /** @type {HTMLElement|null} */
  #m1 = null;
  /** @type {HTMLElement|null} */
  #s0 = null;
  /** @type {HTMLElement|null} */
  #s1 = null;

  connectedCallback() {
    this.#h0 = this.querySelector("[data-number=h0]");
    this.#h1 = this.querySelector("[data-number=h1]");
    this.#m0 = this.querySelector("[data-number=m0]");
    this.#m1 = this.querySelector("[data-number=m1]");
    this.#s0 = this.querySelector("[data-number=s0]");
    this.#s1 = this.querySelector("[data-number=s1]");

    // if any of the numbers are missing, don't start the countdown
    const numbers = [
      this.#h0,
      this.#h1,
      this.#m0,
      this.#m1,
      this.#s0,
      this.#s1,
    ];
    if (numbers.some((number) => !number)) {
      return;
    }

    super.connectedCallback();
  }

  /**
   * Update the display with positive time remaining.
   *
   * @param {RemainingTime} remaining The time remaining.
   * @returns {void}
   */
  update(remaining) {
    this.#h0.innerText = remaining.h0.toString();
    this.#h1.innerText = remaining.h1.toString();
    this.#m0.innerText = remaining.m0.toString();
    this.#m1.innerText = remaining.m1.toString();
    this.#s0.innerText = remaining.s0.toString();
    this.#s1.innerText = remaining.s1.toString();
  }

  /**
   * Update the display with the countdown ended.
   *
   * @returns {void}
   */
  ended() {
    this.#h0.innerText = "0";
    this.#h1.innerText = "0";
    this.#m0.innerText = "0";
    this.#m1.innerText = "0";
    this.#s0.innerText = "0";
    this.#s1.innerText = "0";
  }
}

/**
 * @description A small-display countdown timer.
 *
 * The HTML structure is provided in the HTML itself; we don't
 * explicitly define it here.
 */
class SmallCountdown extends BaseCountdown {
  /** @type {HTMLElement|null} */
  #countdown = null;

  connectedCallback() {
    this.#countdown = this.querySelector(".countdown");

    if (!this.#countdown) {
      return;
    }

    super.connectedCallback();
  }

  /**
   * Update the display with positive time remaining.
   *
   * @param {RemainingTime} remaining The time remaining.
   * @returns {void}
   */
  update(remaining) {
    this.#countdown.innerText = `Ends in ${remaining.h0}${remaining.h1}:${remaining.m0}${remaining.m1}:${remaining.s0}${remaining.s1}`;
  }

  /**
   * Update the display with the countdown ended.
   *
   * @returns {void}
   */
  ended() {
    this.#countdown.innerText = "Just ended!";
  }
}

// register the custom elements
customElements.define("big-countdown", BigCountdown);
customElements.define("small-countdown", SmallCountdown);
