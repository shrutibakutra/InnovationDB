from django import template

register = template.Library()


@register.filter(name='error_to_string')
def convert_error_to_string(value):
	if value == 0:
		return 'Pending'
	elif value == 1:
		return 'Runing'
	elif value == 2:
		return 'completed'

