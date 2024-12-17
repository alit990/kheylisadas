from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify

from utility.utils import unique_slug_generator


class TagCourse(models.Model):
    title = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(default="", blank='True', null=True,
                            db_index=True)  # samsung galaxy s 20 => samsung-galaxy-s-20

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class TagArticle(models.Model):
    title = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(default="", blank='True', null=True,
                            db_index=True)  # samsung galaxy s 20 => samsung-galaxy-s-20

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class TagCCDetail(models.Model):
    title = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(default="", blank='True', null=True,
                            db_index=True)  # samsung galaxy s 20 => samsung-galaxy-s-20

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class TagWeek(models.Model):
    title = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(default="", blank='True', null=True,
                            db_index=True)  # samsung galaxy s 20 => samsung-galaxy-s-20

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


def tag_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(tag_pre_save_receiver, sender=TagArticle)
pre_save.connect(tag_pre_save_receiver, sender=TagCourse)
pre_save.connect(tag_pre_save_receiver, sender=TagCCDetail)
pre_save.connect(tag_pre_save_receiver, sender=TagWeek)
