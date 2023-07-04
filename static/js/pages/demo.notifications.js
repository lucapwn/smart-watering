const notification_buttons = document.querySelectorAll(".notification");

notification_buttons.forEach(button => {
    button.addEventListener("click", () => {
        const item = button.id;
        const id = item.split("-")[1];
        const notification = JSON.parse(request_get(`/api/notifications/${id}/`))[0];

        $("#notification-title").text(notification.fields.title);
        $("#notification-message").text(notification.fields.message);

        var myModal = new bootstrap.Modal($("#notification-modal"));
        myModal.show();

        $("#delete-notification-button").click(function() {
            $("#delete-notification-form").prop("action", `/notification/delete/${id}/`);
            $("#delete-notification-form").submit();
        });
    });
});

const maintenance_buttons = document.querySelectorAll(".maintenance");

maintenance_buttons.forEach(button => {
    button.addEventListener("click", () => {
        $.NotificationApp.send("Sistema", "Funcionalidade em manutenção!", "bottom-right", "rgba(0,0,0,0.2)", "info");
    });
});
