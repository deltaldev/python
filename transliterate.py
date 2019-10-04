###########
#
# Transliterate v-0.1 by Deltal
# Does transliterating from russian to latin.
# 
###########
def transliterate(txt):
	#replace dictionary (ru -> en)
	replace = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo','ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h','ц':'ts','ч':'ch','ш':'sh','щ':'sch','ъ':'y','ы':'i','ь':'','э':'e','ю':'yu','я':'ya','А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'Yo','Ж':'Zh','З':'Z','И':'I','Й':'Y','К':'K','Л':'L','М':'M','Н':'N','О':'O','П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F','Х':'H','Ц':'Ts','Ч':'Ch','Ш':'SH','Щ':'Sch','Ъ':'','Ы':'I','Ь':'`','Э':'E','Ю':'Yu','Я':'Ya'}
	replace['ь'] = '`' #unicode error approach
	re = str() #returning string
	did = False #caught equal character bool
	for sym in txt:
		for fr,to in replace.items():
			if sym == fr: #if original symbol == dictionary item
				re += to
				did = True
		if not did: #if original symbol didn't found dictionary item 
			re += sym
		did = False
	return re
