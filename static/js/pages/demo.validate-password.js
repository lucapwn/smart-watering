var clicked = false;

$("#reset-password").submit(function() {
    clicked = true;
    $("#reset-password").removeClass("was-validated");
    return validate_password();
});

$("#new-password").change(function() {
    if (clicked) {
        return validate_password();
    }
});

$("#confirm-password").change(function() {
    if (clicked) {
        return validate_password();
    }
});

function validate_password() {
    var new_password = $("#new-password");
    var confirm_password = $("#confirm-password");
    var invalid_new_password = $("#new-password-invalid");
    var invalid_confirmation_password = $("#invalid-confirmation-password");

    if (new_password.val().length == 0 && confirm_password.val().length == 0) {
        new_password.removeClass("is-valid");
        new_password.addClass("is-invalid");
        confirm_password.removeClass("is-valid");
        confirm_password.addClass("is-invalid");
        invalid_new_password.text("Informe uma senha válida!");
        invalid_confirmation_password.text("Informe uma senha válida!");
        return false;
    }

    if (new_password.val() != confirm_password.val()) {
        new_password.removeClass("is-valid");
        new_password.addClass("is-invalid");
        confirm_password.removeClass("is-valid");
        confirm_password.addClass("is-invalid");
        invalid_new_password.text("As senhas não conferem!");
        invalid_confirmation_password.text("As senhas não conferem!");
        return false;
    }

    new_password.removeClass("is-invalid");
    new_password.addClass("is-valid");
    confirm_password.removeClass("is-invalid");
    confirm_password.addClass("is-valid");
    
    return true;
}