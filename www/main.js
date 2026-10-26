$(document).ready(function() {
  if ($.fn.textillate) {
    $('.text').textillate({
      loop: true,
      sync: true,
      in: {
        effect: 'bounceIn',
      },
      out: {
        effect: 'bounceOut',
      },
    });

    $('.siri-message').textillate({
      loop: true,
      sync: true,
      in: {
        effect: 'fadeInUp',
        sync: true,
      },
      out: {
        effect: 'fadeOutUp',
        sync: true,
      },
    });
  }

  if (window.SiriWave) {
    new SiriWave({
      container: document.getElementById("siri-container"),
      width: 640,
      height: 200,
      style: 'ios9',
      amplitude: 1,
      speed: 0.10,
      autostart: true
    });
  }

  function handleCommandResult(result) {
    if (!result || !result.action) {
      if (result && result.message) {
        $("#assistant-status").text(result.message);
      }
      return;
    }

    if (result.action === "confirm_whatsapp") {
      var confirmed = result.voice_confirmed || window.confirm(
        "Send this WhatsApp message to " + result.phone_number + "?\n\n" + result.message
      );
      if (!confirmed) {
        $("#assistant-status").text("WhatsApp message canceled.");
        return;
      }

      return eel.sendWhatsAppMessage(result.phone_number, result.message, true)()
        .then(function(message) {
          $("#assistant-status").text(message);
        })
        .catch(function(error) {
          console.error("WhatsApp message failed:", error);
          $("#assistant-status").text("WhatsApp could not send the message.");
        });
    }

    if (result.message) {
      $("#assistant-status").text(result.message);
    }
  }

  function submitTextCommand() {
    var input = $("#chatBox");
    var query = input.val().trim();
    if (!query) {
      $("#assistant-status").text("Type a command first.");
      return;
    }
    if (typeof eel === "undefined" || !eel.processTextCommand) {
      $("#assistant-status").text("The assistant connection is unavailable.");
      return;
    }

    $("#assistant-status").text("Working...");
    input.prop("disabled", true);
    $("#chatBtn").prop("disabled", true);
    eel.processTextCommand(query)()
      .then(handleCommandResult)
      .catch(function(error) {
        console.error("Text command failed:", error);
        $("#assistant-status").text("The assistant could not process that command.");
      })
      .finally(function() {
        input.prop("disabled", false).trigger("focus");
        $("#chatBtn").prop("disabled", false);
      });
  }

  function runVoiceConversation() {
    return eel.allCommands()()
      .then(function(result) {
        var response = handleCommandResult(result);
        if (result && result.conversation) {
          return Promise.resolve(response).then(function() {
            return new Promise(function(resolve) {
              window.setTimeout(resolve, 1000);
            });
          }).then(runVoiceConversation);
        }
        return response;
      })
      .catch(function(error) {
        console.error("Assistant command failed:", error);
        $("#assistant-status").text("The assistant could not process that request.");
      });
  }

  $("#chatBtn").on("click", submitTextCommand);
  $("#chatBox").on("keydown", function(event) {
    if (event.key === "Enter") {
      event.preventDefault();
      submitTextCommand();
    }
  });

  $("#micBtn").click(function() {
    var button = $(this);
    button.prop("disabled", true);
    $("#Oval").prop("hidden", true);
    $("#SiriWave").prop("hidden", false);
    $(".siri-message").text("Listening...");
    $("#assistant-status").text("Listening...");

    if (typeof eel === "undefined" || !eel.allCommands) {
      $(".siri-message").text("The assistant connection is unavailable.");
      $("#assistant-status").text("The assistant connection is unavailable.");
      $("#Oval").prop("hidden", false);
      $("#SiriWave").prop("hidden", true);
      button.prop("disabled", false);
      return;
    }

    if (eel.playClickSound) {
      eel.playClickSound()().catch(function(error) {
        console.error("Could not play click sound:", error);
      });
    }

    runVoiceConversation()
      .finally(function() {
        $("#Oval").prop("hidden", false);
        $("#SiriWave").prop("hidden", true);
        button.prop("disabled", false);
      });
  });

});