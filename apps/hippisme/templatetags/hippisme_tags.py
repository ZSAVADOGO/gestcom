from django import template

register = template.Library()


@register.filter
def getattribute(objet, nom):

    try:
        valeur = getattr(objet, nom)

        if callable(valeur):
            valeur = valeur()

        return valeur

    except (AttributeError, TypeError):
        return ""