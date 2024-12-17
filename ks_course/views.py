import ast
import json
import time

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.views.generic.list import ListView
from guardian.shortcuts import assign_perm
from datetime import datetime, timedelta

from ks_account.models import User
from ks_audio.models import AudioCourse, AudioCourseChapter
from ks_course.models import Course, SectionCourse, CourseComment, CourseVisit, TransactionCourse, GiftCourse
from ks_site.models import Avatar
from ks_subscription.forms import GiftCodeForm
from ks_subscription.models import Payment
from ks_vote.models import CourseVote, AudioCourseVote
from utility.choices import PaymentStatus
from utility.http_service import get_client_ip
from utility.context_audio_with_section_preparation import D, Sec, Au, Ch
from utility.utils import group_course_name

MERCHANT = '646f0c9b-d41f-464d-a7d4-7e83ccd6e719'
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
amount = 0  # Rial / Required
description = "نهایی کردن خرید اشتراک خیلی ساده ست"  # Required
email = ''  # Optional
mobile = ''  # Optional
# Important: need to edit for realy server.
# CallbackURL = 'http://127.0.0.1:8000/courses/course-verify-payment/'



# Create your views here.
class CoursesListView(ListView):
    model = Course
    paginate_by = 10
    template_name = 'courses_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CoursesListView, self).get_context_data(*args, **kwargs)
        return context

    def get_queryset(self):
        query = super(CoursesListView, self).get_queryset()
        query = query.filter(is_active=True)
        return query


class CourseDetailView(DetailView):
    model = Course
    template_name = 'course_detail.html'

    def get_queryset(self):
        query = super(CourseDetailView, self).get_queryset()
        query = query.filter(is_active=True)
        return query

    def get_context_data(self, **kwargs):
        has_perm = False
        context = super(CourseDetailView, self).get_context_data()
        course: Course = kwargs.get('object')
        avatar = Avatar.objects.filter(is_main=True).first()
        context['avatar'] = avatar
        # sections_course = course.sectioncourse_set
        sections = SectionCourse.objects.filter(course_id=course.id, is_active=True)
        context['sections'] = sections
        context['comments'] = CourseComment.objects.filter(course_id=course.id, parent=None).order_by(
            '-create_date').prefetch_related('coursecomment_set')
        context['comments_count'] = CourseComment.objects.filter(course_id=course.id).count()
        context['tags'] = course.tags.all()
        user_ip = get_client_ip(self.request)
        user_id = None
        if self.request.user.is_authenticated:
            current_user: User = self.request.user
            user_id = current_user.id
            has_perm = current_user.has_perm('fully_view_course', course)  # guardian library
        context['has_perm'] = has_perm
        has_been_visited = CourseVisit.objects.filter(ip__iexact=user_ip, course_id=course.id).exists()

        if not has_been_visited:
            new_visit = CourseVisit(ip=user_ip, user_id=user_id, course_id=course.id)
            new_visit.save()

        context['course_likes_count'] = CourseVote.objects.filter(course_id=course.id, vote=1).count()
        context['course_dislikes_count'] = CourseVote.objects.filter(course_id=course.id, vote=0).count()
        if CourseVote.objects.filter(course_id=course.id, user_id=user_id).exists():
            # user_course_vote = CourseVote.objects.filter(course_id=course.id, user_id=user_id).first()
            context['course_user_vote'] = CourseVote.objects.filter(course_id=course.id,
                                                                    user_id=user_id).first().vote
        else:
            context['course_user_vote'] = -1
        d = D(course.title)
        sec = []
        for section in sections:
            s = Sec(id=section.id, title=section.title, name=section.name, description=section.description)
            audio_set = AudioCourse.objects.filter(section_course_id=section.id, is_active=True)
            au = []
            for audio in audio_set:
                added_playlist = False
                like_count = AudioCourseVote.objects.filter(audio_id=audio.id, vote=1).count()
                dislike_count = AudioCourseVote.objects.filter(audio_id=audio.id, vote=0).count()
                user_vote = -1
                if self.request.user.is_authenticated:
                    if AudioCourseVote.objects.filter(audio_id=audio.id, user_id=user_id).exists():
                        user_vote = AudioCourseVote.objects.filter(audio_id=audio.id, user_id=user_id).first().vote
                else:
                    if AudioCourseVote.objects.filter(audio_id=audio.id, ip=user_ip).exists():
                        user_vote = AudioCourseVote.objects.filter(audio_id=audio.id, ip=user_ip).first().vote

                if audio.is_lock and not has_perm:
                    a = Au(id=audio.id, title=audio.title, name=audio.name,
                           description=audio.description, is_lock=audio.is_lock)
                else:
                    a = Au(id=audio.id, title=audio.title, name=audio.name,
                           description=audio.description, is_lock=audio.is_lock,
                           like_count=like_count, dislike_count=dislike_count,
                           fake_like_count=audio.fake_like_count, fake_dislike_count=audio.fake_dislike_count,
                           user_vote=user_vote, added_playlist=added_playlist)
                chapter_set = AudioCourseChapter.objects.filter(audio_id=audio.id, is_active=True)
                ch = []
                for chapter in chapter_set:
                    c = Ch(title=chapter.title, name=chapter.name, start_time=chapter.start_sec())
                    ch.append(c)
                a.add_chapter("chapters", ch)
                au.append(a)
            s.add_audio("audios", au)
            sec.append(s)

        d.add_section("sections", sec)
        data_js = str(d).replace("\'", "\"")
        data = json.loads(data_js)
        context['data'] = data
        context['data_js'] = data_js

        context['student_count'] = Group.objects.filter(name=group_course_name(course.title)).count() + 18
        return context


