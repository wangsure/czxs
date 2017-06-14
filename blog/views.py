# -*- coding: utf-8 -*-
from django import template
from django import forms
from django.http import HttpResponse, Http404
from django.shortcuts import render, render_to_response
from django.template import Context, loader
from django.views.generic import View, TemplateView, ListView, DetailView
from django.db.models import Q
from django.core.cache import caches
from django.core.exceptions import PermissionDenied
from django.contrib import auth
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from blog.models import Article, Category, Carousel, Column, Nav, News,Sensordata,SiteM,SensorM,PointOfInterest,Siteandsensor
from vmaig_comments.models import Comment
from vmaig_auth.models import VmaigUser
from vmaig_system.models import Link
from vmaig_auth.forms import VmaigUserCreationForm, VmaigPasswordRestForm
from django.conf import settings
import datetime
import time
import json
import logging
import random
import couchdb
import json
import paho.mqtt.client as mqtt
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView, ListView, UpdateView

# from blog.forms import CityCreateForm, CityDetailForm
# from blog.models import City
#
#
# class CityListView(ListView):
#     queryset = City.objects.all()
#     template_name = "cities/list.html"
#     context_object_name = "cities"
#
#
# class CityDetailView(UpdateView):
#     form_class = CityDetailForm
#     model = City
#     template_name = "cities/detail.html"
#
#
# class CityCreateView(FormView):
#     template_name = "cities/form.html"
#     form_class = CityCreateForm
#     success_url = reverse_lazy("cities:list")
#
#     def form_valid(self, form):
#         form.save()
#         return super(CityCreateView, self).form_valid(form)
from blog.models import Zone
from django.shortcuts import render_to_response, get_object_or_404, redirect

def ShowZonen(request):
    zone=Zone.objects.all()
    return render_to_response('zonen.html', {"zone": zone})


def showZoneDetail(request, zone_id):
    zone=Zone.objects.get(id=zone_id)
    return render_to_response('map.html', {"zone": zone})



# 缓存
try:
    cache = caches['memcache']
except ImportError as e:
    cache = caches['default']

# logger
logger = logging.getLogger(__name__)


class BaseMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super(BaseMixin, self).get_context_data(**kwargs)
        try:
            # 网站标题等内容
            context['website_title'] = settings.WEBSITE_TITLE
            context['website_welcome'] = settings.WEBSITE_WELCOME
            # 热门分析报告
            context['hot_article_list'] = \
                Article.objects.order_by("-view_times")[0:10]
            # 导航条
            context['nav_list'] = Nav.objects.filter(status=0)
            # 最新反馈
            context['latest_comment_list'] = \
                Comment.objects.order_by("-create_time")[0:10]
            # 友情链接
            context['links'] = Link.objects.order_by('create_time').all()
            colors = ['primary', 'success', 'info', 'warning', 'danger']
            for index, link in enumerate(context['links']):
                link.color = colors[index % len(colors)]
            # 用户未读消息数
            user = self.request.user
            if user.is_authenticated():
                context['notification_count'] = \
                    user.to_user_notification_set.filter(is_read=0).count()
        except Exception as e:
            logger.error(u'[BaseMixin]加载基本信息出错')

        return context



class IndexView(BaseMixin, ListView):
    template_name = 'blog/index.html'
    context_object_name = 'article_list'
    paginate_by = settings.PAGE_NUM  # 分页--每页的数目

    def get_context_data(self, **kwargs):
        # 轮播
        kwargs['carousel_page_list'] = Carousel.objects.all()
        return super(IndexView, self).get_context_data(**kwargs)

    def get_queryset(self):
        article_list = Article.objects.filter(status=0)
        return article_list


