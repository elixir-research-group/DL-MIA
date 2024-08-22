function validate() {
  var tableRows = $("table#main-tab>tbody>tr");
  var intentTextFields = $("textarea.intent");

  // check if all intents that are used are specified in the corresponding text fields
  var intentsOK = true;
  for (var i = 0; i < intentTextFields.length; i++) {
    var intentUsed = false;
    for (var j = 0; j < tableRows.length; j++) {
      var checkboxesInRow = $(
        `table#main-tab>tbody>tr:nth-child(${j + 1})>td>input[type=checkbox]`
      );
      // the 1st checkbox does not correspond to any intent
      if (checkboxesInRow[i + 1].checked) {
        intentUsed = true;
        break;
      }
    }
    if (intentUsed && intentTextFields[i].value.trim().length == 0) {
      intentsOK = false;
      break;
    }
  }

  // check if each row has at least one checkbox checked
  var rowsOK = true;
  for (var i = 0; i < tableRows.length; i++) {
    var checkboxesInRow = $(
      `table#main-tab>tbody>tr:nth-child(${i + 1})>td>input[type=checkbox]`
    );
    var rowOK = false;
    for (var j = 0; j < checkboxesInRow.length; j++) {
      if (checkboxesInRow[j].checked) {
        rowOK = true;
        break;
      }
    }
    if (!rowOK) {
      rowsOK = false;
      break;
    }
  }

  // display or hide errors
  if (rowsOK) {
    $("#error-checkboxes").hide();
  } else {
    $("#error-checkboxes").show();
  }
  if (intentsOK) {
    $("#error-intents").hide();
  } else {
    $("#error-intents").show();
  }

  return intentsOK && rowsOK;
}

function setVals() {
  var intents = document.getElementsByClassName("intent");
  for (var i = 0; i < intents.length; i++) {
    elem = document.createElement("input");
    elem.type = "hidden";
    elem.name = "result_i" + i;
    elem.id = "result_i" + i;
    elem.value = intents.item(i).value;

    document.getElementById("form").appendChild(elem);
  }

  var assessments = document.getElementsByClassName("assessment");
  for (var i = 0; i < assessments.length; i++) {
    var item = assessments.item(i);
    if (item.checked) {
      document.getElementById("result_assessments").value += item.id + " ";
    }
  }
}

$(document).ready(function () {
  var submitButton = $("button.otree-btn-next");
  submitButton.attr("disabled", !validate());

  // validate on any assessment
  $("input[type='checkbox'].assessment").change(function () {
    submitButton.attr("disabled", !validate());
  });

  // validate on modification of intents
  $("textarea.intent").on("input", function () {
    submitButton.attr("disabled", !validate());
  });

  // disable row it is marked irrelevant and validate
  $("input[type='checkbox'].assessment-none").change(function () {
    var psgID = $(this).attr("for");
    var checkboxesForPsg = $(`input[type='checkbox'].assessment[for=${psgID}]`);

    if (this.checked) {
      checkboxesForPsg.prop("checked", false);
      checkboxesForPsg.attr("disabled", true);
    } else {
      checkboxesForPsg.removeAttr("disabled");
    }

    submitButton.attr("disabled", !validate());
  });
});
