$('.js-captcha-refresh').click(function () {
    var $form = $(this).parents('form');
    var url = location.protocol + "//" + window.location.hostname + ":"
        + location.port + "/captcha/refresh/";

    // Make the AJAX-call
    $.getJSON(url, {}, function (json) {
        $form.find('input[name="captcha_field_0"]').val(json.key);
        $form.find('img.captcha').attr('src', json.image_url);
    });

    return false;
});

document.addEventListener('DOMContentLoaded', (event) => {
    let element = document.getElementById('id_captcha_field_1');
    if (element) {
        element.className += ' form-control text-center input-captcha';
    }

});
