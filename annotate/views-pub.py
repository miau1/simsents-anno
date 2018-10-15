from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Count, Max, Min, Q

from .models import *

import datetime

#Number of sentence pairs with a single annotation
def incomplete(lang):
	one = len(Annotation.objects.annotate(num_a=Count("sentencepair__annotation")).filter(sentencepair__lang = lang, num_a = 1, category = 1))
	two = len(Annotation.objects.annotate(num_a=Count("sentencepair__annotation")).filter(sentencepair__lang = lang, num_a = 1, category = 2))
	three = len(Annotation.objects.annotate(num_a=Count("sentencepair__annotation")).filter(sentencepair__lang = lang, num_a = 1, category = 3))
	four = len(Annotation.objects.annotate(num_a=Count("sentencepair__annotation")).filter(sentencepair__lang = lang, num_a = 1, category = 4))
	trash = len(Annotation.objects.annotate(num_a=Count("sentencepair__annotation")).filter(sentencepair__lang = lang, num_a = 1, category = -1))

	return four, three, two, one, trash

#Number of sentence pairs and their annotations by color
def colors(lang):
	gr = Sentencepair.objects.annotate(a = Count("annotation"), min = Min("annotation__category"), diff = Max("annotation__category") - 
Min("annotation__category")).filter(lang = lang, a = 2, diff__lt = 2, min = 4).count()
	lgr = Sentencepair.objects.annotate(a = Count("annotation"), min = Min("annotation__category"), diff = Max("annotation__category") - 
Min("annotation__category")).filter(lang = lang, a = 2, diff__lt = 2, min = 3).count()
	yel = Sentencepair.objects.annotate(a = Count("annotation"), min = Min("annotation__category"), diff = Max("annotation__category") - 
Min("annotation__category")).filter(lang = lang, a = 2, diff__lt = 2, min = 2).count()
	red = Sentencepair.objects.annotate(a = Count("annotation"), min = Min("annotation__category"), diff = Max("annotation__category") - 
Min("annotation__category")).filter(lang = lang, a = 2, diff__lt = 2, min = 1).count()
	tra = Sentencepair.objects.annotate(a = Count("annotation")).filter(lang = lang, a = 2).count() - gr - lgr - yel - red

	return gr, lgr, yel, red, tra

#Returns the number of annotated sentence pairs for each language for the current user
def stats(user, request):
	languages = ["de","en","fi","fr","ru","sv"]
	ret = []
	username = user.username
	for l in languages:
		ret.append(len(Annotation.objects.filter(name = username, sentencepair__lang = l)))

	return ret

#Find the next pair to be annotated
def nextPair(user, language, request):
	username = user.username
	lang = user.annotator.lang
	s = Sentencepair.objects.annotate(num_a=Count("annotation"), num_p=Count("annotator")).filter(lang = lang, num_a=1, num_p=0).exclude(annotation__name = username).order_by("pk").first()
	if s:
		showPair(user, s)
		return s.id
	else:
		s = Sentencepair.objects.annotate(num_a=Count("annotation"), num_p=Count("annotator")).filter(lang = lang, num_a=0, num_p__lte=1).order_by("pk").first()
		if s:
			showPair(user, s)
			return s.id
		else:
			return -1

def index(request):
	return HttpResponseRedirect("/continue")

def showPair(user, pair):
	user.annotator.sentencepair = pair
	user.annotator.save()

def pair(request, pair_id):
	if request.user.is_anonymous:
		if len(User.objects.filter(username = get_client_ip(request))) == 0:
			u = User.objects.create_user(username = get_client_ip(request), password = "")
			a = Annotator()
			a.user = u
			a.save()
		user = authenticate(request, username=get_client_ip(request), password = "")
		login(request, user)
	user = request.user
	pair = get_object_or_404(Sentencepair, pk=pair_id)
	stat = stats(user, request)
	return render(request, "pair.html", {"pair": pair, "user": user, "stats":stat})