def add_course_comment(request: HttpRequest):
    if request.user.is_authenticated:
        current_user = request.user
        course_id = request.GET.get('course_id')
        course_comment = request.GET.get('course_comment')
        parent_id = request.GET.get('parent_id')
        if request.user.is_staff:
            new_comment = CourseComment(course_id=course_id, text=course_comment, user_id=request.user.id,
                                        parent_id=parent_id, is_allowed=True)
            new_comment.save()
            context = {
                'comments': CourseComment.objects.filter(course_id=course_id, parent=None, is_allowed=True).order_by(
                    '-create_date').prefetch_related('coursecomment_set'),
                'comments_count': CourseComment.objects.filter(course_id=course_id, is_allowed=True).count()
            }
            return render(request, 'includes/comments_partial.html', context)
        else:
            limit_minutes_ago = datetime.now() - timedelta(minutes=15)
            comment_count_in_last_limit_min = CourseComment.objects.filter(
                Q(create_date__gte=limit_minutes_ago) & Q(user=current_user)).count()
            if comment_count_in_last_limit_min < 3:
                new_comment = CourseComment(course_id=course_id, text=course_comment, user_id=request.user.id,
                                            parent_id=parent_id)
                new_comment.save()
                return HttpResponse('no-staff')
            else:
                return HttpResponse('too-many-comment')

    return HttpResponse('response')


@method_decorator(login_required, name='dispatch')
class CoursePriceDetailView(FormMixin, DetailView):
    model = Course
    template_name = 'course_price_detail.html'
    form_class = GiftCodeForm

    def get_success_url(self):
        return reverse('course_price_detail', kwargs={'pk': self.object.pk, 'slug': self.object.slug})

    # def get_queryset(self):
    #     query = super(CoursePriceDetailView2, self).get_queryset()
    #     query = query.filter(is_active=True)
    #     return query

    def get_context_data(self, **kwargs):
        context = super(CoursePriceDetailView, self).get_context_data(**kwargs)
        # current_course: Course = kwargs.get('object')
        current_course: Course = self.get_object()
        user_id = self.request.user.id
        current_user: User = User.objects.filter(id=user_id, is_active=True).first()
        context['gift_form'] = self.get_form()
        has_perm = current_user.has_perm('fully_view_course', current_course)  # guardian library
        context['has_perm'] = has_perm
        context['gift_code'] = 'n'
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        print(form.cleaned_data)
        # context = self.get_context_data()
        context = super(CoursePriceDetailView, self).get_context_data()
        context['gift_form'] = form
        code = form.cleaned_data.get('code')
        course = self.get_object()
        try:
            gift_course = GiftCourse.objects.filter(code__iexact=code, course_id=course.id).first()
            if gift_course:
                course.set_off_price = (gift_course.percentage, gift_course.max)
                # course.save()
                context['code_valid'] = f"کد تخفیف {code} اعمال شد "
                context['course'] = course
                context['gift_code'] = gift_course.code
            else:
                form.add_error(field='code', error=' نامعتبر ')
                # form.add_error(field='code', error='invalid')
                return self.form_invalid(form)
        except ObjectDoesNotExist:
            form.add_error(field='code', error=' نامعتبر ')
            context['gift_code'] = 'n'
            return self.form_invalid(form)

        # return super(AuthorDetail, self).form_valid(form)
        return self.render_to_response(context)

    def form_invalid(self, form):
        print("form not valid")
        # This method is called when valid form data has NOT been POSTed
        # It should return a different HttpResponse
        context = self.get_context_data()
        context['gift_form'] = form
        return self.render_to_response(context)



