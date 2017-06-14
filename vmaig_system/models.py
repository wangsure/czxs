# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings

# Create your models here.


IS_READ = {
        0: u'未读',
        1: u'已读'
}

class string_with_title(str):
    """ 用来修改admin中显示的app名称,因为admin app 名称是用 str.title()显示的,
    所以修改str类的title方法就可以实现.
    """
    def __new__(cls, value, title):
        instance = str.__new__(cls, value)
        instance._title = title
        return instance

    def title(self):
        return self._title

    __copy__ = lambda self: self
    __deepcopy__ = lambda self, memodict: self

class Notification(models.Model):
    title = models.CharField(max_length=100, verbose_name=u'标题')
    text = models.TextField(verbose_name=u'内容')
    url = models.CharField(max_length=200, verbose_name=u'连接',
                           null=True, blank=True)
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  default=None, blank=True, null=True,
                                  related_name='from_user_notification_set',
                                  verbose_name=u'发送者')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                related_name='to_user_notification_set',
                                verbose_name=u'接收者')
    type = models.CharField(max_length=20, verbose_name=u'类型',
                            null=True, blank=True)

    is_read = models.IntegerField(default=0, choices=IS_READ.items(),
                                  verbose_name=u'是否读过')

    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间', auto_now=True)

    class Meta:
        verbose_name_plural = verbose_name = u'消息'
        ordering = ['-create_time']
        app_label = string_with_title('vmaig_system', u"系统管理")


class Link(models.Model):
    title = models.CharField(max_length=100, verbose_name=u'标题')
    url = models.CharField(max_length=200, verbose_name=u'连接',
                           null=True, blank=True)
    type = models.CharField(max_length=20, verbose_name=u'类型',
                            null=True, blank=True)

    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间', auto_now=True)

    class Meta:
        verbose_name_plural = verbose_name = u'友情链接'
        ordering = ['-create_time']
        app_label = string_with_title('vmaig_system', u"系统管理")
