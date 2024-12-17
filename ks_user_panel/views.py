import json

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required  # for function base
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator  # for class base
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from guardian.shortcuts import get_objects_for_user

from ks_account.models import User
from ks_audio.models import AudioChapter, AudioWeekChapter, Audio, AudioWeek
from ks_category.models import CCDetail, Section
from ks_site.models import Avatar
from ks_subscription.models import Transaction, Payment
from ks_user_panel.forms import EditProfileModelForm, ChangePasswordForm
from ks_vote.models import AudioPlaylist, AudioWeekPlaylist, AudioVote, AudioWeekVote
from utility.context_audio_no_section_preparation import D, Au, Ch
from utility.utils import group_subscription_name, codename_audio_perm, codename_audio_week_perm


@method_decorator(login_required, name='dispatch')
class UserPanelDashboardPage(TemplateView):
    template_name = 'user_panel_dashboard.html'

    def get_context_data(self, *args, **kwargs):
        context = super(UserPanelDashboardPage, self).get_context_data()
        user = self.request.user
        current_user: User = User.objects.filter(id=user.id).first()
        playlist_count = AudioPlaylist.objects.filter(user_id=user.id, is_delete=False).count()
        avatar = Avatar.objects.filter(is_main=True).first()
        context['avatar'] = avatar


        # permission group for subscription
        has_perm = current_user.groups.filter(name=group_subscription_name()).exists()
        print("has perm?", has_perm)
        if Transaction.objects.filter(user_id=current_user.id, is_paid=True, is_expired=False).exists() and has_perm:
            transaction: Transaction = Transaction.objects.filter(
                user_id=current_user.id, is_paid=True, is_expired=False).first()
            if transaction.is_expired_this:
                content_type_audio = ContentType.objects.get_for_model(Audio)
                perm_view_audio, created = Permission.objects.get_or_create(codename=codename_audio_perm(),
                                                                            content_type=content_type_audio)
                content_type_audio_week = ContentType.objects.get_for_model(AudioWeek)
                perm_view_audio_week, created = Permission.objects.get_or_create(
                    codename=codename_audio_week_perm(),
                    content_type=content_type_audio_week)
                plan_group, plan_created = Group.objects.get_or_create(name=group_subscription_name())
                if plan_created:
                    plan_group.permissions.add(perm_view_audio, perm_view_audio_week)
                current_user.groups.remove(plan_group)
                has_perm = False
            context['transaction'] = transaction
            context['has_perm'] = has_perm

        courses = get_objects_for_user(current_user, 'ks_course.fully_view_course')
        context['courses'] = courses
        context['playlist_count'] = playlist_count

        context['current_user'] = user
        return context

@method_decorator(login_required, name='dispatch')
class PaymentsPage(TemplateView):
    template_name = 'user_panel_payments.html'

    def get_context_data(self, *args, **kwargs):
        context = super(PaymentsPage, self).get_context_data()
        user = self.request.user
        current_user: User = User.objects.filter(id=user.id).first()
        avatar = Avatar.objects.filter(is_main=True).first()
        payments = Payment.objects.filter(user_id=current_user.id)
        context['avatar'] = avatar
        context['payments'] = payments
        context['current_user'] = user

        return context


# felan ok nist
@method_decorator(login_required, name='dispatch')
class EditUserProfilePage(View):
    def get(self, request: HttpRequest):
        current_user = User.objects.filter(id=request.user.id).first()
        edit_form = EditProfileModelForm(instance=current_user)
        context = {
            'form': edit_form,
            'current_user': current_user
        }
        return render(request, 'edit_profile.html', context)

    def post(self, request: HttpRequest):
        # avatar va birthday set nemishe ??
        current_user = User.objects.filter(id=request.user.id).first()
        edit_form = EditProfileModelForm(request.POST, request.FILES, instance=current_user)
        print(request.FILES)
        print(edit_form.is_valid())
        for field in edit_form:
            print("Field Error:", field.name, field.errors)
        if edit_form.is_valid():
            print(edit_form.cleaned_data.get("birthday"))
            # edit_form.save(commit=True)

        context = {
            'form': edit_form,
            'current_user': current_user
        }
        return render(request, 'edit_profile.html', context)


@method_decorator(login_required, name='dispatch')
class ChangePasswordPage(View):
    def get(self, request: HttpRequest):
        avatar = Avatar.objects.filter(is_main=True).first()
        context = {
            'form': ChangePasswordForm(),
            'avatar': avatar
        }
        return render(request, 'change_password.html', context)

    def post(self, request: HttpRequest):
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            current_user: User = User.objects.filter(id=request.user.id).first()
            if current_user.check_password(form.cleaned_data.get('current_password')):
                current_user.set_password(form.cleaned_data.get('password'))
                current_user.save()
                logout(request)
                return redirect(reverse('pass_changed_login_page'))
            else:
                form.add_error('current_password', 'کلمه عبور وارد شده اشتباه می باشد')
                # for field in form.errors:
                #     form[field].field.widget.attrs['class'] += ' alert alert-danger'
        avatar = Avatar.objects.filter(is_main=True).first()
        context = {
            'form': form,
            'avatar': avatar
        }
        return render(request, 'change_password.html', context)\


@login_required
def user_panel_menu_parial(request: HttpRequest):
    return render(request, 'components/user_panel_menu_partial.html')


