from django import template
from num2words import num2words

register = template.Library()


def comma_seperated_bangla(value):
    s = str(value) if value else '0.00'
    dec_right = s.split('.')[1] if len(s.split('.'))>1 else '' #Number after decimal point
    dec_left = s.split('.')[0] #Number of the left side of decimal
    if len(dec_left)<=3:
        return s
    left_s = dec_left[0:len(dec_left)-3]
    right_s = dec_left[-3:]
    s2 = [left_s[-2-i:len(left_s)-i] for i in range(0, len(left_s),2)]
    s2.reverse()
    if len(dec_right)>=1:
        s_final = ','.join(s2)+','+right_s+'.'+dec_right
    else:
        s_final = ','.join(s2)+','+right_s
    return s_final

def number_to_word_bangla_style(value, lang='en_IN'):
    s = num2words(value, to='currency', lang=lang)
    s = s.replace('cent','paisa')
    s = s.replace('euro,',' and').replace('lakh','lac')
    return s


register.filter('comma_seperated_bangla', comma_seperated_bangla)
register.filter('number_to_word_bangla_style', number_to_word_bangla_style)