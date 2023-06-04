from django import template
import locale

register = template.Library()

@register.filter
def format_currency(value):
    if value is None:
        return 'R$ 0,00'
    
    value = float(value)
    formatted_value = locale.currency(value, grouping=True, symbol='R$', international=False)
    return f'{formatted_value}'
