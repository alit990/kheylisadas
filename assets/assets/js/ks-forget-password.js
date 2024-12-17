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


function sendResetCodeToMobile() {
    $('#forgetMobileAlert').hide();
    $('#forgetInfoAlert').hide();

    const mobile_input = $('#mobile');
    const mobile_number = mobile_input.val();
    const activation_code_input = $('#activation_code');
    const regex = new RegExp('^(\\+98|0)?9\\d{9}$');
    const is_valid_number = regex.test(mobile_number);
    console.log(mobile_number + " validation >>" + is_valid_number);
    if (is_valid_number) {
        $.get('/send-reset-pass-code', {
            mobile_number: mobile_number
        }).then(res => {

            console.log(res);
            const btn_confirm_mobile = $('#btnConfirmMobile');
            if (res === "user-not-exists") {
                Swal.fire({
                    icon: 'error',
                    text: 'کاربری با این شماره تلفن یافت نشد!',
                    showConfirmButton: false,
                    footer: '<a href="register-mobile"> ثبت نام </a>'
                })
            } else if (res === "user-is-not-active") {
                Swal.fire({
                    icon: 'error',
                    text: 'حساب کاربری شما فعال نیست!',
                    showConfirmButton: false,
                    footer: '<a href="register-mobile"> ثبت نام و فعالسازی </a>'
                })
            } else if (res === "reset-pass-sms-sent") {
                mobile_input.attr('disabled', 'disabled');
                $('#activationInput').removeAttr('hidden');
                $('#title_register').html(' <span class="theme-cl">کد تایید تغییر کلمه عبور ارسال شده</span> به شماره '+ mobile_number+ 'را وارد کنید');
                btn_confirm_mobile.removeAttr('onclick');
                btn_confirm_mobile.attr("onclick", "confirmUserResetPassCode()");
                btn_confirm_mobile.text('ثبت کد تایید تغییر کلمه عبور');
                activation_code_input.prop('disabled', false);
                activation_code_input.focus();
                let time_counter = "3:00";
                $('#forgetCountdownTimer').text(time_counter);
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
                    $('#forgetCountdownTimer').html(minutes + ':' + seconds);
                    time_counter = minutes + ':' + seconds;
                }, 1000);

            } else if (res === "error") {
                $('#forgetInfoAlert').show();
                $('#forgetInfoAlert').text('متاسفانه در ارسال پیامک خطایی رخ داده!');
                btn_confirm_mobile.text('تلاش مجدد');

            }
        })
    } else {
        $('#forgetMobileAlert').show();
        $('#forgetMobileAlert').text('لطفا شماره تلفن را به صورت صحیح وارد کنید!');
    }


}

function stopTimerEvent(interval) {
    clearInterval(interval);
    $('#forgetInfoAlert').show();
    $('#forgetInfoAlert').text('کد تایید تغییر کلمه عبور شما منقضی شد. دوباره تلاش کنید.');
    const btn_confirm_mobile = $('#btnConfirmMobile');
    $('#btnConfirmMobile').removeAttr('onclick');
    $('#btnConfirmMobile').attr("onclick", "sendResetCodeToMobile()");
    btn_confirm_mobile.text('تلاش مجدد');
    const activation_code_input = $('#activation_code');
    activation_code_input.prop('disabled', true);

}

function confirmUserResetPassCode() {
    const activation_code_user = $('#activation_code').val();
    const mobile_number = $('#mobile').val();
    $.get('/confirm-reset-pass-code', {
        activation_code_user: activation_code_user,
        mobile_number: mobile_number
    }).then(res => {
        console.log(res);
        if (res === "activation-code-match") {
            const url = "/reset-pass-user?mobile_number=" + mobile_number;
            window.location.href = url;
        }else if (res === "activation-code-not-match") {
            $('#forgetInfoAlert').show();
            $('#forgetInfoAlert').text('کد فعالسازی را به صورت صحیح وارد کنید!');
        }else if( res === "user-not-exists"){
            $('#forgetInfoAlert').show();
            $('#forgetInfoAlert').text('کاربری با این مشخصات یافت نشد!');
        }else{
            $('#forgetInfoAlert').show();
            $('#forgetInfoAlert').text('متاسفانه خطایی رخ داده است!');
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


