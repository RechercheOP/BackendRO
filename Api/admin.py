# family/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Family, Member, Relation


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'member_count', 'created_by', 'created_at')
    list_filter = ('created_by', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    def member_count(self, obj):
        return obj.members.count()

    member_count.short_description = "Nombre de membres"


class RelationInline(admin.TabularInline):
    model = Relation
    fk_name = 'source'
    extra = 0
    verbose_name = "Relation sortante"
    verbose_name_plural = "Relations sortantes"


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('full_name_display', 'family', 'gender', 'birth_date', 'photo_thumbnail', 'age_display')
    list_filter = ('family', 'gender')
    search_fields = ('first_name', 'last_name', 'birth_place', 'occupation')
    readonly_fields = ('created_at', 'updated_at', 'photo_preview')
    fieldsets = (
        ('Informations principales', {
            'fields': ('family', 'first_name', 'last_name', 'gender')
        }),
        ('Dates importantes', {
            'fields': ('birth_date', 'birth_place', 'death_date')
        }),
        ('Informations supplémentaires', {
            'fields': ('occupation', 'bio')
        }),
        ('Photo', {
            'fields': ('photo', 'photo_preview')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [RelationInline]

    def full_name_display(self, obj):
        return obj.full_name

    full_name_display.short_description = "Nom complet"

    def age_display(self, obj):
        age = obj.age
        if age is None:
            return "-"
        return f"{age} ans"

    age_display.short_description = "Âge"

    def photo_thumbnail(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />',
                obj.photo.url
            )
        return "-"

    photo_thumbnail.short_description = "Photo"

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 100%;" />',
                obj.photo.url
            )
        return "(Pas de photo)"

    photo_preview.short_description = "Aperçu de la photo"


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ('family', 'relation_display', 'type', 'start_date')
    list_filter = ('family', 'type')
    search_fields = ('source__first_name', 'source__last_name', 'target__first_name', 'target__last_name')
    readonly_fields = ('created_at', 'updated_at')

    def relation_display(self, obj):
        relation_type = dict(obj.RELATION_TYPES).get(obj.type, obj.type)
        return f"{obj.source} → {relation_type} → {obj.target}"

    relation_display.short_description = "Relation"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "target" and request.resolver_match.kwargs.get('object_id'):
            obj_id = request.resolver_match.kwargs.get('object_id')
            relation = Relation.objects.get(pk=obj_id)
            kwargs["queryset"] = Member.objects.filter(family=relation.family)
        elif db_field.name == "source" and request.resolver_match.kwargs.get('object_id'):
            obj_id = request.resolver_match.kwargs.get('object_id')
            relation = Relation.objects.get(pk=obj_id)
            kwargs["queryset"] = Member.objects.filter(family=relation.family)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)