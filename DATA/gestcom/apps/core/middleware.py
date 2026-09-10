from threading import local

_utilisateur_courant = local()


def definir_utilisateur_courant(utilisateur):
    _utilisateur_courant.utilisateur = utilisateur


def obtenir_utilisateur_courant():
    return getattr(
        _utilisateur_courant,
        "utilisateur",
        None
    )


class UtilisateurCourantMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        utilisateur = (
            request.user
            if request.user.is_authenticated
            else None
        )

        definir_utilisateur_courant(utilisateur)

        try:
            response = self.get_response(request)
        finally:
            definir_utilisateur_courant(None)

        return response