@login_required
def course_free_gift(request: HttpRequest, *args, **kwargs):
    current_user: User = request.user
    course_id = kwargs['course_id']
    current_course: Course = Course.objects.filter(id=course_id, is_active=True).first()
    code = kwargs['code']
    gift_course = GiftCourse.objects.filter(code__iexact=code, course_id=current_course.id).first()
    if gift_course:
        has_perm = current_user.has_perm('fully_view_course', current_course)  # guardian library
        if has_perm:
            messages.error(request,
                           f"شما در حال حاضر دسترسی کامل به دوره {current_course.name} دارید. ")
            return redirect('failure_page')
        for transaction in TransactionCourse.objects.filter(user_id=current_user.id,
                                                            is_paid=True):  # agar useri transaction active va expire nashode darad natavanad pardakht konad
            if transaction.course_id == current_course.id:
                messages.error(request,
                               f"شما در حال حاضر دسترسی کامل به دوره {current_course.name} دارید. ")
                return redirect('failure_page')
        new_payment = Payment(
            user=current_user,
            method=Payment.GIFT,
            ref_code=0,
            is_paid=True,
            price=0,
            type=Payment.COURSE,
            payment_date=timezone.now()
        )
        transaction, created = \
            TransactionCourse.objects.get_or_create(user_id=current_user.id, course_id=course_id,
                                                    is_paid=False,
                                                    defaults={'in_process': True,
                                                              'status': TransactionCourse.SUCCESS_PAYMENT,
                                                              'info': "اشتراک هدیه - رایگان",
                                                              'try_date': timezone.now()})
        new_payment.save()
        transaction.is_paid = True
        transaction.payment = new_payment
        transaction.save()
        # guardian permission library
        group, created = Group.objects.get_or_create(name=group_course_name(current_course.title))
        assign_perm('fully_view_course', group, current_course)
        current_user.groups.add(group)
        messages.success(request, f" دوره {current_course.name} به صورت رایگان با موفقیت به شما اختصاص داده شد. ")
        return redirect('success_page')
    messages.error(request, 'متاسفانه در تخصیص دوره رایگان به شما خطایی رخ داده است. ')
    return redirect('failure_page')

@login_required
def course_request_payment(request: HttpRequest, *args, **kwargs):
    current_user: User = request.user
    course_id = kwargs['course_id']
    current_course: Course = Course.objects.filter(id=course_id, is_active=True).first()
    code = kwargs['code']
    gift_course = GiftCourse.objects.filter(code__iexact=code, course_id=current_course.id).first()
    if gift_course:
        current_course.set_off_price = (gift_course.percentage, gift_course.max)
    if current_course.off_price is not None:
        total_price = current_course.off_price
    else:
        total_price = current_course.price
    if total_price == 0:
        return redirect(reverse('course_price_detail'))
    has_perm = current_user.has_perm('fully_view_course', current_course)  # guardian library
    if has_perm:
        messages.error(request,
                       f"شما در حال حاضر دسترسی کامل به دوره {current_course.name} دارید. ")
        return redirect('failure_page')
    for transaction in TransactionCourse.objects.filter(user_id=current_user.id,
                                                        is_paid=True):  # agar useri transaction active va expire nashode darad natavanad pardakht konad
        if transaction.course_id == current_course.id:
            messages.error(request,
                           f"شما در حال حاضر دسترسی کامل به دوره {current_course.name} دارید. ")
            return redirect('failure_page')

    # agar useri dar 10 min ghabl in_process darad ke natavanad pardakht konad
    # agar Na in_process ha hame False shavad va betavanad pardakht konad
    limit_minutes_ago = datetime.now() - timedelta(minutes=2)
    count_transaction_in_process_in_last_limit_min = TransactionCourse.objects.filter(
        Q(try_date__gte=limit_minutes_ago) & Q(user=current_user) & Q(in_process=True)).count()
    if count_transaction_in_process_in_last_limit_min > 0:
        messages.error(request,
                       "شما در حال حاضر یک عملیات پرداخت ناتمام دارید. "
                       "لطفا عملیات قبلی را پرداخت یا لغو یا مجددا تلاش کنید.")
        return redirect('failure_page')

    for transaction in TransactionCourse.objects.filter(user_id=current_user.id, in_process=True):
        transaction.in_process = False
        transaction.status = TransactionCourse.BEFORE_PAYMENT
        transaction.save()
    current_transaction, created = \
        TransactionCourse.objects.get_or_create(user_id=current_user.id, course_id=course_id,
                                                is_paid=False, defaults={'in_process': True})

    if not created:
        current_transaction.try_date = timezone.now()
        current_transaction.in_process = True
        current_transaction.save()

    new_payment = Payment(
        user=current_user,
        method=Payment.ZARINPAL,
        ref_code=0,
        is_paid=False,
        price=total_price,
        type=Payment.COURSE
    )
    CallbackURL = reverse_lazy('course_verify_payment')
    req_data = {
        "merchant_id": MERCHANT,
        "amount": total_price * 10,
        "callback_url": str(CallbackURL),
        "description": description,
        "metadata": {"mobile": current_user.mobile, "email": email}
    }
    req_header = {"accept": "application/json", "content-type": "application/json'"}
    req = requests.post(url=ZP_API_REQUEST, data=json.dumps(req_data), headers=req_header)
    authority = req.json()['data']['authority']
    if len(req.json()['errors']) == 0:
        new_payment.status = f'COURSE {current_course.name} - pending - No errors'
        new_payment.save()
        current_transaction.payment = new_payment
        current_transaction.status = TransactionCourse.BEFORE_PAYMENT
        current_transaction.info = f'No errors - NOT PAID - course {current_course}'
        current_transaction.save()
        return redirect(ZP_API_STARTPAY.format(authority=authority))
    else:
        e_code = req.json()['errors']['code']
        e_message = req.json()['errors']['message']
        new_payment.status = f"COURSE {current_course.name} - Error"
        new_payment.error = PaymentStatus.error(e_code)
        new_payment.save()
        current_transaction.status = TransactionCourse.ERROR_BEFORE_PAYMENT
        current_transaction.info = f"Error code: {e_code}, Error Message: {e_message}"
        current_transaction.save()
        return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")


