import { showPopupBox, showPopupMsg } from "./popupBox.js"

window.onload = function (){
    const XHR = new XMLHttpRequest();
      
    // Define what happens on successful data submission
    XHR.addEventListener("load", async (event) => {
      if(event.target.status == 200) window.location.href = `/success/${event.target.responseText}`;
      else showPopupBox('alert', `${event.target.responseText}`)
    });

    // Define what happens in case of error
    XHR.addEventListener("error", (event) => {
      showPopupBox('alert', 'Something went wrong');});

    // Set up our request
    const url = `/order/wait/${code}`
    XHR.open("GET", url);
    XHR.send()
}