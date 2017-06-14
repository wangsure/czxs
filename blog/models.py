# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils import timezone

# from django.contrib.gis.db import models
# from django.contrib.gis.geos import Point
#
# POINT = Point(-104.9903, 39.7392, srid=4326)
#
#
# class City(models.Model):
#     name = models.CharField(max_length=255)
#     coordinates = models.PointField(help_text="To generate the map for your location")
#     city_hall = models.PointField(blank=True, null=True)
#
#     def __unicode__(self):
#         return self.name
#
#
# class District(models.Model):
#     city = models.ForeignKey(City)
#     name = models.CharField(max_length=255)
#     location = models.PointField(help_text="To generate the map for your location")
#
#     def __unicode__(self):
#         return self.name
from django.db import models
from geoposition.fields import GeopositionField


class Zone(models.Model):
    name = models.CharField(max_length = 50 )
    kuerzel = models.CharField(max_length = 3 )
    kn_nr = models.CharField(max_length = 5 )
    beschreibung = models.CharField(max_length = 300 )
    adresse = models.CharField(max_length = 100 )
    position = GeopositionField()


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

# Create your models here.
STATUS = {
        0: u'使用中',
        1: u'未使用',
        2: u'已删除',
}

# 预警信息来源
NEWS = {
        0: u'oschina',
        1: u'chiphell',
        2: u'freebuf',
        3: u'cnBeta',
}

class PointOfInterest(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255,blank=True,null=True)
    city = models.CharField(max_length=50,blank=True,null=True)
    zipcode = models.CharField(max_length=10,blank=True,null=True)
    position = GeopositionField(blank=True)

    class Meta:
        verbose_name_plural = '兴趣点'
        app_label = string_with_title('blog', u"兴趣点坐标")

class Nav(models.Model):
    name = models.CharField(max_length=40, verbose_name=u'内容')
    url = models.CharField(max_length=200, blank=True, null=True,
                           verbose_name=u'指向地址')

    status = models.IntegerField(default=0, choices=STATUS.items(),
                                 verbose_name=u'状态')
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = u"导航条"
        ordering = ['-create_time']
        app_label = string_with_title('blog', u"监测管理")

    def __unicode__(self):
        return self.name

    __str__ = __unicode__

class PositionCategory(models.Model):
    name = models.CharField(max_length=40, verbose_name=u'名称')
    parent = models.ForeignKey('self', default=None, blank=True, null=True,
                               verbose_name=u'上级分组')
    rank = models.IntegerField(default=0, verbose_name=u'排序')
    status = models.IntegerField(default=0, choices=STATUS.items(),
                                 verbose_name=u'状态')

    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = u'监测点分组'
        ordering = ['rank', '-create_time']
        app_label = string_with_title('blog', u"监测管理")

    def __unicode__(self):
        return self.name
class SensorCategory(models.Model):
    name = models.CharField(max_length=40, verbose_name=u'名称')
    parent = models.ForeignKey('self', default=None, blank=True, null=True,
                               verbose_name=u'上级分组')
    rank = models.IntegerField(default=0, verbose_name=u'排序')
    status = models.IntegerField(default=0, choices=STATUS.items(),
                                 verbose_name=u'状态')

    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = u'传感器分组'
        ordering = ['rank', '-create_time']
        app_label = string_with_title('blog', u"监测管理")

    def __unicode__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=40, verbose_name=u'名称')
    parent = models.ForeignKey('self', default=None, blank=True, null=True, verbose_name=u'上级分类')
    rank = models.IntegerField(default=0, verbose_name=u'排序')
    status = models.IntegerField(default=0, choices=STATUS.items(), verbose_name='状态')

    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = u'报告分组'
        ordering = ['rank', '-create_time']
        app_label = string_with_title('blog', u"报告管理")

    def __unicode__(self):
        return self.name

class SiteM(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'所属单位')
    name = models.CharField(max_length=40, verbose_name=u'名称')
    parent = models.ForeignKey(PositionCategory,verbose_name=u'分组')
    rank = models.IntegerField(default=0, verbose_name=u'半径')
    status = models.IntegerField(default=0, choices=STATUS.items(),
                                 verbose_name=u'状态')
    tags = models.CharField(max_length=200, null=True, blank=True, verbose_name=u'标签', help_text=u'用逗号分隔')
    position = GeopositionField(blank=True)
    create_time = models.DateTimeField(u'更新时间', auto_now_add=True)
    summary = models.TextField(verbose_name=u'描述')
    soildtype = models.TextField(verbose_name=u'土壤类型')
    vegtype = models.TextField(verbose_name=u'种植作物')

    class Meta:
        verbose_name_plural = verbose_name = u'监测点管理'
        ordering = ['rank', '-create_time']
        app_label = string_with_title('blog', u"监测管理")

    def __unicode__(self):
       return self.name



