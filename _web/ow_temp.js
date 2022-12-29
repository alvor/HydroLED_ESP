function update_temp() {
    $.getJSON("/ow18_temp", function(data) {
        $.each(['temp'], function(index, key) {
            $('#' + key).html(data[key]);
        });
    });
}

$(document).ready(function() {
    setInterval(update_temp, 5000);
    update_temp();
});
