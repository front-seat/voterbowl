function finishCheckPartial(self, props) {
  const { isWinner } = props;

  if (isWinner) {
    // @ts-ignore-next-line
    const fireworks = new Fireworks.default(document.querySelector(".fireworks"));
    fireworks.start();
    setTimeout(() => fireworks.stop(), 10_000);
  }

  // smoothly scroll to the top of the page after a slight delay
  setTimeout(() => window.scrollTo({ top: 0, behavior: 'smooth' }), 100);
}
