import * as htmx from "./htmx.min.js";

/*-----------------------------------------------------------------
 * Check Page Component
 * -----------------------------------------------------------------*/

/**
 * @typedef {object} VoteAmericaData
 * @property {string?} tool The tool that sent the event.
 * @property {string?} event The event that was sent.
 * @property {string?} first_name The first name of the user.
 * @property {string?} last_name The last name of the user.
 * @property {string?} email The email of the user.
 */

/**
 * @typedef {object} VoteAmericaDetail
 * @property {VoteAmericaData?} data The data of the event.
 */

class CheckPage extends HTMLElement {
  connectedCallback() {
    window.addEventListener("VoteAmericaEvent", this.handleVoteAmericaEvent);
  }

  disconnectedCallback() {
    window.removeEventListener("VoteAmericaEvent", this.handleVoteAmericaEvent);
  }

  /**
   * Listen for the VoteAmericaEvent and, if appropriate, finish the verify.
   *
   * @param {CustomEvent<VoteAmericaDetail>} event
   */
  handleVoteAmericaEvent = (event) => {
    const { data } = event.detail;
    if (!data) return;
    if (data?.tool === "verify" && data?.event === "action-finish") {
      if (!data.first_name || !data.last_name || !data.email) {
        console.error("Missing data in event");
        return;
      }
      this.finishVerify(data.first_name, data.last_name, data.email);
    }
  };

  /**
   * Finalize a verify and, possibly, mint a new gift card if all is well.
   *
   * @param {string} first_name
   * @param {string} last_name
   * @param {string} email
   * @returns {Promise<void>}
   */
  async finishVerify(first_name, last_name, email) {
    /** @type {HTMLElement|null} */
    const urgency = this.querySelector(".urgency");
    if (!urgency) {
      console.error("Missing urgency element");
      return;
    }
    try {
      await htmx.ajax("POST", "./finish/", {
        target: urgency,
        values: {
          first_name,
          last_name,
          email,
        },
      });
    } catch (error) {
      console.error(error);
    }
  }
}

customElements.define("check-page", CheckPage);

/*-----------------------------------------------------------------
 * Gift code clipboard behavior
 * -----------------------------------------------------------------*/

class GiftCode extends HTMLElement {
  /** @type {HTMLElement} */
  #code;
  /** @type {HTMLElement} */
  #clipboard;
  /** @type {HTMLElement} */
  #copied;

  connectedCallback() {
    /** @type {HTMLElement|null} */
    const code = this.querySelector(".code");
    /** @type {HTMLElement|null} */
    const clipboard = this.querySelector(".clipboard");
    /** @type {HTMLElement|null} */
    const copied = this.querySelector(".copied");

    if (!code || !clipboard || !copied) {
      return;
    }

    this.#code = code;
    this.#clipboard = clipboard;
    this.#copied = copied;

    this.#clipboard.addEventListener("click", this.handleClick);
  }

  disconnectedCallback() {
    if (this.#clipboard) {
      this.#clipboard.removeEventListener("click", this.handleClick);
    }
  }

  handleClick = () => {
    navigator.clipboard.writeText(this.#code.innerText);
    this.#clipboard.classList.add("hidden");
    this.#copied.classList.remove("hidden");
  };
}

customElements.define("gift-code", GiftCode);

/*-----------------------------------------------------------------
 * Countdown Timers
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
    const endAt = this.dataset.endAt;
    if (!endAt) {
      throw new Error("Missing endAt attribute");
    }
    return new Date(endAt);
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
  /** @type {HTMLElement} */
  #h0;
  /** @type {HTMLElement} */
  #h1;
  /** @type {HTMLElement} */
  #m0;
  /** @type {HTMLElement} */
  #m1;
  /** @type {HTMLElement} */
  #s0;
  /** @type {HTMLElement} */
  #s1;

  connectedCallback() {
    /** @type {HTMLElement|null} */
    const h0 = this.querySelector("[data-number=h0]");
    /** @type {HTMLElement|null} */
    const h1 = this.querySelector("[data-number=h1]");
    /** @type {HTMLElement|null} */
    const m0 = this.querySelector("[data-number=m0]");
    /** @type {HTMLElement|null} */
    const m1 = this.querySelector("[data-number=m1]");
    /** @type {HTMLElement|null} */
    const s0 = this.querySelector("[data-number=s0]");
    /** @type {HTMLElement|null} */
    const s1 = this.querySelector("[data-number=s1]");

    // if any of the numbers are missing, don't start the countdown
    if (!h0 || !h1 || !m0 || !m1 || !s0 || !s1) {
      return;
    }

    this.#h0 = h0;
    this.#h1 = h1;
    this.#m0 = m0;
    this.#m1 = m1;
    this.#s0 = s0;
    this.#s1 = s1;

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
  /** @type {HTMLElement} */
  #countdown;

  connectedCallback() {
    /** @type {HTMLElement|null} */
    const countdown = this.querySelector(".countdown");
    if (!countdown) {
      return;
    }

    this.#countdown = countdown;

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
