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
`;

document.head.appendChild(style);
const popup = document.querySelector("body > browser-mod-popup");
if (popup) {
  popup.style.cssText += `
    --ha-card-border-width: 0;
  `;
}
