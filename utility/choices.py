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

    PRIMARY = 1
    ADVANCED = 2

    CHOICES_LEVEL = (
        (PRIMARY, 'مقدماتی'),
        (ADVANCED, 'پیشرفته'),
    )


class PaymentStatus:
    PENDING_NO_ERRORS = 'در حال پرداخت'
    PAID_NO_ERRORS = 'پرداخت شده'
    PAYMENT_ERROR = 'خطا در پرداخت'

    @staticmethod
    def error(error_code):
        return f"خطا - کد {error_code}"

    CHOICES = [
        (PENDING_NO_ERRORS, 'در حال پرداخت'),
        (PAID_NO_ERRORS, 'پرداخت شده'),
        (PAYMENT_ERROR, 'خطا در پرداخت'),
    ]
