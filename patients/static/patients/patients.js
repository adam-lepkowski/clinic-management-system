var inputs = document.querySelectorAll("div.narrow-row input");

/**
 * Make patient details form inputs read-only
 */
function disableInputs() {
    for (i = 0; i < inputs.length; i++) {
        inputs[i].readOnly = true;
    }
}


/**
 * Enable patient details form inputs
 */
function enableInputs() {
    for (i = 0; i < inputs.length; i++) {
        inputs[i].readOnly = false;
    }
}

/**
 * Restore patient details form default values.
 */
function restoreDefault() {
    var form = document.querySelector(".patient-details-form");
    form.reset();
    for (i = 0; i < inputs.length; i++) {
        inputs[i].readOnly = true;
    }
}

document.querySelector(".edit").addEventListener("click", enableInputs)

disableInputs();