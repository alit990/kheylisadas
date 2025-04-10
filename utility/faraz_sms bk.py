from ippanel import Client, Error, HTTPError, ResponseCode

client = Client("wavXYjF4GzZCGXdSFtW5Wgm09GHPHhJKk5k_1Ul04XQ=")
sender_number = "+983000505"


def send_activation_sms(mobile, activation_code):
    message = f"به خیلی ساده ست خوش آمدید. کد فعالسازی شما {activation_code} است "
    print(sender_number, valid_number(mobile), activation_code)
    try:
        message_id = client.send(sender_number,
                                 [valid_number(mobile)],
                                 message,
                                 "summary")
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


def send_reset_pass_sms(mobile, activation_code):
    message = f"به خیلی ساده ست خوش آمدید. کد تایید برای تغییر رمز شما {activation_code} است "
    print(sender_number, valid_number(mobile), activation_code)
    try:
        message_id = client.send(sender_number,
                                 [valid_number(mobile)],
                                 message,
                                 "summary")
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
    message = f"به جمع کاربران خیلی ساده ست خوش آمدید. نام کاربری شما {username} و کلمه عبور شما {password} است. "
    print(sender_number, valid_number(mobile), username, password)
    try:
        message_id = client.send(sender_number,
                                 [valid_number(mobile)],
                                 message,
                                 "summary")
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


def valid_number(phone):
    return "+98" + phone[-10:]


def standard_number(phone):
    if 9 < len(phone) < 14:
        return "0" + phone[-10:]
    else:
        return None
