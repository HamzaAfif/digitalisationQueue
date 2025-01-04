from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_by_id(companies, company_id):
    """
    Retrieves a company from a QuerySet by its ID.
    """
    return companies.filter(id=company_id).first()


@register.filter
def map(queryset, attr):
    return [getattr(item, attr) for item in queryset]
