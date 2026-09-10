const gestComAlerts = {
    // 1. Toast / Notification centrée au milieu de l'écran
    toastCentre(message, icon = "success", titre = "Notification") {
        return Swal.fire({
            position: "center",
            icon: icon,
            title: titre,             // Affiche le titre en gras au-dessus (ex: "Opération réussie")
            text: message,            // Affiche votre message explicatif sous le titre
            showConfirmButton: false,
            timer: 2500,
            timerProgressBar: true,
            customClass: {
                popup: 'rounded-xl shadow-2xl border border-gray-100'
            }
        });
    },

    // Alias 'toast'
    toast(message, icon = "success", titre = "Notification") {
        return this.toastCentre(message, icon, titre);
    },

    // 2. Modale de Succès centrée complète
    succes(message, titre = "Opération réussie") {
        return Swal.fire({
            position: "center",
            title: titre,
            html: message, // Supporte le HTML si besoin
            icon: "success",
            confirmButtonColor: "#4f46e5", // Indigo-600
            confirmButtonText: "D'accord",
            allowOutsideClick: true,
            customClass: {
                popup: 'rounded-xl border border-gray-100',
                confirmButton: 'px-5 py-2.5 rounded-lg text-sm font-medium'
            }
        });
    },

    // 3. Modale d'Erreur centrée enrichie
    erreur(message, titre = "Une erreur est survenue") {
        return Swal.fire({
            position: "center",
            title: titre,
            html: message,
            icon: "error",
            confirmButtonColor: "#4f46e5",
            confirmButtonText: "Compris",
            footer: '<span class="text-xs text-gray-500">Si le problème persiste, contactez l\'administrateur.</span>',
            customClass: {
                popup: 'rounded-xl border border-gray-100',
                confirmButton: 'px-5 py-2.5 rounded-lg text-sm font-medium'
            }
        });
    },

    // 4. Spinner de chargement bloquant au milieu
    chargement(message = "Veuillez patienter...") {
        Swal.fire({
            position: "center",
            title: message,
            allowOutsideClick: false,
            allowEscapeKey: false,
            showConfirmButton: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
    },

    fermerChargement() {
        Swal.close();
    },

    // 5. Confirmation centrée avec option de refus/annulation
    confirmer({
        titre = "Êtes-vous sûr ?",
        message = "Cette action est irréversible.",
        icon = "warning",
        confirmButtonText = "Oui, confirmer",
        cancelButtonText = "Annuler",
        confirmButtonColor = "#4f46e5",
    } = {}, actionCallback) {
        return Swal.fire({
            position: "center",
            title: titre,
            text: message,
            icon: icon,
            showCancelButton: true,
            focusCancel: true, // Met le focus sur le bouton Annuler par sécurité
            confirmButtonColor: confirmButtonColor,
            cancelButtonColor: "#6b7280", // Gray-500
            confirmButtonText: confirmButtonText,
            cancelButtonText: cancelButtonText,
            reverseButtons: true, // Place le bouton d'action principale à droite
            customClass: {
                popup: 'rounded-xl border border-gray-100'
            }
        }).then((result) => {
            if (result.isConfirmed && typeof actionCallback === "function") {
                actionCallback();
            }
            return result;
        });
    }
};

window.gestComAlerts = gestComAlerts;

/* 
const gestComAlerts = {
    // Notification de succès (ex: Enregistrement client réussi)
    succes(message, titre = "Opération réussie") {
        return Swal.fire({
            title: titre,
            text: message,
            icon: "success",
            confirmButtonColor: "#4f46e5", // Indigo-600 correspondant à l'UI
            confirmButtonText: "Continuer"
        });
    },

    // Notification d'erreur ou d'échec
    erreur(message, titre = "Une erreur est survenue") {
        return Swal.fire({
            title: titre,
            text: message,
            icon: "error",
            confirmButtonColor: "#4f46e5"
        });
    },

    // Toast discret, auto-fermé, pour les actions mineures (filtre, page changée, etc.)
    toast(message, icon = "success") {
        return Swal.fire({
            toast: true,
            position: "top-end",
            icon,
            title: message,
            showConfirmButton: false,
            timer: 2500,
            timerProgressBar: true,
        });
    },

    // Spinner bloquant pendant un appel AJAX (recherche, sauvegarde...)
    chargement(message = "Veuillez patienter...") {
        Swal.fire({
            title: message,
            allowOutsideClick: false,
            allowEscapeKey: false,
            didOpen: () => Swal.showLoading(),
        });
    },

    fermerChargement() {
        Swal.close();
    },

    // Confirmation générique réutilisable
    confirmer({
        titre = "Êtes-vous sûr ?",
        message = "Cette action est irréversible.",
        icon = "warning",
        confirmButtonText = "Confirmer",
        confirmButtonColor = "#4f46e5",
    } = {}, actionCallback) {
        return Swal.fire({
            title: titre,
            text: message,
            icon,
            showCancelButton: true,
            confirmButtonColor,
            cancelButtonColor: "#4b5563",
            confirmButtonText,
            cancelButtonText: "Annuler",
        }).then((result) => {
            if (result.isConfirmed && typeof actionCallback === "function") {
                actionCallback();
            }
            return result;
        });
    },

    // Boîte de dialogue de confirmation critique (ex: suppression client/dossier)
    confirmerSuppression(message, actionCallback) {
        return this.confirmer({
            titre: "Êtes-vous sûr ?",
            message: message || "Cette action est irréversible et sera journalisée dans l'audit de conformité.",
            icon: "warning",
            confirmButtonText: "Oui, supprimer",
            confirmButtonColor: "#dc2626", // Rouge Danger
        }, actionCallback);
    }
};

// Rend l'objet d'alertes accessible globalement
window.gestComAlerts = gestComAlerts; */