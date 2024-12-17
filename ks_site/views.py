from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, TemplateView
from django.contrib import messages
from ks_account.models import User
from ks_site.forms import ContactUsModelForm, ContactUsForm
from ks_site.models import ContactUs, FrequentQuestion, SiteSetting
from utility.faraz_sms import standard_number
from django.shortcuts import render, redirect




class AboutUsView(TemplateView):
    template_name = 'about_us.html'
    # model = SiteSetting

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
        context['site_setting'] = setting

        return context


class ContactUsView(View):
    def get(self, request):
        user_id = self.request.user.id
        site_setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
        if request.user.is_authenticated:
            current_user: User = User.objects.filter(id=user_id).first()
            initial_dict = {
                "mobile": current_user.mobile
            }
            contact_us_form = ContactUsForm(request.POST or None, initial=initial_dict)
            context = {
                'form': contact_us_form,
                'site_setting': site_setting
            }
        else:
            context = {
                'site_setting': site_setting
            }
        return render(request, 'contact_us.html', context)

    def post(self, request):
        print("post register view")
        contact_us_form = ContactUsForm(request.POST)
        print(contact_us_form.is_valid())
        # print(contact_us_form)
        if contact_us_form.is_valid():
            mobile = contact_us_form.cleaned_data.get('mobile')
            title = contact_us_form.cleaned_data.get('title')
            message = contact_us_form.cleaned_data.get('message')
            user: User = User.objects.filter(mobile__contains=standard_number(mobile)).first()
            if True:
                contact_us = ContactUs(title=title, user_id=user.id, message=message)
                contact_us.save()
            else:
                # register_form.add_error('mobile', '')
                pass
            messages.success(request, ' پیام شما با موفقیت ارسال شد. ')
            return redirect('success_page')
        context = {
            'form': contact_us_form,
        }

        return render(request, 'contact_us.html', context)


class FrequentQuestionList(ListView):
    template_name = 'frequent_questions.html'
    paginate_by = 10

    def get_queryset(self):
        return FrequentQuestion.objects.filter(is_delete=False, is_active=True).order_by('id')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(FrequentQuestionList, self).get_context_data(**kwargs)
        context['question_count'] = FrequentQuestion.objects.filter(is_delete=False, is_active=True).count()
        return context