@login_required
def user_panel_playlist_page(request):
    has_perm = False
    user_id = request.user.id
    current_user: User = User.objects.filter(id=user_id, is_active=True).first()
    avatar = Avatar.objects.filter(is_main=True).first()
    context = {
        'avatar': avatar
    }

    # permission group for subscription
    has_perm = current_user.groups.filter(name=group_subscription_name()).exists()
    print("has perm?", has_perm)
    if Transaction.objects.filter(user_id=current_user.id, is_paid=True, is_expired=False).exists() and has_perm:
        transaction: Transaction = Transaction.objects.filter(
            user_id=current_user.id, is_paid=True, is_expired=False).first()
        if transaction.is_expired_this:
            content_type_audio = ContentType.objects.get_for_model(Audio)
            perm_view_audio, created = Permission.objects.get_or_create(codename=codename_audio_perm(),
                                                                        content_type=content_type_audio)
            content_type_audio_week = ContentType.objects.get_for_model(AudioWeek)
            perm_view_audio_week, created = Permission.objects.get_or_create(
                codename=codename_audio_week_perm(),
                content_type=content_type_audio_week)
            plan_group, plan_created = Group.objects.get_or_create(name=group_subscription_name())
            if plan_created:
                plan_group.permissions.add(perm_view_audio, perm_view_audio_week)
            current_user.groups.remove(plan_group)
            has_perm = False
        context['transaction'] = transaction
        context['has_perm'] = has_perm

    print(f"{current_user.username} has perm? {has_perm}")

    # context = {'ccdetail': ccdetail, 'sections': sections, 'comments': comments, 'comments_count': comments_count,
    #            'tags': tags,
    #            'ccdetail_likes_count': CCDetailVote.objects.filter(ccdetail_id=ccdetail.id, vote=1).count(),
    #            'ccdetail_dislikes_count': CCDetailVote.objects.filter(ccdetail_id=ccdetail.id, vote=0).count(),
    #            'ccdetail_user_vote': -1}

    audio_playlist_set = AudioPlaylist.objects.filter(user_id=user_id, is_delete=False)
    audio_week_playlist_set = AudioWeekPlaylist.objects.filter(user_id=user_id, is_delete=False)

    d = D("playlist")
    au = []
    for audio_playlist in audio_playlist_set:
        audio = audio_playlist.audio
        added_playlist = True
        like_count = AudioVote.objects.filter(audio_id=audio.id, vote=1).count()
        dislike_count = AudioVote.objects.filter(audio_id=audio.id, vote=0).count()
        user_vote = -1
        if AudioVote.objects.filter(audio_id=audio.id, user_id=user_id).exists():
            user_vote = AudioVote.objects.filter(audio_id=audio.id, user_id=user_id).first().vote

        if audio.section.ccdetail:
            ccdetail_id = audio.section.ccdetail.id
            if audio.is_lock and not has_perm:
                a = Au(id=audio.id, title=audio.title, name=audio.name,
                       image_url=audio.image.url,
                       audio_url="LOCKED",
                       description=audio.description, is_lock=audio.is_lock,
                       model="CCDetail", model_id=ccdetail_id,
                       added_playlist=added_playlist)
            else:
                a = Au(id=audio.id, title=audio.title, name=audio.name,
                       image_url=audio.image.url,
                       audio_url=audio.file.url,
                       description=audio.description, is_lock=audio.is_lock,
                       type=audio.type,
                       like_count=like_count, dislike_count=dislike_count,
                       fake_like_count=audio.fake_like_count, fake_dislike_count=audio.fake_dislike_count,
                       user_vote=user_vote,
                       model="CCDetail", model_id=ccdetail_id,
                       added_playlist=added_playlist, url=audio.url)
            chapter_set = AudioChapter.objects.filter(audio_id=audio.id, is_active=True)
            ch = []
            for chapter in chapter_set:
                c = Ch(title=chapter.title, name=chapter.name, start_time=chapter.start_sec())
                ch.append(c)
            a.add_chapter("chapters", ch)
            au.append(a)
        else:
            break
    # d.add_audio("audios", au)
    # au = []
    for audio_playlist in audio_week_playlist_set:
        audio = audio_playlist.audio
        added_playlist = True
        like_count = AudioWeekVote.objects.filter(audio_id=audio.id, vote=1).count()
        dislike_count = AudioWeekVote.objects.filter(audio_id=audio.id, vote=0).count()
        user_vote = -1
        if AudioWeekVote.objects.filter(audio_id=audio.id, user_id=user_id).exists():
            user_vote = AudioWeekVote.objects.filter(audio_id=audio.id, user_id=user_id).first().vote

        if audio.section_week.week:
            week_id = audio.section_week.week.id
            if audio.is_lock and not has_perm:
                a = Au(id=audio.id, title=audio.title, name=audio.name,
                       image_url=audio.image.url,
                       audio_url="LOCKED",
                       description=audio.description, is_lock=audio.is_lock,
                       model="Week", model_id=week_id)
            else:
                a = Au(id=audio.id, title=audio.title, name=audio.name,
                       image_url=audio.image.url,
                       audio_url=audio.file.url,
                       description=audio.description, is_lock=audio.is_lock,
                       type=audio.type,
                       like_count=like_count, dislike_count=dislike_count,
                       fake_like_count=audio.fake_like_count, fake_dislike_count=audio.fake_dislike_count,
                       user_vote=user_vote,
                       model="Week", model_id=week_id, url=audio.url)
            chapter_set = AudioWeekChapter.objects.filter(audio_id=audio.id, is_active=True)
            ch = []
            for chapter in chapter_set:
                c = Ch(title=chapter.title, name=chapter.name, start_time=chapter.start_sec())
                ch.append(c)
            a.add_chapter("chapters", ch)
            au.append(a)
        else:
            break
    d.add_audio("audios", au)

    data_js = str(d).replace("\'", "\"")
    data = json.loads(data_js)
    context['data'] = data
    context['data_js'] = data_js
    context['has_perm'] = has_perm
    # question_form = QuestionForm()
    # context['question_form'] = question_form

    return render(request, 'user_playlist.html', context)

