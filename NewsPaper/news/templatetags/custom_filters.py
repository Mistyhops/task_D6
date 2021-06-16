from django import template

register = template.Library()


@register.filter(name='censor')
def censor(some_str):
    cens_str = ''
    for i in some_str.split():
        cens_str = some_str.replace('биткоин', '@!#$')
    return cens_str


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()
