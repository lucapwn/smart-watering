var allowed = true;
$("#progress-bar-div").css("display", "none");

if (localStorage.getItem("irrigation-test") == null) {
    localStorage.setItem("update-schedule", "update");
    localStorage.setItem("irrigation-test", "off");
}

if (localStorage.getItem("irrigation-test") == "on") {
    localStorage.setItem("irrigation-test", "off");
    progress_bar_animation();
}

$("#confirm-irrigation").click(function() {
    localStorage.setItem("irrigation-test", "on");
    $("#irrigation-test").submit();
});

$("#start-irrigation-test").click(function() {
    var time = $("#irrigation-time").val();
    localStorage.setItem("irrigation-test-time", time);
    validate_action();
});

$("#add-schedule").click(function() {
    $("#irrigation-type").val("day").change();
    localStorage.setItem("update-schedule", "add");
    $("#schedule-modal-label").text("Agendar Irrigação");
    $("#schedule-irrigation").prop("action", "/schedule-irrigation/");

    var modal = new bootstrap.Modal($("#schedule-modal"));
    modal.show();
});

$("#irrigation-type").change(function() {
    manage_inputs();
});

$("#save-form").click(function() {
    if (!validate_form()) {
        return;
    }

    var modal = bootstrap.Modal.getOrCreateInstance($("#schedule-modal"));
    modal.hide();

    $("#schedule-irrigation").submit();
});

manage_inputs();