class Article(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'发布单位')
    category = models.ForeignKey(Category, verbose_name=u'报告分类')
    title = models.CharField(max_length=100, verbose_name=u'报告标题')
    en_title = models.CharField(max_length=100, verbose_name=u'英文标题')
    img = models.CharField(max_length=200, default='/static/img/article/default.jpg')
    tags = models.CharField(max_length=200, null=True, blank=True, verbose_name=u'标签', help_text=u'用逗号分隔')
    summary = models.TextField(verbose_name=u'报告摘要')
    content = models.TextField(verbose_name=u'报告正文')

    view_times = models.IntegerField(default=0)
    zan_times = models.IntegerField(default=0)

    is_top = models.BooleanField(default=False, verbose_name=u'置顶')
    rank = models.IntegerField(default=0, verbose_name=u'排序')
    status = models.IntegerField(default=0, choices=STATUS.items(), verbose_name='状态')

    pub_time = models.DateTimeField(default=False, verbose_name=u'发布时间')
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间', auto_now=True)

    def get_tags(self):
        return self.tags.split(',')

    class Meta:
        verbose_name_plural = verbose_name = u'报告'
        ordering = ['rank', '-is_top', '-pub_time', '-create_time']
        app_label = string_with_title('blog', u"报告管理")

    def __unicode__(self):
        return self.title

class SensorM(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'所属单位')
    category = models.ForeignKey(SensorCategory, verbose_name=u'分组')
    site = models.ForeignKey(SiteM, verbose_name=u'所处监测点')
    en_title = models.CharField(max_length=100, verbose_name=u'传感器ID')
    img = models.CharField(max_length=200,
                           default='/static/img/article/default.jpg')
    tags = models.CharField(max_length=200, null=True, blank=True,
                            verbose_name=u'标签', help_text=u'用逗号分隔')
    position = GeopositionField(blank=True)
    summary = models.TextField(verbose_name=u'传感器描述')
    content = models.TextField(verbose_name=u'当前描述')

    is_top = models.BooleanField(default=False, verbose_name=u'是否有效')
    rank = models.IntegerField(default=0, verbose_name=u'标志')
    status = models.IntegerField(default=0, choices=STATUS.items(),
                                 verbose_name='状态')
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间', auto_now=True)


    class Meta:
        verbose_name_plural = verbose_name = u'传感器管理'
        ordering = ['rank', '-is_top', '-update_time', '-create_time']
        app_label = string_with_title('blog', u"监测管理")

    def __unicode__(self):
            return self.en_title

class Sensordata(models.Model):
    sensor = models.ForeignKey(SensorM, verbose_name=u'传感器名称')
    site = models.ForeignKey(SiteM, verbose_name=u'所处监测点')
    title = models.CharField(max_length=100, verbose_name=u'测量指标')

    summary = models.TextField(verbose_name=u'采集序列')

    is_top = models.BooleanField(default=False, verbose_name=u'是否有效')
    rank = models.IntegerField(default=0, verbose_name=u'标志')
    create_time = models.DateTimeField(u'采集时间', default=timezone.now())
    class Meta:
        verbose_name_plural = verbose_name = u'传感器数据'
        ordering = ['-is_top', '-create_time']
        app_label = string_with_title('blog', u"监测管理")

    def __unicode__(self):
            return self.title

class Siteandsensor(models.Model):
    site = models.ForeignKey(SiteM, verbose_name=u'监测点')
    sensor = models.ForeignKey(SensorM, verbose_name=u'传感器')
    status = models.IntegerField(default=0, choices=STATUS.items(), verbose_name='状态')


    start_time = models.DateTimeField(u'更新时间',default=timezone.now())

    class Meta:
        verbose_name_plural = verbose_name = u'监测点绑定传感器'
        ordering = ['site','sensor']
        app_label = string_with_title('blog', u"监测管理")



class Column(models.Model):
    name = models.CharField(max_length=40,verbose_name=u'报告专栏内容')
    summary = models.TextField(verbose_name=u'报告专栏摘要')
    article = models.ManyToManyField(Article,verbose_name=u'报告内容')
    status = models.IntegerField(default=0,choices=STATUS.items(),verbose_name='状态')
    create_time = models.DateTimeField(u'创建时间',auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = u'报告专栏'
        ordering = ['-create_time']
        app_label = string_with_title('blog',u"报告管理")

    def __unicode__(self):
        return self.name


class Carousel(models.Model):
    title = models.CharField(max_length=100,verbose_name=u'标题')
    summary = models.TextField(blank=True,null=True,verbose_name=u'摘要')
    img = models.CharField(max_length=200,verbose_name=u'截图图片',default='/static/img/carousel/default.jpg')
    article = models.ForeignKey(Article,verbose_name=u'报告')
    create_time = models.DateTimeField(u'创建时间',auto_now_add=True)
    class Meta:
        verbose_name_plural = verbose_name = u'报告截图轮播'
        ordering = ['-create_time']
        app_label = string_with_title('blog',u"报告管理")


class News(models.Model):
    title = models.CharField(max_length=100, verbose_name=u'消息标题')
    summary = models.TextField(verbose_name=u'消息简介')
    news_from = models.IntegerField(default=0, choices=NEWS.items(), verbose_name='来源')
    url = models.CharField(max_length=200, verbose_name=u'追溯源')

    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    pub_time = models.DateTimeField(default=False, verbose_name=u'发布时间')

    class Meta:
        verbose_name_plural = verbose_name = u'预警消息'
        ordering = ['-title']
        app_label = string_with_title('blog', u"预警管理")

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('news-detail-view', args=(self.pk,))

    def __unicode__(self):
        return self.title

    __str__ = __unicode__
