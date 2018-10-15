import re
from annotate.models import Sentencepair

de = open('testsentences/de.txt', 'r')
en = open('testsentences/en.txt', 'r')
fi = open('testsentences/fi.txt', 'r')
fr = open('testsentences/fr.txt', 'r')
ru = open('testsentences/ru.txt', 'r')
sv = open('testsentences/sv.txt', 'r')

lang =[de,en,fi,fr,ru,sv]

for i in range(len(lang)):
	if i == 0:
		language = "de"
	if i == 1:
		language = "en"
	if i == 2:
		language = "fi"
	if i == 3:
		language = "fr"
	if i == 4:
		language = "ru"
	if i == 5:
		language = "sv"
	for j in range(4):
		if j%100 == 0:
			print(j)
		line = lang[i].readline()
		m = re.search('(.*)\t(.*)\t(.*)', line)
		if m:
			#If the sentencepair is not already in the database
			if len(Sentencepair.objects.filter(sentID = m.group(1), lang = language)) == 0:
				s = Sentencepair(sentID=m.group(1), sent1=m.group(2), sent2=m.group(3), lang = language)
				s.save()

for l in lang:
	l.close()
