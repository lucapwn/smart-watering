$("#notifications-status").prop("checked", localStorage.getItem("notifications") == "on" ? true : false);

$("#temperature-measurement").change(function() {
    $("#temperature-measurement-form").submit();
});

$("#notifications-status").change(function() {
    manage_notifications();
});

$("#reservoir-capacity").change(function() {
    return validate_form();
});

$("#reservoir-shape").change(function() {
    manage_inputs();
});

$("#reservoir-length").change(function() {
    return validate_form();
});

$("#reservoir-width").change(function() {
    return validate_form();
});

$("#reservoir-height").change(function() {
    return validate_form();
});

$("#reservoir-diameter").change(function() {
    return validate_form();
});

$("#reservoir-larger-base-diameter").change(function() {
    return validate_form();
});

$("#reservoir-smaller-base-diameter").change(function() {
    return validate_form();
});

$("#reservoir-larger-base-area").change(function() {
    return validate_form();
});

$("#reservoir-smaller-base-area").change(function() {
    return validate_form();
});

$("#save-reservoir-form").click(function() {
    return validate_form();
});

manage_inputs();

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function manage_notifications() {
    var status = $("#notifications-status").prop("checked");

    if (status) {
        localStorage.setItem("notifications", "on");
        show_alert("Notificações", "As notificações do sistema foram ativadas!", "bottom-right", "rgba(0,0,0,0.2)", "info");
        return;
    }

    localStorage.setItem("notifications", "off");
    $.NotificationApp.send("Notificações", "As notificações do sistema foram desativadas!", "bottom-right", "rgba(0,0,0,0.2)", "info");
}

function manage_inputs() {
    $("#reservoir-shape-form").removeClass("was-validated");

    $("#reservoir-length-div").css("display", "none");
    $("#reservoir-width-div").css("display", "none");
    $("#reservoir-height-div").css("display", "none");
    $("#reservoir-diameter-div").css("display", "none");
    $("#reservoir-larger-base-diameter-div").css("display", "none");
    $("#reservoir-smaller-base-diameter-div").css("display", "none");
    $("#reservoir-larger-base-area-div").css("display", "none");
    $("#reservoir-smaller-base-area-div").css("display", "none");

    $("#reservoir-length").prop("readonly", true);
    $("#reservoir-width").prop("readonly", true);
    $("#reservoir-height").prop("readonly", true);
    $("#reservoir-diameter").prop("readonly", true);
    $("#reservoir-larger-base-diameter").prop("readonly", true);
    $("#reservoir-smaller-base-diameter").prop("readonly", true);
    $("#reservoir-larger-base-area").prop("readonly", true);
    $("#reservoir-smaller-base-area").prop("readonly", true);

    var reservoir_shape = $("#reservoir-shape").val();

    switch (reservoir_shape) {
        case "cube":
            $("#reservoir-height-div").css("display", "block");
            $("#reservoir-height").prop("readonly", false);
            break;

        case "cylinder":
            $("#reservoir-height-div").css("display", "block");
            $("#reservoir-diameter-div").css("display", "block");
            $("#reservoir-length").prop("readonly", false);
            $("#reservoir-height").prop("readonly", false);
            $("#reservoir-diameter").prop("readonly", false);
            break;

        case "parallelepiped":
            $("#reservoir-length-div").css("display", "block");
            $("#reservoir-width-div").css("display", "block");
            $("#reservoir-height-div").css("display", "block");
            $("#reservoir-length").prop("readonly", false);
            $("#reservoir-width").prop("readonly", false);
            $("#reservoir-height").prop("readonly", false);
            break;

        case "cone-trunk":
            $("#reservoir-height-div").css("display", "block");
            $("#reservoir-larger-base-diameter-div").css("display", "block");
            $("#reservoir-smaller-base-diameter-div").css("display", "block");
            $("#reservoir-height").prop("readonly", false);
            $("#reservoir-larger-base-diameter").prop("readonly", false);
            $("#reservoir-smaller-base-diameter").prop("readonly", false);
            break;

        case "pyramid-trunk":
            $("#reservoir-height-div").css("display", "block");
            $("#reservoir-larger-base-area-div").css("display", "block");
            $("#reservoir-smaller-base-area-div").css("display", "block");
            $("#reservoir-height").prop("readonly", false);
            $("#reservoir-larger-base-area").prop("readonly", false);
            $("#reservoir-smaller-base-area").prop("readonly", false);
            break;
    }
}