class ArticleView(BaseMixin, DetailView):
    queryset = Article.objects.filter(Q(status=0) | Q(status=1))

    template_name = 'blog/article.html'
    context_object_name = 'article'
    slug_field = 'en_title'

    def get(self, request, *args, **kwargs):
        # 统计分析报告的访问访问次数
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        self.cur_user_ip = ip

        en_title = self.kwargs.get('slug')
        # 获取15*60s时间内访问过这篇分析报告的所有ip
        visited_ips = cache.get(en_title, [])

        # 如果ip不存在就把分析报告的浏览次数+1
        if ip not in visited_ips:
            try:
                article = self.queryset.get(en_title=en_title)
            except Article.DoesNotExist:
                logger.error(u'[ArticleView]访问不存在的分析报告:[%s]' % en_title)
                raise Http404
            else:
                article.view_times += 1
                article.save()
                visited_ips.append(ip)

            # 更新缓存
            cache.set(en_title, visited_ips, 15*60)

        return super(ArticleView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # 反馈
        en_title = self.kwargs.get('slug', '')
        kwargs['comment_list'] = \
            self.queryset.get(en_title=en_title).comment_set.all()
        return super(ArticleView, self).get_context_data(**kwargs)
class SensordataView(BaseMixin, TemplateView):
    #queryset = Sensordata.objects.all()
    template_name = 'blog/news.html'



    def get_context_data(self, **kwargs):
        timeblocks = []
        dataList = []
        dateList = []
        # 获取开始和终止的日期
        start_day = self.request.GET.get("start", "1")
        end_day = self.request.GET.get("end", "7")
        start_day = int(start_day)
        end_day = int(end_day)

        start_date = datetime.datetime.now()


        for x in range(start_day, end_day + 1):
            date = start_date - datetime.timedelta(x)
            dataL = Sensordata.objects.filter(
                create_time__contains=datetime.date(date.year, date.month, date.day)
            ).values_list("summary")
            dateL = Sensordata.objects.filter(
                create_time__contains=datetime.date(date.year, date.month, date.day)
            ).values_list("create_time")

            if dataL:
                dataList.append(dataL)
            if dateL:
                dateList.append(dateL)


        xdata = []
        ydata = []
        ydata2 = []
        ydata3 = []
        ydata4 = []
        ydata5 = []
        ydata6 = []
        ydata7 = []
        ydata8 = []
        ydata9 = []
        ydata10 = []
        ydata11 = []
        ydata12 = []
        ydata13 = []
        ydata14 = []
        ydata15 = []
        ydata16 = []
        testdate=[]

        for d in dateList:
            for dd in d:
                #int(time.mktime(dd[0].timetuple())*1000 )
                thistime = int(time.mktime(dd[0].timetuple())*1000 )
                xdata.append(thistime)
                #testdate.append(datetime.datetime.fromtimestamp(thistime/1000).strftime('%Y-%m-%d %H:%M:%S'))

        for articles in dataList:
            for article in articles:
                sixteenP = article[0].replace('<p>', '').replace('</p>', '').split(',')
                ydata.append(sixteenP[0])
                ydata2.append(sixteenP[1])
                ydata3.append(sixteenP[2])
                ydata4.append(sixteenP[3])
                ydata5.append(sixteenP[4])
                ydata6.append(sixteenP[5])
                ydata7.append(sixteenP[6])
                ydata8.append(sixteenP[7])
                ydata9.append(sixteenP[8])
                ydata10.append(sixteenP[9])
                ydata11.append(sixteenP[10])
                ydata12.append(sixteenP[11])
                ydata13.append(sixteenP[12])
                ydata14.append(sixteenP[13])
                ydata15.append(sixteenP[14])
                ydata16.append(sixteenP[15])

        tooltip_date = "%Y %b %d %H:%M:%S %p"
        extra_serie = {"tooltip": {"y_start": " ", "y_end": " "},
                       "date_format": tooltip_date}

        chartdata = {
            'x': xdata,
            'name1': 'depth 10', 'y1': ydata, 'extra1': extra_serie,
            'name2': 'depth 20', 'y2': ydata2, 'extra2': extra_serie,
            'name3': 'depth 30', 'y3': ydata3, 'extra3': extra_serie,
            'name4': 'depth 40', 'y4': ydata4, 'extra4': extra_serie,
            'name5': 'depth 50', 'y5': ydata5, 'extra5': extra_serie,
            'name6': 'depth 60', 'y6': ydata6, 'extra6': extra_serie,
            'name7': 'depth 70', 'y7': ydata7, 'extra7': extra_serie,
            'name8': 'depth 80', 'y8': ydata8, 'extra8': extra_serie,
            'name9': 'depth 90', 'y9': ydata9, 'extra9': extra_serie,
            'name10': 'depth 100', 'y10': ydata10, 'extra10': extra_serie,
            'name11': 'depth 110', 'y11': ydata11, 'extra11': extra_serie,
            'name12': 'depth 120', 'y12': ydata12, 'extra12': extra_serie,
            'name13': 'depth 130', 'y13': ydata13, 'extra13': extra_serie,
            'name14': 'depth 140', 'y14': ydata14, 'extra14': extra_serie,
            'name15': 'depth 150', 'y15': ydata15, 'extra15': extra_serie,
            'name16': 'depth 160', 'y16': ydata16, 'extra16': extra_serie
        }
        charttype = "lineWithFocusChart"
        chartcontainer = 'linewithfocuschart_container'  # container name
        data = {
            'charttype': charttype,
            'chartdata': chartdata,
            'chartcontainer': chartcontainer,
            'extra': {
                'x_is_date': True,
                'x_axis_format': ' %b %d %H',
                'tag_script_js': True,
                'jquery_on_ready': True,
            }
        }

        # extra_serie = {}
        #
        # chartdata = {
        #     'x': xdata,
        #     'name1': 'series 1', 'y1': ydata, 'extra1': extra_serie,
        #     'name2': 'depth 20', 'y2': ydata2, 'extra2': extra_serie,
        #     'name3': 'depth 30', 'y3': ydata3, 'extra3': extra_serie,
        #     'name4': 'depth 40', 'y4': ydata4, 'extra4': extra_serie,
        #     'name5': 'depth 50', 'y5': ydata5, 'extra5': extra_serie,
        #     'name6': 'depth 60', 'y6': ydata6, 'extra6': extra_serie,
        #     'name7': 'depth 70', 'y7': ydata7, 'extra7': extra_serie,
        #     'name8': 'depth 80', 'y8': ydata8, 'extra8': extra_serie,
        #     'name9': 'depth 90', 'y9': ydata9, 'extra9': extra_serie,
        #     'name10': 'depth 100', 'y10': ydata10, 'extra10': extra_serie,
        #     'name11': 'depth 110', 'y11': ydata11, 'extra11': extra_serie,
        #     'name12': 'depth 120', 'y12': ydata12, 'extra12': extra_serie,
        #     'name13': 'depth 130', 'y13': ydata13, 'extra13': extra_serie,
        #     'name14': 'depth 140', 'y14': ydata14, 'extra14': extra_serie,
        #     'name15': 'depth 150', 'y15': ydata15, 'extra15': extra_serie,
        #     'name16': 'depth 160', 'y16': ydata16, 'extra16': extra_serie
        # }
        # charttype = "lineChart"
        # chartcontainer = 'linechart_container'  # container name
        # data = {
        #     'charttype': charttype,
        #     'chartdata': chartdata,
        #     'chartcontainer': chartcontainer,
        #     'extra': {
        #         'x_is_date': False,
        #         'x_axis_format': '',
        #         'tag_script_js': True,
        #         'jquery_on_ready': False,
        #     }
        # }
        return dict(super(SensordataView, self).get_context_data(**kwargs).items() + data.items())


class RealtimeView(BaseMixin, TemplateView):
    content="eeee"

    #paho
    def on_connect(client, userdata, rc):
        print("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("hahaha")
    #
    # # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        msgstr = str(msg.payload)
        jsonOb = json.loads(msgstr)
        content = jsonOb["content"]
    # queryset = Sensordata.objects.all()
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set("admin","password")

    client.connect("115.146.94.53", 61613, 60)
    # client.loop_forever()

    template_name = 'blog/realtime.html'
    # Couchdb


    def get_context_data(self, **kwargs):
        couch = couchdb.Server('http://115.146.94.53:5984')
        db = couch['czmqtt']  # existing
        timeblocks = []
        dataList = []
        dateList = []
        xdata = []
        ydata = []
        ydata2 = []
        ydata3 = []
        ydata4 = []
        ydata5 = []
        ydata6 = []
        ydata7 = []
        ydata8 = []
        ydata9 = []
        ydata10 = []
        ydata11 = []
        ydata12 = []
        ydata13 = []
        ydata14 = []
        ydata15 = []
        ydata16 = []

        for d in dateList:
            for dd in d:
                thistime = int(time.mktime(dd[0].timetuple()) * 1000)
                xdata.append(thistime)

        # test pie chart
        nb_element = 100
        start_time = int(time.mktime(datetime.datetime(2012, 6, 1).timetuple()) * 1000)
        # articles = self.queryset.all()
        for articles in dataList:
            for article in articles:
                sixteenP = article[0].split(',')
                ydata.append(sixteenP[0])
                ydata2.append(sixteenP[1])
                ydata3.append(sixteenP[2])
                ydata4.append(sixteenP[3])
                ydata5.append(sixteenP[4])
                ydata6.append(sixteenP[5])
                ydata7.append(sixteenP[6])
                ydata8.append(sixteenP[7])
                ydata9.append(sixteenP[8])
                ydata10.append(sixteenP[9])
                ydata11.append(sixteenP[10])
                ydata12.append(sixteenP[11])
                ydata13.append(sixteenP[12])
                ydata14.append(sixteenP[13])
                ydata15.append(sixteenP[14])
                ydata16.append(sixteenP[15])

        tooltip_date = "%d %b %Y %H:%M:%S %p"
        extra_serie = {"tooltip": {"y_start": "There are ", "y_end": " records"},
                       "date_format": tooltip_date}

        chartdata = {
            'x': xdata,
            'name1': 'depth 10', 'y1': ydata, 'extra1': extra_serie,
            'name2': 'depth 20', 'y2': ydata2, 'extra2': extra_serie,
            'name3': 'depth 30', 'y3': ydata3, 'extra3': extra_serie,
            'name4': 'depth 40', 'y4': ydata4, 'extra4': extra_serie,
            'name5': 'depth 50', 'y5': ydata5, 'extra5': extra_serie,
            'name6': 'depth 60', 'y6': ydata6, 'extra6': extra_serie,
            'name7': 'depth 70', 'y7': ydata7, 'extra7': extra_serie,
            'name8': 'depth 80', 'y8': ydata8, 'extra8': extra_serie,
            'name9': 'depth 90', 'y9': ydata9, 'extra9': extra_serie,
            'name10': 'depth 100', 'y10': ydata10, 'extra10': extra_serie,
            'name11': 'depth 110', 'y11': ydata11, 'extra11': extra_serie,
            'name12': 'depth 120', 'y12': ydata12, 'extra12': extra_serie,
            'name13': 'depth 130', 'y13': ydata13, 'extra13': extra_serie,
            'name14': 'depth 140', 'y14': ydata14, 'extra14': extra_serie,
            'name15': 'depth 150', 'y15': ydata15, 'extra15': extra_serie,
            'name16': 'depth 160', 'y16': ydata16, 'extra16': extra_serie
        }
        charttype = "lineWithFocusChart"
        chartcontainer = 'linewithfocuschart_container'  # container name
        data = {
            'charttype': charttype,
            'chartdata': chartdata,
            'chartcontainer': chartcontainer,
            'extra': {
                'x_is_date': True,
                'x_axis_format': '%d %b %Y %H',
                'tag_script_js': True,
                'jquery_on_ready': True,
            }
        }
        kwargs['content'] = self.content

        return dict(super(RealtimeView, self).get_context_data(**kwargs).items() + data.items())


class ArticleView(BaseMixin, DetailView):
    queryset = Article.objects.filter(Q(status=0) | Q(status=1))

    template_name = 'blog/article.html'
    context_object_name = 'article'
    slug_field = 'en_title'

    def get(self, request, *args, **kwargs):
        # 统计分析报告的访问访问次数
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        self.cur_user_ip = ip

        en_title = self.kwargs.get('slug')
        # 获取15*60s时间内访问过这篇分析报告的所有ip
        visited_ips = cache.get(en_title, [])

        # 如果ip不存在就把分析报告的浏览次数+1
        if ip not in visited_ips:
            try:
                article = self.queryset.get(en_title=en_title)
            except Article.DoesNotExist:
                logger.error(u'[ArticleView]访问不存在的分析报告:[%s]' % en_title)
                raise Http404
            else:
                article.view_times += 1
                article.save()
                visited_ips.append(ip)

            # 更新缓存
            cache.set(en_title, visited_ips, 15 * 60)

        return super(ArticleView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # 反馈
        en_title = self.kwargs.get('slug', '')
        kwargs['comment_list'] = \
            self.queryset.get(en_title=en_title).comment_set.all()
        return super(ArticleView, self).get_context_data(**kwargs)


class MapdataView(BaseMixin, TemplateView):
    # queryset = Sensordata.objects.all()
    template_name = 'blog/maps.html'


    def get_context_data(self, **kwargs):
        pois = Siteandsensor.objects.all()
        poissite=SiteM.objects.all()
        poisensor=SensorM.objects.all()


        context = super(MapdataView, self).get_context_data(**kwargs)  # Add in a QuerySet of all the books
        context['poisensor'] = poisensor
        context['poissite'] = poissite
        return context


class AllView(BaseMixin, ListView):
    template_name = 'blog/all.html'
    context_object_name = 'article_list'

    def get_context_data(self, **kwargs):
        kwargs['category_list'] = Category.objects.all()
        kwargs['PAGE_NUM'] = settings.PAGE_NUM
        return super(AllView, self).get_context_data(**kwargs)

    def get_queryset(self):
        article_list = Article.objects.filter(
            status=0
        ).order_by("-pub_time")[0:settings.PAGE_NUM]
        return article_list

    def post(self, request, *args, **kwargs):
        val = self.request.POST.get("val", "")
        sort = self.request.POST.get("sort", "time")
        start = self.request.POST.get("start", 0)
        end = self.request.POST.get("end", settings.PAGE_NUM)

        start = int(start)
        end = int(end)

        if sort == "time":
            sort = "-pub_time"
        elif sort == "recommend":
            sort = "-view_times"
        else:
            sort = "-pub_time"

        if val == "all":
            article_list = \
                Article.objects.filter(status=0).order_by(sort)[start:end+1]
        else:
            try:
                article_list = Category.objects.get(
                                   name=val
                               ).article_set.filter(
                                   status=0
                               ).order_by(sort)[start:end+1]
            except Category.DoesNotExist:
                logger.error(u'[AllView]此分类不存在:[%s]' % val)
                raise PermissionDenied

        isend = len(article_list) != (end-start+1)

        article_list = article_list[0:end-start]

        html = ""
        for article in article_list:
            html += template.loader.get_template(
                        'blog/include/all_post.html'
                    ).render(template.Context({'post': article}))

        mydict = {"html": html, "isend": isend}
        return HttpResponse(
            json.dumps(mydict),
            content_type="application/json"
        )



class SearchView(BaseMixin, ListView):
    template_name = 'blog/search.html'
    context_object_name = 'article_list'
    paginate_by = settings.PAGE_NUM

    def get_context_data(self, **kwargs):
        kwargs['s'] = self.request.GET.get('s', '')
        return super(SearchView, self).get_context_data(**kwargs)

    def get_queryset(self):
        # 获取搜索的关键字
        s = self.request.GET.get('s', '')
        # 在分析报告的标题,summary和tags中搜索关键字
        article_list = Article.objects.only(
            'title', 'summary', 'tags'
        ).filter(
            Q(title__icontains=s) |
            Q(summary__icontains=s) |
            Q(tags__icontains=s),
            status=0
        )
        return article_list


class TagView(BaseMixin, ListView):
    template_name = 'blog/tag.html'
    context_object_name = 'article_list'
    paginate_by = settings.PAGE_NUM

    def get_queryset(self):
        tag = self.kwargs.get('tag', '')
        article_list = \
            Article.objects.only('tags').filter(tags__icontains=tag, status=0)

        return article_list


class CategoryView(BaseMixin, ListView):
    template_name = 'blog/category.html'
    context_object_name = 'article_list'
    paginate_by = settings.PAGE_NUM

    def get_queryset(self):
        category = self.kwargs.get('category', '')
        try:
            article_list = \
                Category.objects.get(name=category).article_set.all()
        except Category.DoesNotExist:
            logger.error(u'[CategoryView]此分类不存在:[%s]' % category)
            raise Http404

        return article_list


class UserView(BaseMixin, TemplateView):
    template_name = 'blog/user.html'

    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated():
            logger.error(u'[UserView]用户未登陆')
            return render(request, 'blog/login.html')

        slug = self.kwargs.get('slug')

        if slug == 'changetx':
            self.template_name = 'blog/user_changetx.html'
        elif slug == 'changepassword':
            self.template_name = 'blog/user_changepassword.html'
        elif slug == 'changeinfo':
            self.template_name = 'blog/user_changeinfo.html'
        elif slug == 'message':
            self.template_name = 'blog/user_message.html'
        elif slug == 'notification':
            self.template_name = 'blog/user_notification.html'

        return super(UserView, self).get(request, *args, **kwargs)

        logger.error(u'[UserView]不存在此接口')
        raise Http404

    def get_context_data(self, **kwargs):
        context = super(UserView, self).get_context_data(**kwargs)

        slug = self.kwargs.get('slug')

        if slug == 'notification':
            context['notifications'] = \
                self.request.user.to_user_notification_set.order_by(
                    '-create_time'
                ).all()

        return context


class ColumnView(BaseMixin, ListView):
    queryset = Column.objects.all()
    template_name = 'blog/column.html'
    context_object_name = 'article_list'
    paginate_by = settings.PAGE_NUM

    def get_context_data(self, **kwargs):
        column = self.kwargs.get('column', '')
        try:
            kwargs['column'] = Column.objects.get(name=column)
        except Column.DoesNotExist:
            logger.error(u'[ColumnView]访问专栏不存在: [%s]' % column)
            raise Http404

        return super(ColumnView, self).get_context_data(**kwargs)

    def get_queryset(self):
        column = self.kwargs.get('column', '')
        try:
            article_list = Column.objects.get(name=column).article.all()
        except Column.DoesNotExist:
            logger.error(u'[ColumnView]访问专栏不存在: [%s]' % column)
            raise Http404

        return article_list


class NewsView(BaseMixin, TemplateView):
    template_name = 'blog/realeg/testreal.html'

    def get_context_data(self, **kwargs):
        timeblocks = []

        # 获取开始和终止的日期
        start_day = self.request.GET.get("start", "0")
        end_day = self.request.GET.get("end", "6")
        start_day = int(start_day)
        end_day = int(end_day)

        start_date = datetime.datetime.now()

        # 获取url中时间断的预警信息
        for x in range(start_day, end_day+1):
            date = start_date - datetime.timedelta(x)
            news_list = News.objects.filter(
                pub_time__year=date.year,
                pub_time__month=date.month,
                pub_time__day=date.day
            )

            if news_list:
                timeblocks.append(news_list)

        kwargs['timeblocks'] = timeblocks
        kwargs['active'] = start_day/7  # li中那个显示active


        #test pie chart
        nb_element = 100
        start_time = int(time.mktime(datetime.datetime.now().timetuple()) * 1000)

        xdata = range(nb_element)
        xdata = map(lambda x: start_time + x * 1000000, xdata)
        ydata = [i * random.randint(1, 10) for i in range(nb_element)]#datetime.datetime.now().second
        ydata2 = map(lambda x: x *4, ydata)
        ydata3 = map(lambda x: x *3, ydata)
        ydata4 = map(lambda x: x *2, ydata)

        tooltip_date = "%d %b %Y %H:%M:%S %p"
        extra_serie = {"tooltip": {"y_start": "The total value is", "y_end": " s"},
                       "date_format": tooltip_date}

        chartdata = {
            'x': xdata,
            'name1': 'depth 10', 'y1': ydata, 'extra1': extra_serie,
            'name2': 'depth 20', 'y2': ydata2, 'extra2': extra_serie,
            'name3': 'depth 30', 'y3': ydata3, 'extra3': extra_serie,
            'name4': 'depth 40', 'y4': ydata4, 'extra4': extra_serie
        }
        charttype = "lineWithFocusChart"
        chartcontainer = 'linewithfocuschart_container'  # container name
        data = {
            'charttype': charttype,
            'chartdata': chartdata,
            'chartcontainer': chartcontainer,
            'extra': {
                'x_is_date': True,
                'x_axis_format': '%d %b %Y %H',
                'tag_script_js': True,
                'jquery_on_ready': True,
            }
        }


        return dict(super(NewsView, self).get_context_data(**kwargs).items()+data.items())

class NewsnewView(BaseMixin, TemplateView):
    template_name = 'blog/newsnew.html'

    def get_context_data(self, **kwargs):
        timeblocks = []

        # 获取开始和终止的日期
        start_day = self.request.GET.get("start", "0")
        end_day = self.request.GET.get("end", "6")
        start_day = int(start_day)
        end_day = int(end_day)

        start_date = datetime.datetime.now()

        # 获取url中时间断的预警信息
        for x in range(start_day, end_day + 1):
            date = start_date - datetime.timedelta(x)
            news_list = News.objects.filter(
                pub_time__year=date.year,
                pub_time__month=date.month,
                pub_time__day=date.day
            )

            if news_list:
                timeblocks.append(news_list)

        kwargs['timeblocks'] = timeblocks
        kwargs['active'] = start_day / 7  # li中那个显示active

        # test pie chart
        nb_element = 10
        xdata = range(nb_element)
        ydata = [random.randint(1, 10) for i in range(nb_element)]
        ydata2 = map(lambda x: x * 2, ydata)
        ydata3 = map(lambda x: x * 3, ydata)
        ydata4 = map(lambda x: x * 4, ydata)

        extra_serie = {"tooltip": {"y_start": "There are ", "y_end": " calls"}}

        chartdata = {
            'x': xdata,
            'name1': 'series 1', 'y1': ydata, 'extra1': extra_serie,
            'name2': 'series 2', 'y2': ydata2, 'extra2': extra_serie,
            'name3': 'series 3', 'y3': ydata3, 'extra3': extra_serie,
            'name4': 'series 4', 'y4': ydata4, 'extra4': extra_serie
        }

        nb_element = 100
        start_time = int(time.mktime(datetime.datetime(2012, 6, 1).timetuple()) * 1000)
        xdata = range(nb_element)
        xdata = map(lambda x: start_time + x * 1000000000, xdata)
        ydata = [i + random.randint(1, 10) for i in range(nb_element)]
        ydata2 = map(lambda x: x * 2, ydata)

        tooltip_date = "%d %b %Y %H:%M:%S %p"
        extra_serie = {"tooltip": {"y_start": "There are ", "y_end": " calls"},
                       "date_format": tooltip_date}

        date_chartdata = {
            'x': xdata,
            'name1': 'series 1', 'y1': ydata, 'extra1': extra_serie,
            'name2': 'series 2', 'y2': ydata2, 'extra2': extra_serie,
        }

        nb_element = 10
        xdata = range(nb_element)
        ydata = [i + random.randint(-10, 10) for i in range(nb_element)]
        ydata2 = map(lambda x: x * 2, ydata)

        extra_serie = {"tooltip": {"y_start": "", "y_end": " mins"}}

        hori_chartdata = {
            'x': xdata,
            'name1': 'series 1', 'y1': ydata, 'extra1': extra_serie,
            'name2': 'series 2', 'y2': ydata2, 'extra2': extra_serie,
        }

        nb_element = 50
        xdata = [i + random.randint(1, 10) for i in range(nb_element)]
        ydata1 = [i * random.randint(1, 10) for i in range(nb_element)]
        ydata2 = map(lambda x: x * 2, ydata1)
        ydata3 = map(lambda x: x * 5, ydata1)

        kwargs1 = {'shape': 'circle'}
        kwargs2 = {'shape': 'cross'}
        kwargs3 = {'shape': 'triangle-up'}

        extra_serie1 = {"tooltip": {"y_start": "", "y_end": " balls"}}

        sc_chartdata = {
            'x': xdata,
            'name1': 'series 1', 'y1': ydata1, 'kwargs1': kwargs1, 'extra1': extra_serie1,
            'name2': 'series 2', 'y2': ydata2, 'kwargs2': kwargs2, 'extra2': extra_serie1,
            'name3': 'series 3', 'y3': ydata3, 'kwargs3': kwargs3, 'extra3': extra_serie1
        }
        sc_charttype = "scatterChart"
        sc_chartcontainer = 'scatterchart_container'  # container name

        charttype = "multiBarChart"
        chartcontainer = 'multibarchart_container'  # container name
        chartcontainer_with_date = 'date_multibarchart_container'  # container name
        hori_charttype = "multiBarHorizontalChart"
        hori_chartcontainer = 'multibarhorizontalchart_container'  # container name
        data = {
            'charttype': charttype,
            'chartdata': chartdata,
            'chartcontainer': chartcontainer,
            'extra': {
                'x_is_date': False,
                'x_axis_format': '',
                'tag_script_js': True,
                'jquery_on_ready': True,
            },
            'chartdata_with_date': date_chartdata,
            'chartcontainer_with_date': chartcontainer_with_date,
            'extra_with_date': {
                'name': chartcontainer_with_date,
                'x_is_date': True,
                'x_axis_format': '%d %b %Y',
                'tag_script_js': True,
                'jquery_on_ready': True,
            },
            'hori_charttype': hori_charttype,
            'hori_chartdata': hori_chartdata,
            'hori_chartcontainer': hori_chartcontainer,
            'hori_extra': {
                'name': hori_chartcontainer,
                'x_is_date': False,
                'x_axis_format': '',
                'tag_script_js': True,
                'jquery_on_ready': True,
            },
            'sc_charttype': sc_charttype,
            'sc_chartdata': sc_chartdata,
            'sc_chartcontainer': sc_chartcontainer,
            'sc_extra': {
                'name': sc_chartcontainer,
                'x_is_date': True,
                'x_axis_format': '%d-%b',
                'tag_script_js': True,
                'jquery_on_ready': True,
            },
        }

        return dict(super(NewsnewView, self).get_context_data(**kwargs).items() + data.items())

