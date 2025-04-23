# family/serializers.py

from rest_framework import serializers
from .models import Family, Member, Relation


class FamilySerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Family
        fields = ['id', 'name', 'description', 'created_at', 'created_by', 'member_count']
        read_only_fields = ['created_at', 'created_by']

    def get_member_count(self, obj):
        return obj.members.count()

    def create(self, validated_data):
        # Assigner automatiquement l'utilisateur actuel comme créateur
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class MemberSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            'id', 'family', 'first_name', 'last_name', 'full_name',
            'gender', 'birth_date', 'death_date', 'birth_place',
            'occupation', 'bio', 'photo', 'photo_url', 'age',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_photo_url(self, obj):
        if obj.photo:
            return self.context['request'].build_absolute_uri(obj.photo.url)
        return None


class RelationSerializer(serializers.ModelSerializer):
    source_name = serializers.StringRelatedField(source='source', read_only=True)
    target_name = serializers.StringRelatedField(source='target', read_only=True)

    class Meta:
        model = Relation
        fields = [
            'id', 'family', 'source', 'target', 'source_name', 'target_name',
            'type', 'start_date', 'end_date', 'notes'
        ]

    def validate(self, data):
        """
        Validation personnalisée:
        - Source et target doivent appartenir à la même famille
        - Une personne ne peut pas être son propre parent ou conjoint
        """
        if data['source'] == data['target']:
            raise serializers.ValidationError("Une personne ne peut pas avoir une relation avec elle-même")

        if data['source'].family != data['family'] or data['target'].family != data['family']:
            raise serializers.ValidationError("Les membres doivent appartenir à la même famille que la relation")

        return data


class FamilyDetailSerializer(serializers.ModelSerializer):
    """Serializer pour afficher tous les détails d'une famille, y compris ses membres et relations"""
    members = MemberSerializer(many=True, read_only=True)
    relations = RelationSerializer(many=True, read_only=True)

    class Meta:
        model = Family
        fields = ['id', 'name', 'description', 'created_at', 'created_by', 'members', 'relations']