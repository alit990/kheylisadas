from ippanel import Client, Error, HTTPError, ResponseCode
from jalali_date import date2jalali

sms = Client("wavXYjF4GzZCGXdSFtW5Wgm09GHPHhJKk5k_1Ul04XQ=")
sender_number = "+983000505"
pattern_code_activation = "4k9hfjg4glaq6nn"
pattern_contact_us = "k8w0nobabvblvq4"
pattern_new_subscription = "oseiz9gu23essa9"
pattern_user_pass = "hg0tdziqhmi6j83"
pattern_user_activate = "c7a1lqtz1j2mpt8"
pattern_contact_response = "g6t7bhnews5sir8"


def send_contact_response_sms(mobile, contact_id):
    #  مشترک گرامی، به پیام شما با کد رهگیری %contact_id% در پنل کاربری شما و قسمت (لیست پیام های شما) پاسخ داده شد.
    # (خیلی ساده‌ست)
    # تست
    print(sender_number, valid_number(mobile), contact_id)
    pattern_values = {
        "contact_id": contact_id,
    }
    try:
        message_id = sms.send_pattern(
            pattern_code_activation,  # pattern code
            sender_number,  # originator
            valid_number(mobile),  # recipient
            pattern_values,  # pattern values
        )
        return message_id
    except Error as e:
        print("Error handled => code: %s, message: %s" % (e.code, e.message))
        if e.code == ResponseCode.ErrUnprocessableEntity.value:
            if isinstance(e.message, dict):
                for field in e.message:
                    print("Field: %s, Errors: %s" % (field, e.message[field]))
            else:
                print("Error message is not a dictionary")
    except HTTPError as e:
        print("Error handled => code: %s" % (e))
    return None


def send_activation_sms(mobile, activation_code):
    #  به خیلی ساده‌ست خوش آمدید. کد فعالسازی شما %activation_code% است
    print(sender_number, valid_number(mobile), activation_code)
    pattern_values = {
        "activation_code": activation_code,
    }
    try:
        message_id = sms.send_pattern(
            pattern_code_activation,  # pattern code
            sender_number,  # originator
            valid_number(mobile),  # recipient
            pattern_values,  # pattern values
        )
        return message_id
    except Error as e:
        print("Error handled => code: %s, message: %s" % (e.code, e.message))
        if e.code == ResponseCode.ErrUnprocessableEntity.value:
            if isinstance(e.message, dict):
                for field in e.message:
                    print("Field: %s, Errors: %s" % (field, e.message[field]))
            else:
                print("Error message is not a dictionary")
    except HTTPError as e:
        print("Error handled => code: %s" % (e))
    return None


def send_contact_us_sms(mobile, code):
    # پیام شما با کد رهگیری %code% با موفقیت ثبت شد.
    print(sender_number, valid_number(mobile), code)
    pattern_values = {
        "code": code,
    }
    try:
        message_id = sms.send_pattern(
            pattern_contact_us,  # pattern code
            sender_number,  # originator
            valid_number(mobile),  # recipient
            pattern_values,  # pattern values
        )
        return message_id
    except Error as e:
        print("Error handled => code: %s, message: %s" % (e.code, e.message))
        if e.code == ResponseCode.ErrUnprocessableEntity.value:
            if isinstance(e.message, dict):
                for field in e.message:
                    print("Field: %s, Errors: %s" % (field, e.message[field]))
            else:
                print("Error message is not a dictionary")
    except HTTPError as e:
        print("Error handled => code: %s" % (e))
    return None


def send_new_subscription_sms(mobile, plan_name, plan_duration, end_date):
    #  مشترک عزیز، اشتراک %plan_name% شما با موفقیت فعال شد
    #  و به مدت %plan_duration% روز تا تاریخ %end_date% فعال خواهد بود. (خیلی ساده‌ست)
    if end_date:
        jalali_date = date2jalali(end_date)
        jalali_date_str = jalali_date.strftime('%Y/%m/%d')  # فرمت دلخواه
    else:
        jalali_date_str = "تاریخ مشخص نشده"
    pattern_values = {
        "plan_name": plan_name,
        "plan_duration": plan_duration,
        "end_date": jalali_date_str,
    }
    try:
        message_id = sms.send_pattern(
            pattern_new_subscription,  # pattern code
            sender_number,  # originator
            valid_number(mobile),  # recipient
            pattern_values,  # pattern values
        )
        return message_id
    except Error as e:
        print("Error handled => code: %s, message: %s" % (e.code, e.message))
        if e.code == ResponseCode.ErrUnprocessableEntity.value:
            if isinstance(e.message, dict):
                for field in e.message:
                    print("Field: %s, Errors: %s" % (field, e.message[field]))
            else:
                print("Error message is not a dictionary")
    except HTTPError as e:
        print("Error handled => code: %s" % (e))
    return None


def send_reset_pass_sms(mobile, activation_code):
    message = f"به خیلی ساده ست خوش آمدید. کد تایید برای تغییر رمز شما {activation_code} است "
    print(sender_number, valid_number(mobile), activation_code)
    pattern_values = {
        "activation_code": activation_code,
    }
    try:
        message_id = sms.send_pattern(
            pattern_code_activation,  # pattern code
            sender_number,  # originator
            valid_number(mobile),  # recipient
            pattern_values,  # pattern values
        )
        print(message_id)
        return message_id
        # return 10
    except Error as e:
        print("Error handled => code: %s, message: %s" % (e.code, e.message))

        if e.code == ResponseCode.ErrUnprocessableEntity.value:
            for field in e.message:
                print("Field: %s , Errors: %s" % (field, e.message[field]))
    except HTTPError as e:
        print("Error handled => code: %s" % (e))
    return None


def send_user_pass_sms(mobile, username, password):
    # استفاده از پترن با متغیرهای username و password
    pattern_values = {
        "username": username,
        "password": password,
    }
    try:
        message_id = sms.send_pattern(
            pattern_user_pass,  # کد پترن
            sender_number,  # فرستنده
            valid_number(mobile),  # گیرنده
            pattern_values,  # مقادیر پترن
        )
        print(message_id)
        return message_id
    except Error as e:
        print("Error handled => code: %s, message: %s" % (e.code, e.message))
        if e.code == ResponseCode.ErrUnprocessableEntity.value:
            if isinstance(e.message, dict):
                for field in e.message:
                    print("Field: %s, Errors: %s" % (field, e.message[field]))
            else:
                print("Error message is not a dictionary")
    except HTTPError as e:
        print("Error handled => code: %s" % (e))
    return None
def send_user_activate_sms(mobile, username, password):
    # استفاده از پترن با متغیرهای username و password
    pattern_values = {
        "username": username,
        "password": password,
    }
    try:
        message_id = sms.send_pattern(
            pattern_user_activate,  # کد پترن
            sender_number,  # فرستنده
            valid_number(mobile),  # گیرنده
            pattern_values,  # مقادیر پترن
        )
        print(message_id)
        return message_id
    except Error as e:
        print("Error handled => code: %s, message: %s" % (e.code, e.message))
        if e.code == ResponseCode.ErrUnprocessableEntity.value:
            if isinstance(e.message, dict):
                for field in e.message:
                    print("Field: %s, Errors: %s" % (field, e.message[field]))
            else:
                print("Error message is not a dictionary")
    except HTTPError as e:
        print("Error handled => code: %s" % (e))
    return None


def valid_number(phone):
    return "+98" + phone[-10:]


def standard_number(phone):
    if 9 < len(phone) < 14:
        return "0" + phone[-10:]
    else:
        return None
