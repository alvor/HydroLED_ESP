function update_temp() {
    $.getJSON("/api/ow18_api?"+$(decodeURI)[0].URL.split('?')[1], function(data) {
        $.each(['temp'], function(index, key) {
            $('#' + key).html(data[key]);
        });
    });
}

$(document).ready(function() {
    setInterval(update_temp, 1000);
    update_temp();
});