@login_required
def course_verify_payment(request: HttpRequest):
    current_user: User = request.user
    current_transaction: TransactionCourse = TransactionCourse.objects.filter(user_id=current_user.id,
                                                                              in_process=True).first()
    current_payment: Payment = current_transaction.payment
    current_course: Course = current_transaction.course
    total_price = current_course.price

    t_authority = request.GET['Authority']
    if request.GET.get('Status') == 'OK':
        req_header = {"accept": "application/json", "content-type": "application/json'"}
        req_data = {
            "merchant_id": MERCHANT,
            "amount": total_price * 10,
            "authority": t_authority
        }
        req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
        if len(req.json()['errors']) == 0:
            t_status = req.json()['data']['code']
            if t_status == 100:
                ref_str = req.json()['data']['ref_id']
                current_payment.is_paid = True
                current_payment.payment_date = time.time()
                current_payment.ref_code = req.json()['data']['ref_id']
                current_payment.status = 'PAID - No errors'
                current_payment.save()
                current_transaction.in_process = False
                current_transaction.is_paid = True
                current_transaction.status = TransactionCourse.SUCCESS_PAYMENT
                current_transaction.info = f" Success payment by refId = {ref_str} by user: {current_user} for course: {current_course}"
                current_transaction.save()
                # guardian permission library
                group, created = Group.objects.get_or_create(name=group_course_name(current_course.title))
                assign_perm('fully_view_course', group, current_course)
                current_user.groups.add(group)

                return render(request, 'course_payment_detail.html', {
                    'transaction': current_transaction,
                    'success': f'تراکنش شما با کد پیگیری {ref_str} با موفقیت انجام شد'
                })
            elif t_status == 101:
                return render(request, 'course_payment_detail.html', {
                    'transaction': current_transaction,
                    'info': 'این تراکنش قبلا ثبت شده است'
                })
            else:
                # return HttpResponse('Transaction failed.\nStatus: ' + str(
                #     req.json()['data']['message']
                # ))
                return render(request, 'course_payment_detail.html', {
                    'transaction': current_transaction,
                    'error': str(req.json()['data']['message'])
                })
        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']
            # return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
            return render(request, 'course_payment_detail.html', {
                'transaction': current_transaction,
                'error': f"Error code: {e_code}, Error Message: {e_message}"
            })
    else:
        return render(request, 'course_payment_detail.html', {
            'transaction': current_transaction,
            'error': 'پرداخت با خطا مواجه شد / یا شما پرداخت را لغو کردید.'
        })
