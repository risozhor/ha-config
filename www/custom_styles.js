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
  @media (min-width: 768px) {
    .col-m-auto {
        width: auto;
        margin: auto;
    }
  }

  /* Bold */
  @font-face {
    url('/local/fonts/digital-7.ttf') format('ttf');
    font-family: 'digital-7';
    font-weight: 700;
    font-display: swap;
  }

  @font-face {
    font-family: "London Underground LCD Clock";
    src: url("https://db.onlinewebfonts.com/t/56ba446a8480fabd8bb33d65bc7e0b75.eot");
    src: url("https://db.onlinewebfonts.com/t/56ba446a8480fabd8bb33d65bc7e0b75.eot?#iefix")format("embedded-opentype"),
    url("https://db.onlinewebfonts.com/t/56ba446a8480fabd8bb33d65bc7e0b75.woff2")format("woff2"),
    url("https://db.onlinewebfonts.com/t/56ba446a8480fabd8bb33d65bc7e0b75.woff")format("woff"),
    url("https://db.onlinewebfonts.com/t/56ba446a8480fabd8bb33d65bc7e0b75.ttf")format("truetype"),
    url("https://db.onlinewebfonts.com/t/56ba446a8480fabd8bb33d65bc7e0b75.svg#London Underground LCD Clock")format("svg");
}
@font-face {
    font-family: "LCD";
    src: url("https://db.onlinewebfonts.com/t/233131eb5b5e4a930cbdfb07008a09e1.eot");
    src: url("https://db.onlinewebfonts.com/t/233131eb5b5e4a930cbdfb07008a09e1.eot?#iefix")format("embedded-opentype"),
    url("https://db.onlinewebfonts.com/t/233131eb5b5e4a930cbdfb07008a09e1.woff2")format("woff2"),
    url("https://db.onlinewebfonts.com/t/233131eb5b5e4a930cbdfb07008a09e1.woff")format("woff"),
    url("https://db.onlinewebfonts.com/t/233131eb5b5e4a930cbdfb07008a09e1.ttf")format("truetype"),
    url("https://db.onlinewebfonts.com/t/233131eb5b5e4a930cbdfb07008a09e1.svg#LCD")format("svg");
}


`;

document.head.appendChild(style);
const popup = document.querySelector("body > browser-mod-popup");
if (popup) {
  popup.style.cssText += `
    --ha-card-border-width: 0;
  `;
}
console.info("%c  CUSTOM STYLES  \n%c  Version 07.a8  ", 
  "color: white; font-weight: bold; background: #563d7c", 
  "color: #563d7c; font-weight: bold; background: white");
