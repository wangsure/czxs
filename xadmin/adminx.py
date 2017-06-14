# -*- coding: utf-8 -*-
import xadmin
from models import UserSettings
from xadmin.layout import *
from views import CommAdminView, BaseAdminView
from blog.models import Article, Category, Carousel, Nav, Column,SensorM, News,Sensordata,SiteM,SensorCategory,PositionCategory,Siteandsensor,PointOfInterest
from vmaig_comments.models import Comment
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from vmaig_auth.models import VmaigUser
import  vmaig_auth
from vmaig_auth.forms import VmaigUserCreationForm
from vmaig_system.models import Notification, Link
from django import forms
from django.contrib.gis import admin
# from blog.models import City, District
# from django.contrib.gis.db import models
# from mapwidgets.widgets import GooglePointFieldWidget, GooglePointFieldInlineWidget, GoogleStaticMapWidget, \
#     GoogleStaticOverlayMapWidget
#
#
# class DistrictAdminInline(admin.TabularInline):
#     model = District
#     extra = 3
#     formfield_overrides = {
#         models.PointField: {"widget": GooglePointFieldInlineWidget}
#     }
#
#
# class CityAdminForm(forms.ModelForm):
#     class Meta:
#         model = City
#         fields = "__all__"
#         widgets = {
#             'coordinates': GooglePointFieldWidget,
#             'city_hall': GooglePointFieldWidget,
#         }
#
#
# class CityAdminStaticForm(forms.ModelForm):
#
#     class Meta:
#         model = City
#         fields = "__all__"
#         widgets = {
#             'coordinates': GoogleStaticMapWidget,
#             'city_hall': GoogleStaticOverlayMapWidget,
#         }
#
#
# class CityAdmin(admin.ModelAdmin):
#     list_display = ("name", "coordinates")
#     inlines = (DistrictAdminInline,)
#
#     def get_form(self, request, obj=None, **kwargs):
#         if not obj:
#             self.form = CityAdminForm
#         else:
#             self.form = CityAdminStaticForm
#         return super(CityAdmin, self).get_form(request, obj, **kwargs)
#
#
# class DistrictAdmin(admin.ModelAdmin):
#     formfield_overrides = {
#         models.PointField: {"widget": GoogleStaticOverlayMapWidget}
#     }
#
#
# xadmin.site.register(City, CityAdmin)
# xadmin.site.register(District, DistrictAdmin)





class UserSettingsAdmin(object):
    model_icon = 'fa fa-cog'
    hidden_menu = True
class BaseSetting(object):
    enable_themes=True
    use_bootswatch=True
class GlobalSetting(object):
    #设置base_site.html的Title
    site_title = '土壤墒情大数据云平台后台'
    #设置base_site.html的Footer
    site_footer  = '北京创智新水大数据智能科技有限公司'
    menu_style = "accordion"

    # 菜单设置

class PositionCategoryAdmin(object):
    search_fields = ('name',)
    list_filter = ('status', 'create_time')
    list_display = ('name', 'parent', 'rank', 'status')
    fields = ('name', 'parent', 'rank', 'status')
class SensorCategoryAdmin(object):
    search_fields = ('name',)
    list_filter = ('status', 'create_time')
    list_display = ('name', 'parent', 'rank', 'status')
    fields = ('name', 'parent', 'rank', 'status')
class SiteMAdmin(object):
    search_fields = ('name',)
    list_filter = ('status', 'create_time')
    list_display = ('name', 'parent', 'rank', 'status','create_time','tags', 'position', 'position_map',)
    fields = ('name', 'parent', 'rank', 'status','summary','soildtype','vegtype','tags', 'position', )

    def position_map(self, instance):
        if instance.position is not None:
            return '<img src="http://maps.googleapis.com/maps/api/staticmap?center=%(latitude)s,%(longitude)s&zoom=%(zoom)s&size=%(width)sx%(height)s&maptype=roadmap&markers=%(latitude)s,%(longitude)s&sensor=false&visual_refresh=true&scale=%(scale)s" width="%(width)s" height="%(height)s">' % {
                'latitude': instance.position.latitude,
                'longitude': instance.position.longitude,
                'zoom': 15,
                'width': 100,
                'height': 100,
                'scale': 2
            }

    position_map.allow_tags = True
class SensorandsiteAdmin(object):
    search_fields = ('site', 'sensor')
    list_filter = ('status',)
    list_display = ('site', 'sensor', 'status', 'start_time')
    fields = ('site', 'sensor', 'status', 'start_time')

class SensordataAdmin(object):
    search_fields = ('sensor', 'site')
    list_filter = ('sensor', 'site', 'is_top','create_time')
    list_display = ('title', 'sensor','site','summary', 'is_top', 'create_time','rank')
    fields = ('title', 'sensor','site','summary', 'is_top', 'create_time','rank')

class SensorAdmin(object):
    search_fields = ( 'summary','en_title')
    list_filter = ('site', 'category', 'en_title')
    list_display = ('en_title', 'category', 'author','site',
                    'status', 'is_top', 'update_time','create_time', 'position', 'position_map',)

    fieldsets = (
        (u'基本信息', {
            'fields': ('en_title', 'img',
                       'category', 'tags', 'author','site',
                       'is_top', 'rank', 'status', 'position', 'position_map',)
            }),
        (u'当前描述', {
            'fields': ('content',)
            }),
        (u'传感器描述', {
            'fields': ('summary',)
            }),
        (u'时间', {
            'fields': ('create_time',)
            }),
    )

    def position_map(self, instance):
        if instance.position is not None:
            return '<img src="http://maps.googleapis.com/maps/api/staticmap?center=%(latitude)s,%(longitude)s&zoom=%(zoom)s&size=%(width)sx%(height)s&maptype=roadmap&markers=%(latitude)s,%(longitude)s&sensor=false&visual_refresh=true&scale=%(scale)s" width="%(width)s" height="%(height)s">' % {
                'latitude': instance.position.latitude,
                'longitude': instance.position.longitude,
                'zoom': 15,
                'width': 100,
                'height': 100,
                'scale': 2
            }

    position_map.allow_tags = True
