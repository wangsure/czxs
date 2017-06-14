from django.conf.urls import include, url
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap, Sitemap
from django.core.urlresolvers import reverse

from django.contrib import admin

from blog.models import Article, News, Category, Column
from demoproject import views

import suit;

import xadmin;
xadmin.autodiscover();
from xadmin.plugins import xversion
xversion.register_models()
class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['index-view', 'news-view']

    def location(self, item):
        return reverse(item)

sitemaps = {
    'article-is-top': GenericSitemap(
                {
                    'queryset': Article.objects.filter(
                                    status=0, is_top=True
                                ).all(),
                    'date_field': 'pub_time'
                },
                priority=1.0,
                changefreq='daily'
            ),
    'article-is-not-top': GenericSitemap(
                {
                    'queryset': Article.objects.filter(status=0).all(),
                    'date_field': 'pub_time'
                },
                priority=0.8,
                changefreq='daily'
            ),
    'news': GenericSitemap(
                {
                    'queryset': News.objects.all(),
                    'data_field': 'pub_time'
                },
                priority=0.6,
                changefreq='daily'
            ),
    'category': GenericSitemap(
                {
                    'queryset': Category.objects.all()
                },
                priority=0.9,
                changefreq='daily'
            ),
    'column': GenericSitemap(
                {
                    'queryset': Column.objects.all()
                },
                priority=0.9,
                changefreq='daily'
            ),
    'static': StaticViewSitemap
}


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('blog.urls')),
    url(r'', include('vmaig_comments.urls')),
    url(r'', include('vmaig_auth.urls')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^piechart/', views.demo_piechart, name='demo_piechart'),
    url(r'^linechart/', views.demo_linechart, name='demo_linechart'),
    url(r'^linechart_without_date/', views.demo_linechart_without_date, name='demo_linechart_without_date'),
    url(r'^linewithfocuschart/', views.demo_linewithfocuschart, name='demo_linewithfocuschart'),
    url(r'^multibarchart/', views.demo_multibarchart, name='demo_multibarchart'),
    url(r'^stackedareachart/', views.demo_stackedareachart, name='demo_stackedareachart'),
    url(r'^multibarhorizontalchart/', views.demo_multibarhorizontalchart, name='demo_multibarhorizontalchart'),
    url(r'^lineplusbarchart/', views.demo_lineplusbarchart, name='demo_lineplusbarchart'),
    url(r'^cumulativelinechart/', views.demo_cumulativelinechart, name='demo_cumulativelinechart'),
    url(r'^discretebarchart/', views.demo_discretebarchart, name='demo_discretebarchart'),
    url(r'^discretebarchart_with_date/', views.demo_discretebarchart_with_date, name='demo_discretebarchart_date'),
    url(r'^scatterchart/', views.demo_scatterchart, name='demo_scatterchart'),
    url(r'^linechart_with_ampm/', views.demo_linechart_with_ampm, name='demo_linechart_with_ampm'),
    url(r'^charthome$', views.home, name='charthome'),
    url(r'^xadmin/', include(xadmin.site.urls)),

]
