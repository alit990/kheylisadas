from django.db import models
from django.utils import timezone

from ks_account.models import User
from ks_article.models import Article
from ks_audio.models import Audio, AudioWeek, AudioCourse, AudioArticle
from ks_category.models import CCDetail, Week
from ks_course.models import Course


class Question(models.Model):
    CHOICE1 = 1
    CHOICE2 = 2
    CHOICE3 = 3
    CHOICE4 = 4
    CHOICES = (
        (CHOICE1, 'CHOICE1',),
        (CHOICE2, 'CHOICE2',),
        (CHOICE3, 'CHOICE3',),
        (CHOICE4, 'CHOICE4',),
    )
    title = models.CharField(max_length=150, null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    text = models.CharField(max_length=150, null=False, blank=False)
    choice1 = models.CharField(max_length=150, null=False, blank=False)
    choice2 = models.CharField(max_length=150, null=False, blank=False)
    choice3 = models.CharField(max_length=150, null=False, blank=False)
    choice4 = models.CharField(max_length=150, null=False, blank=False)
    answer = models.IntegerField(choices=CHOICES, null=False, blank=False)
    audio = models.ForeignKey(Audio, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    create_date = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.audio} / {self.text} "


class UserAnswer(models.Model):
    CHOICE1 = 1
    CHOICE2 = 2
    CHOICE3 = 3
    CHOICE4 = 4
    CHOICES = (
        (CHOICE1, 'CHOICE1',),
        (CHOICE2, 'CHOICE2',),
        (CHOICE3, 'CHOICE3',),
        (CHOICE4, 'CHOICE4',),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.IntegerField(choices=CHOICES, null=False, blank=False)
    create_date = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.user} / {self.question} "


class ArticleVote(models.Model):
    LIKE = 1
    DISLIKE = 0
    VOTE_CHOICES = (
        (LIKE, 'Like',),
        (DISLIKE, 'Dislike',),
    )
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    vote = models.IntegerField(choices=VOTE_CHOICES, null=True, blank=True)
    ip = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f'{self.article.title} / {self.ip} / {self.user}'


class AudioVote(models.Model):
    LIKE = 1
    DISLIKE = 0
    VOTE_CHOICES = (
        (LIKE, 'Like',),
        (DISLIKE, 'Dislike',),
    )
    audio = models.ForeignKey(Audio, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    vote = models.IntegerField(choices=VOTE_CHOICES, null=True, blank=True)
    ip = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f'{self.audio.title} / {self.ip} / {self.user}'


class AudioWeekVote(models.Model):
    LIKE = 1
    DISLIKE = 0
    VOTE_CHOICES = (
        (LIKE, 'Like',),
        (DISLIKE, 'Dislike',),
    )
    audio = models.ForeignKey(AudioWeek, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    vote = models.IntegerField(choices=VOTE_CHOICES, null=True, blank=True)
    ip = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f'{self.audio.title} / {self.ip} / {self.user}'


class AudioCourseVote(models.Model):
    LIKE = 1
    DISLIKE = 0
    VOTE_CHOICES = (
        (LIKE, 'Like',),
        (DISLIKE, 'Dislike',),
    )
    audio = models.ForeignKey(AudioCourse, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    vote = models.IntegerField(choices=VOTE_CHOICES, null=True, blank=True)
    ip = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f'{self.audio.title} / {self.ip} / {self.user}'


class AudioArticleVote(models.Model):
    LIKE = 1
    DISLIKE = 0
    VOTE_CHOICES = (
        (LIKE, 'Like',),
        (DISLIKE, 'Dislike',),
    )
    audio = models.ForeignKey(AudioArticle, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    vote = models.IntegerField(choices=VOTE_CHOICES, null=True, blank=True)
    ip = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f'{self.audio.title} / {self.ip} / {self.user}'


class CCDetailVote(models.Model):
    LIKE = 1
    DISLIKE = 0
    VOTE_CHOICES = (
        (LIKE, 'Like',),
        (DISLIKE, 'Dislike',),
    )
    ccdetail = models.ForeignKey(CCDetail, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    vote = models.IntegerField(choices=VOTE_CHOICES, null=True, blank=True)
    ip = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f'{self.ccdetail.title} / {self.ip} / {self.user}'


class WeekVote(models.Model):
    LIKE = 1
    DISLIKE = 0
    VOTE_CHOICES = (
        (LIKE, 'Like',),
        (DISLIKE, 'Dislike',),
    )
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    vote = models.IntegerField(choices=VOTE_CHOICES, null=True, blank=True)
    ip = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f'{self.week.title} / {self.ip} / {self.user}'


class CourseVote(models.Model):
    LIKE = 1
    DISLIKE = 0
    VOTE_CHOICES = (
        (LIKE, 'Like',),
        (DISLIKE, 'Dislike',),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    vote = models.IntegerField(choices=VOTE_CHOICES, null=True, blank=True)
    ip = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f'{self.course.title} / {self.ip} / {self.user}'


class AudioPlaylist(models.Model):
    audio = models.ForeignKey(Audio, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.audio.title} / {self.user}'


class AudioWeekPlaylist(models.Model):
    audio = models.ForeignKey(AudioWeek, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.audio.title} / {self.user}'
