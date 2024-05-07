/**
 * 
 * @param {HTMLElement} self 
 */
function(self) {
  onloadAdd(() => {
    const clipboard = self.querySelector(".clipboard");
    const copied = self.querySelector(".copied");
    /** @type {HTMLElement?} */
    const code = self.querySelector(".code");
    if (!clipboard || !copied || !code) {
      return;
    }
    clipboard.addEventListener("click", () => {
      navigator.clipboard.writeText(code.innerText);
      // hide the `clipboard` span; show the `copied` span
      // do this by adding `hidden` class to `clipboard` and
      // removing it from `copied`
      clipboard.classList.add("hidden");
      copied.classList.remove("hidden");
    });
  });
}