function validate_form() {
    var status = true;

    var reservoir_capacity = $("#reservoir-capacity").val();
    var reservoir_shape = $("#reservoir-shape").val();
    var reservoir_length = $("#reservoir-length").val();
    var reservoir_width = $("#reservoir-width").val();
    var reservoir_height = $("#reservoir-height").val();
    var reservoir_diameter = $("#reservoir-diameter").val();
    var reservoir_larger_base_diameter = $("#reservoir-larger-base-diameter").val();
    var reservoir_smaller_base_diameter = $("#reservoir-smaller-base-diameter").val();
    var reservoir_larger_base_area = $("#reservoir-larger-base-area").val();
    var reservoir_smaller_base_area = $("#reservoir-smaller-base-area").val();

    manage_inputs();

    if (reservoir_capacity <= 0) {
        $("#reservoir-capacity").removeClass("is-valid");
        $("#reservoir-capacity").addClass("is-invalid");
        status = false;
    } else {
        $("#reservoir-capacity").removeClass("is-invalid");
        $("#reservoir-capacity").addClass("is-valid");
    }

    if (reservoir_shape == "parallelepiped") {
        if (reservoir_length <= 0) {
            $("#reservoir-length").removeClass("is-valid");
            $("#reservoir-length").addClass("is-invalid");
            status = false;
        } else {
            $("#reservoir-length").removeClass("is-invalid");
            $("#reservoir-length").addClass("is-valid");
        }
    }

    if (reservoir_shape == "parallelepiped") {
        if (reservoir_width <= 0) {
            $("#reservoir-width").removeClass("is-valid");
            $("#reservoir-width").addClass("is-invalid");
            status = false;
        } else {
            $("#reservoir-width").removeClass("is-invalid");
            $("#reservoir-width").addClass("is-valid");
        }
    }

    if (reservoir_shape == "cube" || reservoir_shape == "cylinder" || reservoir_shape == "parallelepiped" || reservoir_shape == "cone-trunk" || reservoir_shape == "pyramid-trunk") {
        if (reservoir_height <= 0) {
            $("#reservoir-height").removeClass("is-valid");
            $("#reservoir-height").addClass("is-invalid");
            status = false;
        } else {
            $("#reservoir-height").removeClass("is-invalid");
            $("#reservoir-height").addClass("is-valid");
        }
    }

    if (reservoir_shape == "cylinder") {
        if (reservoir_diameter <= 0) {
            $("#reservoir-diameter").removeClass("is-valid");
            $("#reservoir-diameter").addClass("is-invalid");
            status = false;
        } else {
            $("#reservoir-diameter").removeClass("is-invalid");
            $("#reservoir-diameter").addClass("is-valid");
        }
    }

    if (reservoir_shape == "cone-trunk") {
        if (reservoir_larger_base_diameter <= 0) {
            $("#reservoir-larger-base-diameter").removeClass("is-valid");
            $("#reservoir-larger-base-diameter").addClass("is-invalid");
            status = false;
        } else {
            $("#reservoir-larger-base-diameter").removeClass("is-invalid");
            $("#reservoir-larger-base-diameter").addCLass("is-valid");
        }
        
        if (reservoir_smaller_base_diameter <= 0) {
            $("#reservoir-smaller-base-diameter").removeClass("is-valid");
            $("#reservoir-smaller-base-diameter").addCLass("is-invalid");
            status = false;
        } else {
            $("#reservoir-smaller-base-diameter").removeClass("is-invalid");
            $("#reservoir-smaller-base-diameter").addCLass("is-valid");
        }
    }

    if (reservoir_shape == "pyramid-trunk") {
        if (reservoir_larger_base_area <= 0) {
            $("#reservoir-larger-base-area").removeClass("is-valid");
            $("#reservoir-larger-base-area").addCLass("is-invalid");
            status = false;
        } else {
            $("#reservoir-larger-base-area").removeClass("is-invalid");
            $("#reservoir-larger-base-area").addCLass("is-valid");
        }
    
        if (reservoir_smaller_base_area <= 0) {
            $("#reservoir-smaller-base-area").removeClass("is-valid");
            $("#reservoir-smaller-base-area").addCLass("is-invalid");
            status = false;
        } else {
            $("#reservoir-smaller-base-area").removeClass("is-invalid");
            $("#reservoir-smaller-base-area").addCLass("is-valid");
        }
    }

    return status;
}