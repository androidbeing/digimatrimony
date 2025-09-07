from django import template

register = template.Library()

@register.filter
def get_primary(photos):
    """Returns the primary photo object if exists, else None."""
    return photos.filter(is_primary=True).first()