class PointOfInterestAdmin(object):
    list_display = ('name', 'position', 'position_map',)

    def position_map(self, instance):
        if instance.position is not None:
            return '<img src="http://maps.googleapis.com/maps/api/staticmap?center=%(latitude)s,%(longitude)s&zoom=%(zoom)s&size=%(width)sx%(height)s&maptype=roadmap&markers=%(latitude)s,%(longitude)s&sensor=false&visual_refresh=true&scale=%(scale)s" width="%(width)s" height="%(height)s">' % {
                'latitude': instance.position.latitude,
                'longitude': instance.position.longitude,
                'zoom': 15,
                'width': 100,
                'height': 100,
                'scale': 2
            }
    position_map.allow_tags = True


xadmin.site.register(PointOfInterest, PointOfInterestAdmin)
xadmin.site.register(Sensordata, SensordataAdmin)
xadmin.site.register(SensorM, SensorAdmin)
xadmin.site.register(SiteM, SiteMAdmin)
xadmin.site.register(SensorCategory, SensorCategoryAdmin)
xadmin.site.register(PositionCategory, PositionCategoryAdmin)
class ArticleAdmin(object):
    search_fields = ('title', 'summary')
    list_filter = ('status', 'category', 'is_top',
                   'create_time', 'update_time', 'is_top')
    list_display = ('title', 'category', 'author',
                    'status', 'is_top', 'update_time')
    fieldsets = (
        (u'基本信息', {
            'fields': ('title', 'en_title', 'img',
                       'category', 'tags', 'author',
                       'is_top', 'rank', 'status')
            }),
        (u'内容', {
            'fields': ('content',)
            }),
        (u'摘要', {
            'fields': ('summary',)
            }),
        (u'时间', {
            'fields': ('pub_time',)
            }),
    )
class CategoryAdmin(object):
    search_fields = ('name',)
    list_filter = ('status', 'create_time')
    list_display = ('name', 'parent', 'rank', 'status')
    fields = ('name', 'parent', 'rank', 'status')


class ColumnAdmin(object):
    search_fields = ('name',)
    list_display = ('name', 'status', 'create_time')
    list_filter = ('status', 'create_time')
    fields = ('name', 'status', 'article', 'summary')
    filter_horizontal = ('article',)


class CarouselAdmin(object):
    search_fields = ('title',)
    list_display = ('title', 'article', 'img', 'create_time')
    list_filter = ('create_time',)
    fields = ('title', 'article', 'img', 'summary')

xadmin.site.register(Column, ColumnAdmin)
xadmin.site.register(Carousel, CarouselAdmin)
xadmin.site.register(Category, CategoryAdmin)
xadmin.site.register(Article, ArticleAdmin)


class NewsAdmin(object):
    search_fields = ('title', 'summary')
    list_filter = ('news_from', 'create_time')
    list_display = ('title', 'news_from', 'url', 'create_time')
    fields = ('title', 'news_from', 'url', 'summary', 'pub_time')

class NavAdmin(object):
    search_fields = ('name',)
    list_display = ('name', 'url', 'status', 'create_time')
    list_filter = ('status', 'create_time')
    fields = ('name', 'url', 'status')




xadmin.site.register(Nav, NavAdmin)
xadmin.site.register(UserSettings, UserSettingsAdmin)
xadmin.site.register(CommAdminView, GlobalSetting)
xadmin.site.register(BaseAdminView, BaseSetting)
xadmin.site.register(Siteandsensor, SensorandsiteAdmin)
xadmin.site.register(News, NewsAdmin)

class CommentAdmin(object):
    search_fields = ('user__username', 'article__title', 'text')
    list_filter = ('create_time',)
    list_display = ('user', 'article', 'text', 'create_time')
    fields = ('user', 'article', 'parent', 'text')


xadmin.site.register(Comment, CommentAdmin)

class NotificationAdmin(object):
    search_fields = ('text',)
    list_display = ('title', 'from_user', 'to_user', 'create_time')
    list_filter = ('create_time',)
    fields = ('title', 'is_read', 'text',
              'url', 'from_user', 'to_user', 'type')
xadmin.site.register(Notification, NotificationAdmin)

class LinkAdmin(object):
    search_fields = ('title',)
    list_display = ('title', 'url')
    list_filter = ('create_time',)
    fields = ('title', 'url', 'type')



xadmin.site.register(Link, LinkAdmin)

class VmaigUserAdmin(UserAdmin):
    add_form = VmaigUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')
        }),
    )
    fieldsets = (
        (u'基本信息', {'fields': ('username', 'password', 'email')}),
        (u'权限', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (u'时间信息', {'fields': ('last_login', 'date_joined')}),
    )
#xadmin.site.unregister(reversion.revisions)
#xadmin.site.unregister(Group)
#xadmin.site.unregister(VmaigUser)
#xadmin.site.register(VmaigUser, VmaigUserAdmin)