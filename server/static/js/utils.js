/**
 * VoterBowl utility functions accessible globally via $vb.
 * 
 * @namespace $vb
 */
globalThis.$vb = {
  /** 
   * Invoke the callback exactly once, when the DOM is ready.
   * 
   * @param {Function} callback
   * @returns {void}
   */
  onReady: (callback) => {
    if (document.readyState !== 'loading') {
      callback();
    } else {
      const listener = () => {
        document.removeEventListener('DOMContentLoaded', listener);
        callback();
      }
      document.addEventListener('DOMContentLoaded', listener);
    }
  }
};
