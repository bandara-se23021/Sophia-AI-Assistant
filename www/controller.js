$(document).ready(function() {

  // Display Speak Message
  eel.expose(DisplayMessage) 
  function DisplayMessage(message) {
   $(".siri-message").text(message);
   $("#assistant-status").text(message);
   if ($.fn.textillate) {
    $(".siri-message").textillate('start');
   }
  }

  //Display hood
  eel.expose(ShowHood)
  function ShowHood() {
    $("#Oval").prop("hidden", false);
    $("#SiriWave").prop("hidden", true);
  }

  });
