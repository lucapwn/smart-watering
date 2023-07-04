if (localStorage.getItem("notifications") === null) {
    localStorage.setItem("notifications", "on");
}

function show_alert(title, message, position, color, type) {
    var status = localStorage.getItem("notifications");

    if (status == "on") {
        $.NotificationApp.send(title, message, position, color, type);
    }
}
