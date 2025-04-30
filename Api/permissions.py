# Api/permissions.py (nouveau fichier)
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission qui permet uniquement aux propriétaires d'une famille de la modifier
    ou de voir les données privées.
    """
    
    def has_object_permission(self, request, view, obj):
        # Les permissions en lecture sont autorisées pour n'importe quelle requête
        if request.method in permissions.SAFE_METHODS:
            # Vérifier si la famille est publique
            if hasattr(obj, 'family'):
                # Pour les membres et relations, vérifier la famille associée
                return obj.family.is_public or obj.family.created_by == request.user
            elif hasattr(obj, 'is_public'):
                # Pour les familles directement
                return obj.is_public or obj.created_by == request.user
                
        # L'écriture n'est autorisée qu'au propriétaire
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'family'):
            return obj.family.created_by == request.user
            
        return False