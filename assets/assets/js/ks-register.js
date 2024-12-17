$("button").on("click", function (event) {
    event.preventDefault();
    $("<div>")
        .append("default " + event.type + " prevented")
        .appendTo("#log");

});
$(document).ready(function () {
    console.log("ready!");
    $('#usernameExists').hide();
});


function sendCodeToMobile() {
    $('#mobileAlert').hide();
    $('#infoAlert').hide();
    $('#activationInput').removeAttr('hidden');
    const mobile_input = $('#mobile');
    const mobile_number = mobile_input.val();
    const activation_code_input = $('#activation_code');
    const regex = new RegExp('^(\\+98|0)?9\\d{9}$');
    const is_valid_number = regex.test(mobile_number);
    console.log(mobile_number + " validation >>" + is_valid_number);
    if (is_valid_number) {
        $.get('/send-code', {
            mobile_number: mobile_number
        }).then(res => {
            console.log(res);
            const btn_confirm_mobile = $('#btnConfirmMobile');
            if (res === "mobile-is-already-active") {
                Swal.fire({
                    icon: 'info',
                    text: 'شما قبلا ثبت نام کرده اید! لطفا وارد شوید.',
                    showConfirmButton: false,
                    footer: '<a href="login/"> ورود </a>'
                })
                // const url = "/login"; //
                // window.location.href = url;
            } else if (res === "sms-sent") {
                mobile_input.attr('disabled', 'disabled');
                $('#title_register').html(' <span class="theme-cl">کد ارسال شده</span> به شماره '+ mobile_number+ 'را وارد کنید');
                btn_confirm_mobile.removeAttr('onclick');
                btn_confirm_mobile.attr("onclick", "confirmUserCode()");
                btn_confirm_mobile.text('ثبت کد');
                activation_code_input.prop('disabled', false);
                activation_code_input.focus();
                let time_counter = "3:00";
                $('#countdownTimer').text(time_counter);
                const interval = setInterval(function () {
                    const timer = time_counter.split(':');
                    //by parsing integer, I avoid all extra string processing
                    let minutes = parseInt(timer[0], 10);
                    let seconds = parseInt(timer[1], 10);
                    --seconds;
                    minutes = (seconds < 0) ? --minutes : minutes;
                    if (minutes === 0 && seconds === 0) {
                        // clearInterval(interval);
                        stopTimerEvent(interval);
                    }
                    seconds = (seconds < 0) ? 59 : seconds;
                    seconds = (seconds < 10) ? '0' + seconds : seconds;
                    //minutes = (minutes < 10) ?  minutes : minutes;
                    $('#countdownTimer').html(minutes + ':' + seconds);
                    time_counter = minutes + ':' + seconds;
                }, 1000);

            } else if (res === "too-many-sms-sent") {
                activation_code_input.prop('disabled', true);
                Swal.fire({
                    icon: 'error',
                    text: 'تعداد پیامک های ارسالی در 15 دقیقه اخیر برای شما بیش از 3 عدد بوده است. لطفا دقایقی دیگر مجددا تلاش کنید.',
                    showConfirmButton: true,
                })

            } else if (res === "error") {
                activation_code_input.prop('disabled', true);
                $('#infoAlert').show();
                $('#infoAlert').text('متاسفانه در ارسال پیامک خطایی رخ داده!');
                btn_confirm_mobile.text('تلاش مجدد');

            }
        })
    } else {
        $('#mobileAlert').show();
        $('#mobileAlert').text('لطفا شماره تلفن را به صورت صحیح وارد کنید!');
    }


}

function stopTimerEvent(interval) {
    clearInterval(interval);
    console.log("counter stoped")
    $('#infoAlert').text('کد فعالسازی شما منقضی شد. دوباره تلاش کنید.');
    const btn_confirm_mobile = $('#btnConfirmMobile');
    btn_confirm_mobile.removeAttr('onclick');
    btn_confirm_mobile.attr("onclick", "sendCodeToMobile()");
    btn_confirm_mobile.text('تلاش مجدد');
    const activation_code_input = $('#activation_code');
    activation_code_input.prop('disabled', true);

}

function confirmUserCode() {
    const activation_code_user = $('#activation_code').val();
    const mobile_number = $('#mobile').val();
    $.get('/confirm-user-code', {
        activation_code_user: activation_code_user,
        mobile_number: mobile_number
    }).then(res => {
        console.log(res);
        if (res === "activation-code-match") {
            const url = "/register-user?mobile_number=" + mobile_number;
            window.location.href = url;
        }else{
            $('#infoAlert').show();
            $('#infoAlert').text('کد فعالسازی را به صورت صحیح وارد کنید!');
        }
    })

}

function validateRegister() {
    $('#usernameExists').hide();
    const mobile_number = $('#mobileNumber').val();
    const username = $('#username').val();
    const password = $('#password').val();
    $.get('/validate_user', {
        username: username,
        mobile_number: mobile_number,
        password: password
    }).then(res => {
        console.log(res);
        if (res === "username-already-exists") {
            $('#usernameExists').show(200);
        }

    })


}


