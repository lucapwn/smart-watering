$(document).ready(function() {
    $(".exported-data").on("change", function() {
        var isChecked = $(".exported-data:checked").length > 0;
        
        if (isChecked) {
            $("#export-csv").prop("disabled", false);
        } else {
            $("#export-csv").prop("disabled", true);
        }
    });
});