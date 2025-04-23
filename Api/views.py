# family/views.py

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.reverse import reverse

from .models import Family, Member, Relation
from .serializers import (
    FamilySerializer, FamilyDetailSerializer,
    MemberSerializer, RelationSerializer
)


@api_view(['GET'])
def api_root(request, format=None):
    """
    Vue racine de l'API fournissant des liens vers les principales ressources.
    """
    return Response({
        'families': reverse('family-list', request=request, format=format),
        'members': reverse('member-list', request=request, format=format),
        'relations': reverse('relation-list', request=request, format=format),
    })

class FamilyViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les familles.
    Permet la création, la lecture, la mise à jour et la suppression de familles.
    """
    serializer_class = FamilySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        # Seules les familles créées par l'utilisateur courant sont accessibles
        return Family.objects.filter(created_by=self.request.user)

    def get_serializer_class(self):
        # Utiliser un serializer différent pour les détails
        if self.action == 'retrieve':
            return FamilyDetailSerializer
        return FamilySerializer

    @action(detail=True, methods=['get'])
    def full_data(self, request, pk=None):
        """
        Action personnalisée pour obtenir tous les membres et relations d'une famille en une seule requête
        """
        family = self.get_object()
        serializer = FamilyDetailSerializer(family, context={'request': request})
        return Response(serializer.data)


class MemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les membres.
    Permet la création, la lecture, la mise à jour et la suppression de membres.
    """
    serializer_class = MemberSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['family', 'gender']
    search_fields = ['first_name', 'last_name', 'occupation', 'birth_place']
    ordering_fields = ['first_name', 'last_name', 'birth_date', 'death_date']

    def get_queryset(self):
        # Seuls les membres des familles créées par l'utilisateur courant sont accessibles
        return Member.objects.filter(family__created_by=self.request.user)

    @action(detail=False, methods=['post'])
    def upload_photo(self, request):
        """
        Action personnalisée pour télécharger une photo de profil
        """
        file = request.FILES.get('photo')
        if not file:
            return Response({"detail": "Aucun fichier fourni."}, status=status.HTTP_400_BAD_REQUEST)

        member_id = request.data.get('member_id')
        if not member_id:
            return Response({"detail": "ID membre manquant."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            member = self.get_queryset().get(pk=member_id)
            member.photo = file
            member.save()
            return Response({
                "detail": "Photo téléchargée avec succès.",
                "photo_url": request.build_absolute_uri(member.photo.url)
            })
        except Member.DoesNotExist:
            return Response({"detail": "Membre non trouvé."}, status=status.HTTP_404_NOT_FOUND)

    # Ajout à family/views.py - dans la classe MemberViewSet

    @action(detail=True, methods=['post'])
    def upload_photo(self, request, pk=None):
        """
        Action pour télécharger une photo de profil pour un membre spécifique
        """
        member = self.get_object()

        # Vérifier que le fichier est présent
        if 'photo' not in request.FILES:
            return Response(
                {'error': 'Aucun fichier photo fourni'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Enregistrer la photo
        member.photo = request.FILES['photo']
        member.save()

        # Retourner l'URL de la photo
        serializer = self.get_serializer(member)
        return Response(serializer.data)

    # Ajout à family/views.py - dans la classe MemberViewSet
    @action(detail=True, methods=['get'])
    def family_relations(self, request, pk=None):
        """
        Action pour obtenir toutes les relations familiales d'un membre
        (parents, enfants, frères/sœurs, conjoints)
        """
        from .services import FamilyTreeService

        member = self.get_object()
        relations = FamilyTreeService.get_all_relations(member.id)

        # Sérialiser chaque type de relation
        result = {}
        for relation_type, members in relations.items():
            result[relation_type] = MemberSerializer(
                members, many=True, context={'request': request}
            ).data

        return Response(result)


class RelationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les relations.
    Permet la création, la lecture, la mise à jour et la suppression de relations.
    """
    serializer_class = RelationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['family', 'source', 'target', 'type']
    ordering_fields = ['type']

    def get_queryset(self):
        # Seules les relations des familles créées par l'utilisateur courant sont accessibles
        return Relation.objects.filter(family__created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def by_member(self, request):
        """
        Action personnalisée pour obtenir toutes les relations d'un membre spécifique
        """
        member_id = request.query_params.get('member_id')
        if not member_id:
            return Response({"detail": "ID membre requis"}, status=status.HTTP_400_BAD_REQUEST)

        relations = self.get_queryset().filter(
            models.Q(source_id=member_id) | models.Q(target_id=member_id)
        )
        serializer = self.get_serializer(relations, many=True)
        return Response(serializer.data)