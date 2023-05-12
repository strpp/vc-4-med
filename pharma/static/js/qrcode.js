import { showPopupBox, showPopupMsg } from "./popupBox.js"

var socket = io();

socket.on('connect', () => {
  socket.emit('subscribe', {'socket_id': socket.id});
});

socket.on('stream_id', (resp) => {
  console.log(`You should be redirected at: /callback/${resp['stream_id']}`);
  window.location.replace(`/callback/${resp['stream_id']}`);
});

socket.on('error', (resp) => {
  showPopupBox('alert', resp['error'])
});