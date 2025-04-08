class KSChoices:
    FREE = 1
    LOCKED = 2
    LOCKED_WITH_QUESTION = 3
    LOCKED_RELY_TO_QUESTION = 4

    CHOICES_AUDIO_TYPE = (
        (FREE, 'FREE'),
        (LOCKED, 'LOCKED'),
        (LOCKED_WITH_QUESTION, 'LOCKED_WITH_QUESTION'),
        (LOCKED_RELY_TO_QUESTION, 'LOCKED_RELY_TO_QUESTION'),
    )




class PaymentStatus:
    PENDING_NO_ERRORS = 'در حال پرداخت'
    PAID_NO_ERRORS = 'پرداخت شده'
    PAYMENT_ERROR = 'خطا در پرداخت'
    DUPLICATE_TRANSACTION = 'تراکنش تکراری'
    ZARINPAL_ERROR = 'خطا از زرین پال'
    REQUEST_ERROR = 'خطا در درخواست'
    TIMEOUT_ERROR = 'Timeout'
    CONNECTION_ERROR = 'خطا در اتصال'
    UNKNOWN_ERROR = 'خطای نامشخص'
    LOCKING_ERROR = 'خطا در قفل گذاری'
    DATABASE_ERROR = 'خطای پایگاه داده'
    USER_CANCELLED = 'لغو توسط کاربر'
    INVALID_AMOUNT = 'مبلغ نامعتبر'
    ACTIVE_SUBSCRIPTION = 'اشتراک فعال'
    PENDING_TRANSACTION = 'تراکنش در حال انجام'


    @staticmethod
    def error(error_code):  # This might be redundant, consider removing
        return f"خطا - کد {error_code}"

    CHOICES = [
        (PENDING_NO_ERRORS, 'در حال پرداخت'),
        (PAID_NO_ERRORS, 'پرداخت شده'),
        (PAYMENT_ERROR, 'خطا در پرداخت'),
        (DUPLICATE_TRANSACTION, 'تراکنش تکراری'),
        (ZARINPAL_ERROR, 'خطا از زرین پال'),
        (REQUEST_ERROR, 'خطا در درخواست'),
        (TIMEOUT_ERROR, 'Timeout'),
        (CONNECTION_ERROR, 'خطا در اتصال'),
        (UNKNOWN_ERROR, 'خطای نامشخص'),
        (LOCKING_ERROR, 'خطا در قفل گذاری'),
        (DATABASE_ERROR, 'خطای پایگاه داده'),
        (USER_CANCELLED, 'لغو توسط کاربر'),
        (INVALID_AMOUNT, 'مبلغ نامعتبر'),
        (ACTIVE_SUBSCRIPTION, 'اشتراک فعال'),
        (PENDING_TRANSACTION, 'تراکنش در حال انجام'),
    ]