def get_client_ip(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip

def annotateLogic(pair, c, username, language, request):
	ans = len(Annotation.objects.filter(sentencepair = pair.id, sentencepair__lang = language))
	#If there are no annotations for this pair or there is one annotation not made by current
        #user, save the annotation.
	if ans == 0 or (ans == 1 and len(Annotation.objects.filter(sentencepair = pair.id, name = username, sentencepair__lang = language)) == 0):
		Annotation.objects.create(sentencepair = pair, category = c, name = username)
	#If there are annotations made by current user, delete those annotations and create a new one (edit)
	elif (ans == 1 or ans == 2) and len(Annotation.objects.filter(sentencepair = pair.id, name = username, sentencepair__lang = language)) >= 1:
		Annotation.objects.filter(sentencepair = pair.id, name = username, sentencepair__lang = language).delete()
		Annotation.objects.create(sentencepair = pair, category = c, name = username)
	pair.save()

def annotate(request, pair_id):
	pair = get_object_or_404(Sentencepair, pk = pair_id)
	c = request.POST.get("category", "")
	user = request.user
	username = user.username
	language = pair.lang
	annotateLogic(pair, c, username, language, request)
	return HttpResponseRedirect("/continue")

@login_required(login_url="/login")
def db(request):
	if request.user.is_superuser:
		#Number of pairs with annotations for each language
		languages = ["de","en","fi","fr","ru","sv"]
		stats = []
		for l in languages:
			g = colors(l)
			i = incomplete(l)
			stats.append((l, g[0], g[1], g[2], g[3], g[4], i[0], i[1], i[2], i[3], i[4]))
		annotations = Annotation.objects.order_by("-date")[:100]
		return render(request, "db.html", {"annotations": annotations, "stat": stats})
	else:
		messages.info(request, "You are not admin")
		return HttpResponseRedirect("/user")

def loginView(request):
	return render(request, "login.html")

def userLogin(request):
	username = request.POST.get("username", "")
	password = request.POST.get("password", "")
	user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		return HttpResponseRedirect("/continue")
	else:
		return render(request, "login.html", {"error_message": "Invalid username or password"})

def logoutView(request):
    logout(request)
    return HttpResponseRedirect("/login")

@login_required(login_url="/login")
def user(request):
	user = request.user
	annotations = Annotation.objects.filter(name = user.username).order_by("-date")[:100]
	stat = stats(user, request)
	languages = ["de","en","fi","fr","ru","sv"]
	return render(request, "user.html", {"annotations": annotations, "user": user, "stats": stat, "languages": languages})

@login_required(login_url="/login")
def changeLanguage(request):
	language = request.POST.get("language", "")
	user = request.user
	user.annotator.lang = language
	user.annotator.save()
	return HttpResponseRedirect("/user")

def continueAnnotating(request):
	if request.user.is_anonymous:
		if len(User.objects.filter(username = get_client_ip(request))) == 0:
			u = User.objects.create_user(username = get_client_ip(request), password = "")
			a = Annotator()
			a.user = u
			a.save()
		user = authenticate(request, username=get_client_ip(request), password = "")
		login(request, user)

	u = request.user
	language = u.annotator.lang
	n = nextPair(u, language, request)
	if n == -1:
		messages.info(request, "No more sentencepairs to annotate in " + language)
		return HttpResponseRedirect("/user")
	return HttpResponseRedirect("/"+str(n))

@login_required(login_url="/login")
def newPass(request):
	newpass = request.POST.get("password", "")
	u = request.user
	u.set_password(newpass)
	u.save()
	user = authenticate(request, username=u.username, password=newpass)
	login(request, user)
	messages.success(request, "Password updated succesfully")
	return HttpResponseRedirect("/user")

#Print annotated sentencepairs
@login_required(login_url="/login")
def lang(request, lang):
	if request.user.is_superuser:
		ret = []
		sents = Sentencepair.objects.annotate(a = Count("annotation"), min = Min("annotation__category"), diff = Max("annotation__category") - 
Min("annotation__category")).filter(lang = lang, a = 2, diff__lt = 2).exclude(min = -1).order_by("pk")
		for s in sents:
			annos = s.annotation_set.all().order_by("pk")
			anno1 = annos[0].category
			anno2 = annos[1].category
#			if abs(anno1-anno2) < 2 and anno1 != -1 and anno2 != -1:
			ret.append((s.sentID, s.sent1, s.sent2, min(anno1, anno2), annos[0].name, annos[0].category, annos[1].name, annos[1].category))
		return render(request, "lang.html", {"sents": ret})
	else:
		messages.info(request, "You are not admin")
		return HttpResponseRedirect("/user")

@login_required(login_url="/login")
def discarded(request, lang):
        if request.user.is_superuser:
                ret = []
                sents = Sentencepair.objects.annotate(a = Count("annotation"), min = Min("annotation__category"), diff = Max("annotation__category") - 
Min("annotation__category")).filter(Q(lang = lang) & Q(a = 2) & Q(Q(min=-1) | Q(diff__gte = 2))).order_by("pk")
                for s in sents:
                        annos = s.annotation_set.all().order_by("pk")
                        anno1 = annos[0].category
                        anno2 = annos[1].category
                        ret.append((s.sentID, s.sent1, s.sent2, -1, annos[0].name, annos[0].category, annos[1].name, annos[1].category))
                return render(request, "discarded.html", {"sents": ret})
        else:
                messages.info(request, "You are not admin")
                return HttpResponseRedirect("/user")

#Change the language and edit an annotation
@login_required(login_url="/login")
def edit(request, pair_id, lang):
	user = request.user
	user.annotator.lang = lang
	user.annotator.save()
	pair = get_object_or_404(Sentencepair, pk=pair_id, lang = user.annotator.lang)
	stat = stats(user, request)
	return render(request, "pair.html", {"pair": pair, "user": user, "stats":stat})

def signup(request):
	name = request.POST.get("fullname", "")
	email = request.POST.get("email", "")

	try:
		validate_email(email)
	except ValidationError as e:
		return render(request, "login.html", {"error_message": "Invalid email"})
	else:
		Application.objects.create(name = name, email = email)
		messages.success(request, "You sign up is waiting for approval")
		return HttpResponseRedirect("/login")

@login_required(login_url="/login")
def applications(request):
	if request.user.is_superuser:
		a = Application.objects.all()
		return render(request, "applications.html", {"applications": a})
	else:
		messages.info(request, "You are not admin")
		return HttpResponseRedirect("/user")

@login_required(login_url="/login")
def deleteAppl(request, app_id):
	if request.user.is_superuser:
		a = Application.objects.get(pk = app_id)
		a.delete()
		return HttpResponseRedirect("/applications")
	else:
		messages.info(request, "You are not admin")
		return HttpResponseRedirect("/user")

@login_required(login_url="/login")
def users(request):
	if request.user.is_superuser:
		usrstats = []
		usrs = User.objects.all().order_by("username")
		for u in usrs:
			stat = stats(u, request)
			usrstats.append((u.username, stat[0], stat[1], stat[2], stat[3], stat[4], stat[5]))
		return render(request, "users.html", {"users": usrstats})
	else:
		messages.info(request, "You are not admin")
		return HttpResponseRedirect("/user")

@login_required(login_url="/login")
def search(request, username, language, order, printable):
	if request.user.is_superuser:
		a = Annotation.objects.all()
		if username != "empty":
			a = a.filter(name = username)
		if language != "empty":
			a = a.filter(sentencepair__lang = language)
		if order != "empty":
			a = a.order_by(order)
		languages = ["de","en","fi","fr","ru","sv"]
		orders = [["ID, ascending", "sentencepair__id"], ["ID, descending", "-sentencepair__id"], ["Name, ascending", "name"], ["Name, descending", "-name"], ["Category, ascending", "category"], ["Category, descending", "-category"], ["Date, ascending", "date"], ["Date, descending", "-date"]]
		users = User.objects.all().order_by("username")
		if printable == "":
			return render(request, "search.html", {"anno": a, "languages": languages, "users": users, "orders": orders, "sel_name": username, "sel_lang": language, "sel_order": order, "printable": printable})
		else:
			return render(request, "printsearch.html", {"anno": a})
	else:
		messages.info(request, "You are not admin")
		return HttpResponseRedirect("/user")

@login_required(login_url="/login")
def searchOption(request):
	if request.user.is_superuser:
		username = request.POST.get("username", "")
		language = request.POST.get("language", "")
		printable = request.POST.get("printable", "")
		order = request.POST.get("order", "")
		return HttpResponseRedirect("/search/"+username+"/"+language+"/"+order+"/"+printable)
	else:
		messages.info(request, "You are not admin")
		return HttpResponseRedirect("/user")

