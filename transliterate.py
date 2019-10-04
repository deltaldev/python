###########
#
# Transliterate v-0.2 by Deltal
#
###########


def createTab(intab, outtab):
    replace = {}
    for i, sym in enumerate(intab):
        replace[sym] = outtab[i]
    return replace


def encode(tab, txt):
    re = str()
    did = False
    for sym in txt:
        for fr, to in tab.items():
            if sym == fr:
                re += to
                did = True
            if not did:
                re += sym
            did = False
    return re


tabs = {
    'rusToLatin': {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': 'y', 'ы': 'i', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo', 'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'SH', 'Щ': 'Sch', 'Ъ': '', 'Ы': 'I', 'Ь': '`', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'}
}
