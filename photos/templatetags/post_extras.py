import re
from django import template

register = template.Library()

@register.filter
def format_caption(value):

    # hashtags
    value = re.sub(
        r'#(\w+)',
        r'<a href="/photos/tag/\1/">#\1</a>',
        value
    )

    # mentions
    value = re.sub(
        r'@(\w+)',
        r'<a href="/photos/user/\1/">@\1</a>',
        value
    )

    return value
