from django import template
from django.contrib.messages import Message
from django.contrib.messages import constants as message_constants

register = template.Library()


@register.simple_tag
def bootstrap_message_tag(message: Message):
    print(message.level_tag)
    match message.level:
        case message_constants.DEBUG:
            return "danger"
        case message_constants.ERROR:
            return "danger"
        case _:
            return message.level_tag
