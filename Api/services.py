# family/services.py

from django.db.models import Q
from .models import Member, Relation


class FamilyTreeService:
    """
    Service pour obtenir des données structurées sur l'arbre généalogique
    """

    @staticmethod
    def get_parents(member_id):
        """Obtenir les parents d'un membre"""
        parent_relations = Relation.objects.filter(
            target_id=member_id,
            type='parent'
        ).select_related('source')

        return [relation.source for relation in parent_relations]

    @staticmethod
    def get_children(member_id):
        """Obtenir les enfants d'un membre"""
        child_relations = Relation.objects.filter(
            source_id=member_id,
            type='parent'
        ).select_related('target')

        return [relation.target for relation in child_relations]

    @staticmethod
    def get_siblings(member_id):
        """
        Obtenir les frères et sœurs d'un membre
        (partageant au moins un parent avec le membre)
        """
        # Trouver les parents du membre
        parents = FamilyTreeService.get_parents(member_id)
        parent_ids = [parent.id for parent in parents]

        if not parent_ids:
            return []

        # Trouver tous les enfants des parents (sauf le membre lui-même)
        sibling_relations = Relation.objects.filter(
            source_id__in=parent_ids,
            type='parent'
        ).exclude(
            target_id=member_id
        ).select_related('target')

        return list({relation.target for relation in sibling_relations})

    @staticmethod
    def get_spouses(member_id):
        """Obtenir les conjoints d'un membre"""
        spouse_relations = Relation.objects.filter(
            Q(source_id=member_id, type='spouse') |
            Q(target_id=member_id, type='spouse')
        ).select_related('source', 'target')

        return [
            relation.target if relation.source_id == member_id else relation.source
            for relation in spouse_relations
        ]

    @staticmethod
    def get_all_relations(member_id):
        """
        Obtenir toutes les relations d'un membre sous forme structurée
        (parents, enfants, frères/sœurs, conjoints)
        """
        return {
            'parents': FamilyTreeService.get_parents(member_id),
            'children': FamilyTreeService.get_children(member_id),
            'siblings': FamilyTreeService.get_siblings(member_id),
            'spouses': FamilyTreeService.get_spouses(member_id)
        }