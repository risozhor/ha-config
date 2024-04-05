const style = document.createElement('style');
style.textContent = `
  .browser-mod-require-interaction {
    display: none;
  }
  .fullheight {
    min-height: calc(100vh - var(--header-height));
  }
  .bt-solid {
    border-top: solid;
  }
  .bb-solid {
    border-bottom: solid;
  }
  .br-solid {
    border-right: solid;
  }
  .bl-solid {
    border-left: solid;
  }
  .border-w1 {
    border-width: 1px;
  }
  .border-w2 {
    border-width: 2px;
  }
  .border-color-divider{
    border-color: var(--divider-color);
  }
  .pulse {
    animation: pulse 1500ms infinite;
  }
  .space-between {
    justify-content: space-between;
    display: flex;
    flex-direction: column;
  }
  /* Bold */
  @font-face {
    src: url('/local/fonts/alarm-clock.woff2') format('woff2'),
    url('/local/fonts/alarm_clock.ttf') format('ttf');
    font-family: 'LCD Bold';
    font-weight: 700;
    font-display: swap;
  }


  /* Light */
  @font-face {
    src: url('/local/fonts/alarm-clock.woff2') format('woff2'),
    url('/local/fonts/alarm_clock.ttf') format('ttf');
    font-family: 'LCD Light';
    font-weight: 300;
    font-display: swap;
  }


  /* Regular */
  @font-face {
    src: url('/local/fonts/alarm-clock.woff2') format('woff2'),
    url('/local/fonts/alarm_clock.ttf') format('ttf');
    font-family: 'LCD Regular';
    font-weight: 400;
    font-display: swap;
  }
`;

document.head.appendChild(style);
const popup = document.querySelector("body > browser-mod-popup");
if (popup) {
  popup.style.cssText += `
    --ha-card-border-width: 0;
  `;
}
