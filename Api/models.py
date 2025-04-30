# family/models.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid


class Family(models.Model):
    """Modèle représentant une famille/arbre généalogique."""
    name = models.CharField(_("Nom de la famille"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    created_at = models.DateTimeField(_("Date de création"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date de modification"), auto_now=True)
    # Api/models.py - dans la classe Family
    is_public = models.BooleanField(_("Famille publique"), default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='families',
        verbose_name=_("Créé par")
    )
    

    class Meta:
        verbose_name = _("Famille")
        verbose_name_plural = _("Familles")
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Member(models.Model):
    """Modèle représentant un membre d'une famille."""
    GENDER_CHOICES = [
        ('male', _('Homme')),
        ('female', _('Femme')),
        ('other', _('Autre')),
    ]

    # Champs de base
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name=_("Famille")
    )
    first_name = models.CharField(_("Prénom"), max_length=100)
    last_name = models.CharField(_("Nom"), max_length=100, blank=True)
    gender = models.CharField(_("Genre"), max_length=10, choices=GENDER_CHOICES, default='male')
    birth_date = models.DateField(_("Date de naissance"), null=True, blank=True)
    death_date = models.DateField(_("Date de décès"), null=True, blank=True)
    birth_place = models.CharField(_("Lieu de naissance"), max_length=200, blank=True)
    occupation = models.CharField(_("Profession"), max_length=100, blank=True)
    bio = models.TextField(_("Biographie"), blank=True)

    # Photo de profil
    photo = models.ImageField(
        upload_to='members/photos/',
        null=True,
        blank=True,
        verbose_name=_("Photo de profil")
    )

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Membre")
        verbose_name_plural = _("Membres")
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def age(self):
        """Calcule l'âge du membre en fonction de sa date de naissance et de décès."""
        if not self.birth_date:
            return None

        from django.utils import timezone
        import datetime

        end_date = self.death_date if self.death_date else timezone.now().date()

        # Calcul simple de l'âge
        years = end_date.year - self.birth_date.year

        # Ajustement si l'anniversaire de cette année n'est pas encore passé
        if end_date.month < self.birth_date.month or (
                end_date.month == self.birth_date.month and
                end_date.day < self.birth_date.day
        ):
            years -= 1

        return years


class Relation(models.Model):
    """
    Modèle représentant une relation entre deux membres.
    - Pour une relation parent, source est le parent et target est l'enfant
    - Pour une relation conjoint, source et target sont les conjoints
    """
    RELATION_TYPES = [
        ('parent', _('Parent')),
        ('spouse', _('Conjoint(e)')),
    ]

    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='relations',
        verbose_name=_("Famille")
    )
    source = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='source_relations',
        verbose_name=_("Source")
    )
    target = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='target_relations',
        verbose_name=_("Cible")
    )
    type = models.CharField(
        _("Type de relation"),
        max_length=10,
        choices=RELATION_TYPES
    )
    start_date = models.DateField(_("Date de début"), null=True, blank=True)
    end_date = models.DateField(_("Date de fin"), null=True, blank=True)
    notes = models.TextField(_("Notes"), blank=True)

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Relation")
        verbose_name_plural = _("Relations")
        # Empêcher les relations en double
        constraints = [
            models.UniqueConstraint(
                fields=['family', 'source', 'target', 'type'],
                name='unique_relation'
            )
        ]

    def __str__(self):
        relation_type = dict(self.RELATION_TYPES).get(self.type, self.type)
        return f"{self.source} - {relation_type} - {self.target}"

    def clean(self):
        """
        Validation personnalisée:
        - Une personne ne peut pas être son propre parent
        - Une personne ne peut pas être son propre conjoint
        """
        from django.core.exceptions import ValidationError

        if self.source == self.target:
            raise ValidationError(_("Une personne ne peut pas avoir une relation avec elle-même"))