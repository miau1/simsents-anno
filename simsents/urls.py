from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()

import annotate.views

urlpatterns = [
	url(r'^$', annotate.views.index, name='index'),
	url(r'^db', annotate.views.db, name='db'),
	url(r'^login', annotate.views.loginView, name='login'),
	url(r'^userlogin', annotate.views.userLogin, name='userlogin'),
	url(r'^logout', annotate.views.logoutView, name='logout'),
	url(r'^admin/', admin.site.urls),
	url(r'^(?P<pair_id>[0-9]+)/annotate/$', annotate.views.annotate, name='annotate'),
	url(r'^(?P<pair_id>[0-9]+)/$', annotate.views.pair, name='pair'),
	url(r'^user/$', annotate.views.user, name='user'),
	url(r'^changelang', annotate.views.changeLanguage, name='changelang'),
	url(r'^continue', annotate.views.continueAnnotating, name='continue'),
	url(r'^newpass', annotate.views.newPass, name='newpass'),
	url(r'^lang/(?P<lang>[a-z]{2})/$', annotate.views.lang, name='lang'),
	url(r'^discarded/(?P<lang>[a-z]{2})/$', annotate.views.discarded, name='discarded'),
	url(r'^edit/(?P<pair_id>[0-9]+)/(?P<lang>[a-z]{2})/$', annotate.views.edit, name='edit'),
	url(r'^signup', annotate.views.signup, name='signup'),
	url(r'^applications', annotate.views.applications, name='applications'),
	url(r'^appl/(?P<app_id>[0-9]+)/$', annotate.views.deleteAppl, name='deleteAppl'),
	url(r'^userstats', annotate.views.users, name='users'),
	url(r'^search/(?P<username>.*)/(?P<language>.*)/(?P<order>.*)/(?P<printable>.*)$', annotate.views.search, name='search'),
	url(r'^searchoption', annotate.views.searchOption, name='searchoption'),
]
