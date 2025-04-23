# README.md - Documentation détaillée du Backend Django

# Genealogy API - Documentation du Backend

Ce document détaille l'architecture et le fonctionnement du backend Django Rest Framework pour l'application d'arbre généalogique.

## Sommaire
1. [Introduction](#introduction)
2. [Configuration technique](#configuration-technique)
3. [Modèles de données](#modèles-de-données)
4. [API REST](#api-rest)
5. [Services et fonctionnalités](#services-et-fonctionnalités)
6. [Administration](#administration)
7. [Sécurité](#sécurité)
8. [Déploiement](#déploiement)

## Introduction

Le backend Genealogy API est développé avec Django et Django Rest Framework pour offrir une API RESTful complète permettant de gérer des arbres généalogiques. Il permet de créer, visualiser et organiser des informations sur les familles, les membres et leurs relations.

### Principales fonctionnalités

- Gestion de multiples arbres généalogiques par utilisateur
- Création et organisation de membres familiaux
- Définition de relations familiales (parent, conjoint)
- Téléchargement et gestion de photos
- Calcul automatique des relations familiales complexes (frères/sœurs, etc.)
- Interface d'administration puissante pour la gestion des données
- Points d'API complets pour l'intégration avec un frontend

## Configuration technique

### Prérequis
- Python 3.8+
- Django 4.2.10
- Django Rest Framework 3.14.0

### Package Python requis
```bash
django==4.2.10
djangorestframework==3.14.0
django-cors-headers==4.3.1
Pillow==10.1.0
django-filter==23.5
django-webpack-loader==2.0.1
django-cleanup==8.0.0
```

### Structure du projet

```
genealogy_project/
├── family/                   # Application principale
│   ├── migrations/           # Migrations de base de données
│   ├── admin.py              # Configuration de l'interface admin
│   ├── models.py             # Modèles de données Django
│   ├── serializers.py        # Sérialiseurs DRF
│   ├── services.py           # Logique métier
│   ├── tests.py              # Tests unitaires
│   ├── urls.py               # Configuration des URLs
│   └── views.py              # Vues et ViewSets
├── genealogy_project/        # Projet Django
│   ├── settings.py           # Configuration du projet
│   ├── urls.py               # URLs racine du projet
│   └── wsgi.py               # Configuration de déploiement
├── media/                    # Fichiers téléchargés (photos)
├── static/                   # Fichiers statiques
├── manage.py                 # Script Django
└── requirements.txt          # Dépendances Python
```

## Modèles de données

Le backend s'appuie sur trois modèles principaux qui constituent la base de l'application généalogique.

### Family (Famille)

Représente un arbre généalogique complet. Chaque utilisateur peut avoir plusieurs familles.

| Champ | Type | Description |
|-------|------|-------------|
| name | CharField | Nom de la famille |
| description | TextField | Description de la famille |
| created_at | DateTimeField | Date de création |
| updated_at | DateTimeField | Date de dernière modification |
| created_by | ForeignKey (User) | Utilisateur créateur |

### Member (Membre)

Représente un individu dans l'arbre généalogique.

| Champ | Type | Description |
|-------|------|-------------|
| family | ForeignKey (Family) | Famille d'appartenance |
| first_name | CharField | Prénom |
| last_name | CharField | Nom de famille |
| gender | CharField | Genre (male/female/other) |
| birth_date | DateField | Date de naissance |
| death_date | DateField | Date de décès (optionnel) |
| birth_place | CharField | Lieu de naissance |
| occupation | CharField | Profession |
| bio | TextField | Biographie |
| photo | ImageField | Photo de profil |

**Propriétés calculées:**
- `full_name`: Prénom et nom combinés
- `age`: Âge calculé à partir des dates de naissance (et décès si applicable)

### Relation (Relation)

Représente une relation entre deux membres.

| Champ | Type | Description |
|-------|------|-------------|
| family | ForeignKey (Family) | Famille d'appartenance |
| source | ForeignKey (Member) | Membre source |
| target | ForeignKey (Member) | Membre cible |
| type | CharField | Type de relation (parent, spouse) |
| start_date | DateField | Date de début (optionnel) |
| end_date | DateField | Date de fin (optionnel) |
| notes | TextField | Notes sur la relation |

**Types de relation:**
- `parent`: Le membre source est parent du membre cible
- `spouse`: Les membres source et cible sont conjoints

## API REST

L'API suit les principes RESTful et utilise Django Rest Framework pour exposer les fonctionnalités.

### Points d'entrée principaux

#### Familles
- `GET /api/families/` - Liste toutes les familles de l'utilisateur
- `POST /api/families/` - Crée une nouvelle famille
- `GET /api/families/{id}/` - Détails d'une famille
- `PUT /api/families/{id}/` - Met à jour une famille
- `DELETE /api/families/{id}/` - Supprime une famille
- `GET /api/families/{id}/full_data/` - Obtient tous les détails d'une famille avec membres et relations

#### Membres
- `GET /api/members/` - Liste tous les membres
- `POST /api/members/` - Crée un nouveau membre
- `GET /api/members/{id}/` - Détails d'un membre
- `PUT /api/members/{id}/` - Met à jour un membre
- `DELETE /api/members/{id}/` - Supprime un membre
- `POST /api/members/{id}/upload_photo/` - Télécharge une photo pour un membre
- `GET /api/members/{id}/family_relations/` - Obtient toutes les relations familiales d'un membre

#### Relations
- `GET /api/relations/` - Liste toutes les relations
- `POST /api/relations/` - Crée une nouvelle relation
- `GET /api/relations/{id}/` - Détails d'une relation
- `PUT /api/relations/{id}/` - Met à jour une relation
- `DELETE /api/relations/{id}/` - Supprime une relation
- `GET /api/relations/by_member/?member_id={id}` - Obtient toutes les relations d'un membre

### Filtres et recherche

Les endpoints prennent en charge divers paramètres pour le filtrage, la recherche et le tri:

#### Familles
- `?search=texte` - Recherche dans les noms et descriptions
- `?ordering=field` - Tri par champ (préfixer avec `-` pour tri descendant)

#### Membres
- `?family=id` - Filtre par famille
- `?gender=value` - Filtre par genre
- `?search=texte` - Recherche dans les noms, professions, lieux
- `?ordering=field` - Tri par divers champs

#### Relations
- `?family=id` - Filtre par famille
- `?source=id` - Filtre par membre source
- `?target=id` - Filtre par membre cible
- `?type=value` - Filtre par type de relation

### Exemples d'utilisation

#### Créer un nouveau membre

```http
POST /api/members/
Content-Type: application/json

{
  "family": 1,
  "first_name": "Jean",
  "last_name": "Dubois",
  "gender": "male",
  "birth_date": "1980-05-15",
  "birth_place": "Paris, France",
  "occupation": "Ingénieur"
}
```

#### Créer une relation parent-enfant

```http
POST /api/relations/
Content-Type: application/json

{
  "family": 1,
  "source": 5,  // ID du parent
  "target": 8,  // ID de l'enfant
  "type": "parent"
}
```

## Services et fonctionnalités

Le backend inclut plusieurs services avancés pour gérer les relations familiales complexes.

### FamilyTreeService

Ce service fournit des méthodes pour calculer et récupérer des informations structurées sur l'arbre généalogique:

- `get_parents(member_id)` - Récupère les parents d'un membre
- `get_children(member_id)` - Récupère les enfants d'un membre
- `get_siblings(member_id)` - Récupère les frères/sœurs d'un membre
- `get_spouses(member_id)` - Récupère les conjoints d'un membre
- `get_all_relations(member_id)` - Récupère toutes les relations structurées

### Gestion des photos

Le système permet l'upload et la gestion de photos pour les membres:

- Upload via formulaire multipart
- Redimensionnement automatique des images
- Nettoyage automatique des images supprimées
- Génération d'URLs pour le frontend

## Administration

L'interface d'administration Django a été personnalisée pour faciliter la gestion des données.

### Caractéristiques de l'administration

- **Families**: Affichage du nombre de membres, filtrage, recherche
- **Members**: Prévisualisation des photos, calcul d'âge, organisation par sections logiques
- **Relations**: Interface intuitive, filtrage contextuel, validation intégrée

### Validations personnalisées

Des validations ont été mises en place pour éviter les incohérences:
- Empêche qu'une personne soit son propre parent ou conjoint
- Vérifie que les membres d'une relation appartiennent à la même famille
- Détecte les relations en double
- Validation des dates (naissance, décès, début/fin de relation)

## Sécurité

Le backend implémente plusieurs mesures de sécurité:

- Authentification via DRF (`SessionAuthentication`, `BasicAuthentication`)
- Autorisation basée sur la propriété (chaque utilisateur ne voit que ses propres données)
- Protection CSRF activée
- Configuration CORS pour contrôler les domaines autorisés
- Validation des uploads de fichiers
- Sanitisation des entrées via les sérialiseurs DRF

## Déploiement

### Pour le développement

```bash
# Installation des dépendances
pip install -r requirements.txt

# Migrations
python manage.py makemigrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur de développement
python manage.py runserver
```

### Configuration pour la production

Pour un déploiement en production, plusieurs changements sont recommandés:

1. Configurer une base de données robuste (PostgreSQL)
2. Utiliser un serveur WSGI comme Gunicorn
3. Configurer un serveur web frontal (Nginx, Apache)
4. Activer HTTPS avec Let's Encrypt
5. Configurer les paramètres de sécurité Django:
   - `DEBUG = False`
   - Secret key sécurisé
   - ALLOWED_HOSTS restrictif
   - CORS_ALLOWED_ORIGINS limité aux domaines nécessaires

## Personnalisation et extension

Le code a été conçu pour être facilement extensible:

- Ajout de nouveaux types de relations
- Extension du modèle Member avec de nouveaux champs
- Création de nouveaux services pour des fonctionnalités additionnelles
- Intégration avec des services tiers (par exemple, stockage de photos S3)

---

## Conclusion

Le backend Genealogy API fournit une base solide et flexible pour la gestion d'arbres généalogiques. Il combine la robustesse de Django avec la flexibilité de Django Rest Framework pour offrir une API complète, sécurisée et performante.

Pour toute question ou amélioration, n'hésitez pas à contacter l'équipe de développement.


