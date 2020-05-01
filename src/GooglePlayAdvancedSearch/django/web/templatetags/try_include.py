from django import template
from django.template.loader_tags import do_include
from django.template.defaulttags import CommentNode
register = template.Library()


@register.tag('try_include')
def do_try_include(parser, token):
    "Source: http://stackoverflow.com/a/18951166/15690"
    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError(
            "%r tag takes at least one argument: "
            "the name of the template to be included." % bits[0])

    try:
        silent_node = do_include(parser, token)
    except template.TemplateDoesNotExist:
        # Django < 1.7
        return ""

    _orig_render = silent_node.render
    def wrapped_render(*args, **kwargs):
        try:
            return _orig_render(*args, **kwargs)
        except template.TemplateDoesNotExist:
            return ""
    silent_node.render = wrapped_render
    return silent_node