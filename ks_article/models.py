from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image
from django_ckeditor_5.fields import CKEditor5Field

from ks_account.models import User
from ks_audio.models import AudioArticle
from ks_course.models import Course
from ks_site.models import AgeCategory
from ks_tag.models import Tag
from utility.choices import KSChoices
from utility.utils import upload_articles_category_image_path, upload_articles_image_path


class ArticleCategoriesManager(models.Manager):
    def get_active_categories(self):
        return self.get_queryset().filter(is_active=True)



class ArticlesManager(models.Manager):
    def get_active_articles(self):
        return self.get_queryset().filter(is_active=True)

    def get_articles_by_category_id(self, category_id):
        return self.get_queryset().filter(category_id=category_id, is_active=True)

    def get_by_id(self, article_id):
        qs = self.get_queryset().filter(id=article_id, is_active=True)
        if qs.count() == 1:
            return qs.first()
        else:
            return None

    # def search(self, query):
    #     lookup = (
    #             Q(title__icontains=query) |
    #             Q(description__icontains=query) |
    #             Q(tag__title__icontains=query)
    #     )
    #     return self.get_queryset().filter(lookup, active=True).distinct()


# Create your models here.
class ArticleCategory(models.Model):
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    # thumb = models.ImageField(upload_to=upload_articles_category_image_path, null=True, blank=True)
    image = models.ImageField(upload_to=upload_articles_category_image_path, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    slug = models.SlugField(default="", blank='True', null=True,
                            db_index=True)  # samsung galaxy s 20 => samsung-galaxy-s-20
    objects = ArticleCategoriesManager()

    def get_count(self):
        return self.article_set.all().count()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


    # class Meta:
    #     verbose_name = 'دسته بندی'
    #     verbose_name_plural = 'دسته بندی ها'

    def __str__(self):
        return self.name


class Article(models.Model):
    category = models.ForeignKey(ArticleCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=150, null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    image = models.ImageField(upload_to=upload_articles_image_path, null=True, blank=True)
    description = models.TextField(null=True)
    description_rich = CKEditor5Field('Description', config_name='default', null=True, blank=True)
    alt_image = models.TextField(null=True, blank=True, max_length=100)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    slug = models.SlugField(default="", blank='True', null=True,
                            db_index=True)  # samsung galaxy s 20 => samsung-galaxy-s-20
    tags = models.ManyToManyField(Tag, blank=True)
    courses = models.ManyToManyField(Course, blank=True)
    audios = models.ManyToManyField(AudioArticle, blank=True)
    age_category = models.ForeignKey(AgeCategory, on_delete=models.CASCADE, null=True, blank=True)
    fake_visit_count = models.IntegerField(default=5)
    fake_like_count = models.IntegerField(default=5)
    fake_dislike_count = models.IntegerField(default=5)


    objects = ArticlesManager()

    def get_absolute_url(self):
        return reverse('article_detail', args=[self.id, self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    # class Meta:
    #     verbose_name = 'فصل دسته'
    #     verbose_name_plural = 'فصل دسته ها'

    def __str__(self):
        return self.title

class ArticleComment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    parent = models.ForeignKey('ArticleComment', null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now)
    text = models.TextField()
    is_allowed = models.BooleanField(default=False)


    def __str__(self):
        return str(self.user)


class ArticleVisit(models.Model):
    article = models.ForeignKey('Article', on_delete=models.CASCADE)
    ip = models.CharField(max_length=30)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f'{self.article.title} / {self.ip}'