function manage_inputs() {
    $("#irrigation-type").removeClass("is-valid");
    $("#schedule-irrigation").removeClass("was-validated");

    $("#period-container").css("display", "block");
    $("#irrigation-period").prop("disabled", false);

    $("#per-day").css("display", "none");
    $("#datetime-on").prop("disabled", true);
    $("#datetime-off").prop("disabled", true);

    $("#per-time").css("display", "none");
    $("#time-on").prop("disabled", true);
    $("#time-off").prop("disabled", true);

    $("#per-humidity").css("display", "none");
    $("#humidity").prop("disabled", true);
    $("#night-irrigation").prop("disabled", true);

    $("#per-flow").css("display", "none");
    $("#water-flow").prop("disabled", true);
    $("#time-on-flow").prop("disabled", true);

    var offset = (new Date()).getTimezoneOffset() * 60000;
    var ISO = (new Date(Date.now() - offset)).toISOString().slice(0, -1);
    var datetime = ISO.slice(0, 19);
    var time = ISO.slice(11, 19);
    var type = $("#irrigation-type").val();

    if (type == "day") {
        $("#period-container").css("display", "none");
        $("#irrigation-period").prop("disabled", true);

        $("#per-day").css("display", "block");
        $("#datetime-on").prop("disabled", false);
        $("#datetime-off").prop("disabled", false);

        $("#datetime-on").val(datetime);
        $("#datetime-off").val(datetime);
        
        $("#datetime-on").change(function() {
            return validate_form();
        });
        
        $("#datetime-off").change(function() {
            return validate_form();
        });
    } else if (type == "time") {
        $("#per-time").css("display", "block");
        $("#time-on").prop("disabled", false);
        $("#time-off").prop("disabled", false);

        $(".time").mask("00:00:00", {
            placeholder: "--:--:--"
        });

        $("#time-on").val(time);
        $("#time-off").val(time);

        $("#time-on").change(function() {
            return validate_form();
        });
        
        $("#time-off").change(function() {
            return validate_form();
        });
    } else if (type == "humidity") {
        $("#per-humidity").css("display", "block");
        $("#humidity").prop("disabled", false);
        $("#night-irrigation").prop("disabled", false);

        var humidity = $("#humidity").data("ionRangeSlider");

        humidity.update({
            from: 32,
            to: 64
        });

        $("#humidity").change(function() {
            return validate_form();
        });
    } else {
        $("#per-flow").css("display", "block");
        $("#water-flow").prop("disabled", false);
        $("#time-on-flow").prop("disabled", false);

        $(".time").mask("00:00:00", {
            placeholder: "--:--:--"
        });
        
        $("#time-on-flow").val(time);

        $("#time-on-flow").change(function() {
            return validate_form();
        });
        
        $("#water-flow").change(function() {
            return validate_form();
        });
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function validate_action() {
    if (!allowed) {
        show_alert("Teste de Irrigação", ["A plantação já está sendo irrigada!", "Aguarde a finalização do processo."], "bottom-right", "rgba(0,0,0,0.2)", "error");
        return false;
    }

    var time = localStorage.getItem("irrigation-test-time");
    $("#seconds-text").text(time + " segundos");

    var modal = new bootstrap.Modal($("#standard-modal"));
    modal.show();
}

async function progress_bar_animation() {
    if (!allowed) {
        return;
    }

    var percentage = 0;
    var time = localStorage.getItem("irrigation-test-time");

    $("#progress-bar-div").css("display", "block");
    show_alert("Teste de Irrigação", "A plantação será irrigada em breve!", "bottom-right", "rgba(0,0,0,0.2)", "info");

    for (var i = 1; i <= time; i++) {
        percentage = Math.floor((i * 100) / time);

        $("#progress-bar").css("width", percentage + "%");
        $("#progress-bar").text(percentage + "%");

        await sleep(1000);
        allowed = false;
    }

    await sleep(500);
    $("#progress-bar-div").css("display", "none");
    allowed = true;
}

function validate_form() {
    var irrigation_type = $("#irrigation-type").val();

    var offset = (new Date()).getTimezoneOffset() * 60000;
    var ISO = (new Date(Date.now() - offset)).toISOString().slice(0, -1);
    var current_datetime = ISO.slice(0, 19);
    var pattern_time = /^(?:2[0-3]|[01][0-9]):[0-5][0-9]:[0-5][0-9]$/;

    switch (irrigation_type) {
        case "day":
            var status = true;
            var datetime_on = $("#datetime-on").val();
            var datetime_off = $("#datetime-off").val();

            if (datetime_on.length == 16) {
                $("#datetime-on").val(datetime_on + ":00");
                datetime_on = $("#datetime-on").val();
            }

            if (datetime_off.length == 16) {
                $("#datetime-off").val(datetime_off + ":00");
                datetime_off = $("#datetime-off").val();
            }

            if (datetime_on <= current_datetime || datetime_on >= datetime_off) {
                $("#datetime-on").removeClass("is-valid");
                $("#datetime-on").addClass("is-invalid");
                status = false;
            }
            else {
                $("#datetime-on").removeClass("is-invalid");
                $("#datetime-on").addClass("is-valid");
            }
            
            if (datetime_off <= current_datetime || datetime_off <= datetime_on) {
                $("#datetime-off").removeClass("is-valid");
                $("#datetime-off").addClass("is-invalid");
                status = false;
            }
            else {
                $("#datetime-off").removeClass("is-invalid");
                $("#datetime-off").addClass("is-valid");
            }
    
            if (!status) {
                $("#irrigation-type").addClass("is-valid");
            }
    
            return status;

        case "time":
            var status = true;
            var time_on = $("#time-on").val();
            var time_off = $("#time-off").val();

            if (pattern_time.test(time_on)) {
                $("#time-on").removeClass("is-invalid");
                $("#time-on").addClass("is-valid");
            } else {
                $("#time-on").removeClass("is-valid");
                $("#time-on").addClass("is-invalid");
                status = false;
            }

            if (pattern_time.test(time_off)) {
                $("#time-off").removeClass("is-invalid");
                $("#time-off").addClass("is-valid");
            } else {
                $("#time-off").removeClass("is-valid");
                $("#time-off").addClass("is-invalid");
                status = false;
            }

            if (time_on == time_off) {
                $("#time-on").removeClass("is-valid");
                $("#time-on").addClass("is-invalid");
                $("#time-off").removeClass("is-valid");
                $("#time-off").addClass("is-invalid");
                status = false;
            }

            if (!status) {
                $("#irrigation-type").addClass("is-valid");
                $("#irrigation-period").addClass("is-valid");
            }

            return status;

        case "humidity":
            var status = true;
            var humidity_on = Number($("#humidity").val().split(";")[0]);
            var humidity_off = Number($("#humidity").val().split(";")[1]);

            if (humidity_on < humidity_off) {
                $("#humidity").removeClass("is-invalid");
                $("#humidity").addClass("is-valid");
            } else {
                $("#humidity").removeClass("is-valid");
                $("#humidity").addClass("is-invalid");
                status = false;
            }

            if (!status) {
                $("#irrigation-type").addClass("is-valid");
                $("#irrigation-period").addClass("is-valid");
            }

            return status;

        case "flow":
            var status = true;
            var water_flow = $("#water-flow").val();
            var time_on_flow = $("#time-on-flow").val();

            if (water_flow <= 0) {
                $("#water-flow").removeClass("is-valid");
                $("#water-flow").addClass("is-invalid");
                status = false;
            } else {
                $("#water-flow").removeClass("is-invalid");
                $("#water-flow").addClass("is-valid");
            }

            if (pattern_time.test(time_on_flow)) {
                $("#time-on-flow").removeClass("is-invalid");
                $("#time-on-flow").addClass("is-valid");
            } else {
                $("#time-on-flow").removeClass("is-valid");
                $("#time-on-flow").addClass("is-invalid");
                status = false;
            }

            if (!status) {
                $("#irrigation-type").addClass("is-valid");
                $("#irrigation-period").addClass("is-valid");
            }

            return status;
    }

    return true;
}

$(document).ready(function() {
    $(".update").click(function(event) {
        var id = event.target.id;

        if (!id) {
            return;
        }

        localStorage.setItem("update-schedule-id", id);
        localStorage.setItem("update-schedule", "update");

        var response = JSON.parse(request_get(`/api/irrigation-schedules/${id}/`));

        $("#schedule-modal-label").text("Editar Agenda");
        $("#schedule-irrigation").prop("action", `/schedule-irrigation/update/${id}/`);

        var irrigation_type = response[0].fields.irrigation_type;
        var irrigation_period = response[0].fields.irrigation_period;

        $("#irrigation-type").val(irrigation_type).change();
        $("#irrigation-period").val(irrigation_period).change();

        switch (irrigation_type) {
            case "day":
                var datetime_on = response[0].fields.datetime_on;
                var datetime_off = response[0].fields.datetime_off;
                $("#datetime-on").val(datetime_on).change();
                $("#datetime-off").val(datetime_off).change();
                break;
            
            case "time":
                var time_on = response[0].fields.time_on;
                var time_off = response[0].fields.time_off;
                $("#time-on").val(time_on).change();
                $("#time-off").val(time_off).change();
                break;

            case "humidity":
                var humidity_on = response[0].fields.humidity_on;
                var humidity_off = response[0].fields.humidity_off;
                var night_irrigation = response[0].fields.night_irrigation;
                var humidity = $("#humidity").data("ionRangeSlider");

                humidity.update({
                    from: humidity_on,
                    to: humidity_off
                });

                $("#night-irrigation").prop("checked", night_irrigation);
                break;
            
            case "flow":
                var water_flow = response[0].fields.water_flow;
                var time_on = response[0].fields.time_on;
                $("#water-flow").val(Number(water_flow).toFixed(2)).change();
                $("#time-on-flow").val(time_on).change();
                break;
        }

        var modal = new bootstrap.Modal($("#schedule-modal"));
        modal.show();
    });
});

$(document).ready(function() {
    $(".delete").click(function(event) {
        var id = event.target.id;
        $("#delete-schedule-irrigation").prop("action", `/schedule-irrigation/delete/${id}/`);

        var modal = new bootstrap.Modal($("#delete-schedule-irrigation-modal"));
        modal.show();

        $("#delete-schedule-irrigation-button").click(function() {
            $("#delete-schedule-irrigation").submit();
        });
    });
});

$(document).ready(function() {
    "use strict";
    $("#scroll-horizontal-datatable").DataTable({
        scrollX: !0,
        language: { paginate: { previous: "<i class='mdi mdi-chevron-left'>", next: "<i class='mdi mdi-chevron-right'>" } },
        drawCallback: function () {
            $(".dataTables_paginate > .pagination").addClass("pagination-rounded");
        },
    }),
    $(".dataTables_length select").addClass("form-select form-select-sm m-1"),
    $(".dataTables_length label").addClass("form-label"),
    $(".dataTables_filter").addClass("m-1"),
    $(".dataTables_scroll").addClass("mb-2");
});

$(".readonly").click(function() {
    return false;
});