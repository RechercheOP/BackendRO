import random
from urllib.request import urlopen

# from django.core.files import ContentFile
from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import BaseCommand

from Api.models import Relation, Member
import datetime
from Api.models import Relation
import random
from django.utils import timezone
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.conf import settings
from Api.models import Family, Member, Relation
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen


class Command(BaseCommand):
    help = 'Populates the database with initial data'

    def handle(self, *args, **options):
        import datetime
        from Api.models import Relation
        import random
        from django.utils import timezone
        from django.core.files.base import ContentFile
        from django.contrib.auth.models import User
        from django.conf import settings
        from Api.models import Family, Member, Relation
        from django.core.files.temp import NamedTemporaryFile
        from urllib.request import urlopen


        # Fonction utilitaire pour créer un membre
        # Fonction utilitaire pour créer un membre
        def create_member(family, first_name, last_name, gender, birth_date=None,
                          death_date=None, birth_place="", occupation="", bio="", photo_url=None):
            member = Member.objects.create(
                family=family,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                birth_date=birth_date,
                death_date=death_date,
                birth_place=birth_place,
                occupation=occupation,
                bio=bio
            )

            # Ajouter une photo depuis une URL si fournie
            if photo_url:
                try:
                    img_temp = NamedTemporaryFile()  # Supprime l'argument delete
                    img_temp.write(urlopen(photo_url).read())
                    img_temp.flush()

                    # Générer un nom de fichier
                    filename = f"{first_name.lower()}_{last_name.lower()}_{random.randint(100, 999)}.jpg"

                    # Enregistrer l'image dans le champ photo
                    member.photo.save(filename, ContentFile(open(img_temp.name, 'rb').read()), save=True)
                    img_temp.close()  # Assure-toi de fermer le fichier temporaire
                except Exception as e:
                    print(f"Erreur lors du téléchargement de la photo pour {first_name} {last_name}: {e}")

            return member

        # Fonction pour créer une relation parent-enfant
        def add_parent_child(family, parent, child):
            Relation.objects.create(
                family=family,
                source=parent,
                target=child,
                type='parent'
            )


        # Fonction pour créer une relation de couple
        def add_spouse(family, person1, person2, start_date=None):
            Relation.objects.create(
                family=family,
                source=person1,
                target=person2,
                type='spouse',
                start_date=start_date
            )


        # Configuration: créer un utilisateur si nécessaire
        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            print("Utilisateur 'admin' créé avec le mot de passe 'admin123'")

        # Supprimer les données existantes (optionnel - décommentez si nécessaire)
        # Family.objects.all().delete()
        # Member.objects.all().delete()
        # Relation.objects.all().delete()

        print("Début de la génération des données...")

        # 1. Création de la famille Dupont
        dupont_family = Family.objects.create(
            name="Famille Dupont",
            description="Une grande famille française avec plusieurs générations",
            created_by=user
        )

        # Photos placeholder
        male_photos = [
            "https://randomuser.me/api/portraits/men/1.jpg",
            "https://randomuser.me/api/portraits/men/22.jpg",
            "https://randomuser.me/api/portraits/men/33.jpg",
            "https://randomuser.me/api/portraits/men/45.jpg",
            "https://randomuser.me/api/portraits/men/54.jpg"
        ]

        female_photos = [
            "https://randomuser.me/api/portraits/women/2.jpg",
            "https://randomuser.me/api/portraits/women/23.jpg",
            "https://randomuser.me/api/portraits/women/35.jpg",
            "https://randomuser.me/api/portraits/women/44.jpg",
            "https://randomuser.me/api/portraits/women/56.jpg"
        ]

        # Première génération - Grands-parents
        grandpere_dupont = create_member(
            dupont_family,
            "Maurice",
            "Dupont",
            "male",
            birth_date=datetime.date(1925, 6, 15),
            death_date=datetime.date(2010, 3, 20),
            birth_place="Lyon, France",
            occupation="Charpentier",
            bio="Fondateur de l'entreprise familiale Dupont Construction. A servi dans l'armée française pendant la Seconde Guerre mondiale.",
            photo_url=male_photos[0]
        )

        grandmere_dupont = create_member(
            dupont_family,
            "Jeanne",
            "Martin",
            "female",
            birth_date=datetime.date(1928, 11, 3),
            death_date=datetime.date(2015, 7, 12),
            birth_place="Marseille, France",
            occupation="Institutrice",
            bio="A enseigné pendant 40 ans à l'école primaire du village. Connue pour sa cuisine exceptionnelle et son engagement communautaire.",
            photo_url=female_photos[0]
        )

        add_spouse(dupont_family, grandpere_dupont, grandmere_dupont, start_date=datetime.date(1950, 5, 8))

        # Deuxième génération - Parents et oncles/tantes
        pere_dupont = create_member(
            dupont_family,
            "Jean",
            "Dupont",
            "male",
            birth_date=datetime.date(1955, 4, 12),
            birth_place="Paris, France",
            occupation="Architecte",
            bio="A repris l'entreprise familiale et l'a transformée en cabinet d'architecture. Passionné de voile.",
            photo_url=male_photos[1]
        )

        mere_dupont = create_member(
            dupont_family,
            "Marie",
            "Dubois",
            "female",
            birth_date=datetime.date(1958, 9, 25),
            birth_place="Bordeaux, France",
            occupation="Médecin",
            bio="Pédiatre renommée, ayant travaillé pour Médecins Sans Frontières pendant plusieurs années.",
            photo_url=female_photos[1]
        )

        oncle_dupont = create_member(
            dupont_family,
            "Philippe",
            "Dupont",
            "male",
            birth_date=datetime.date(1960, 2, 18),
            birth_place="Paris, France",
            occupation="Avocat",
            bio="Spécialisé en droit commercial. Grand amateur de vin et collectionneur d'art.",
            photo_url=male_photos[2]
        )

        tante_dupont = create_member(
            dupont_family,
            "Sophie",
            "Leroy",
            "female",
            birth_date=datetime.date(1962, 12, 3),
            birth_place="Nice, France",
            occupation="Professeur d'université",
            bio="Enseigne la littérature française à la Sorbonne. Auteure de plusieurs ouvrages sur Proust.",
            photo_url=female_photos[2]
        )

        # Relations de parenté - 2ème génération
        add_parent_child(dupont_family, grandpere_dupont, pere_dupont)
        add_parent_child(dupont_family, grandmere_dupont, pere_dupont)
        add_parent_child(dupont_family, grandpere_dupont, oncle_dupont)
        add_parent_child(dupont_family, grandmere_dupont, oncle_dupont)

        # Relations de couple - 2ème génération
        add_spouse(dupont_family, pere_dupont, mere_dupont, start_date=datetime.date(1980, 7, 19))
        add_spouse(dupont_family, oncle_dupont, tante_dupont, start_date=datetime.date(1985, 5, 30))

        # Troisième génération - Enfants
        fils_dupont = create_member(
            dupont_family,
            "Thomas",
            "Dupont",
            "male",
            birth_date=datetime.date(1985, 8, 22),
            birth_place="Paris, France",
            occupation="Ingénieur",
            bio="Travaille dans les énergies renouvelables. Passionné d'escalade et de photographie.",
            photo_url=male_photos[3]
        )

        fille_dupont = create_member(
            dupont_family,
            "Julie",
            "Dupont",
            "female",
            birth_date=datetime.date(1988, 3, 14),
            birth_place="Paris, France",
            occupation="Journaliste",
            bio="Correspondante à l'étranger pour un grand quotidien français. A vécu sur trois continents.",
            photo_url=female_photos[3]
        )

        cousine_dupont = create_member(
            dupont_family,
            "Émilie",
            "Dupont",
            "female",
            birth_date=datetime.date(1990, 11, 5),
            birth_place="Paris, France",
            occupation="Artiste",
            bio="Peintre et sculptrice dont les œuvres sont exposées internationalement. Diplômée des Beaux-Arts.",
            photo_url=female_photos[4]
        )

        cousin_dupont = create_member(
            dupont_family,
            "Nicolas",
            "Dupont",
            "male",
            birth_date=datetime.date(1992, 7, 8),
            birth_place="Paris, France",
            occupation="Chef cuisinier",
            bio="Formé dans des restaurants étoilés, il a ouvert son propre restaurant à 25 ans.",
            photo_url=male_photos[4]
        )

        # Relations de parenté - 3ème génération
        add_parent_child(dupont_family, pere_dupont, fils_dupont)
        add_parent_child(dupont_family, mere_dupont, fils_dupont)
        add_parent_child(dupont_family, pere_dupont, fille_dupont)
        add_parent_child(dupont_family, mere_dupont, fille_dupont)
        add_parent_child(dupont_family, oncle_dupont, cousine_dupont)
        add_parent_child(dupont_family, tante_dupont, cousine_dupont)
        add_parent_child(dupont_family, oncle_dupont, cousin_dupont)
        add_parent_child(dupont_family, tante_dupont, cousin_dupont)

        # 2. Création de la famille Garcia
        garcia_family = Family.objects.create(
            name="Famille Garcia",
            description="Une famille espagnole avec des racines en Amérique latine",
            created_by=user
        )

        # Première génération - Grands-parents
        grandpere_garcia = create_member(
            garcia_family,
            "Miguel",
            "Garcia",
            "male",
            birth_date=datetime.date(1930, 3, 12),
            death_date=datetime.date(2012, 8, 7),
            birth_place="Madrid, Espagne",
            occupation="Viticulteur",
            bio="Propriétaire d'un vignoble familial près de Valence. A émigré en France dans les années 1960.",
            photo_url="https://randomuser.me/api/portraits/men/61.jpg"
        )

        grandmere_garcia = create_member(
            garcia_family,
            "Carmen",
            "Rodriguez",
            "female",
            birth_date=datetime.date(1933, 6, 24),
            death_date=datetime.date(2018, 4, 15),
            birth_place="Séville, Espagne",
            occupation="Couturière",
            bio="Talentueuse couturière ayant travaillé pour plusieurs maisons de haute couture à Madrid puis Paris.",
            photo_url="https://randomuser.me/api/portraits/women/60.jpg"
        )

        add_spouse(garcia_family, grandpere_garcia, grandmere_garcia, start_date=datetime.date(1955, 9, 3))

        # Deuxième génération
        pere_garcia = create_member(
            garcia_family,
            "Antonio",
            "Garcia",
            "male",
            birth_date=datetime.date(1960, 5, 17),
            birth_place="Valence, Espagne",
            occupation="Restaurateur",
            bio="Propriétaire de plusieurs restaurants espagnols en France. Connu pour ses paellas authentiques.",
            photo_url="https://randomuser.me/api/portraits/men/62.jpg"
        )

        mere_garcia = create_member(
            garcia_family,
            "Isabella",
            "Fernandez",
            "female",
            birth_date=datetime.date(1962, 11, 29),
            birth_place="Barcelone, Espagne",
            occupation="Professeure d'espagnol",
            bio="Enseigne l'espagnol au lycée international. Passionnée de littérature hispanique.",
            photo_url="https://randomuser.me/api/portraits/women/61.jpg"
        )

        oncle_garcia = create_member(
            garcia_family,
            "Carlos",
            "Garcia",
            "male",
            birth_date=datetime.date(1965, 8, 3),
            birth_place="Madrid, Espagne",
            occupation="Musicien",
            bio="Guitariste flamenco reconnu, ayant joué dans les plus grandes salles de concert d'Europe.",
            photo_url="https://randomuser.me/api/portraits/men/63.jpg"
        )

        # Relations de parenté - 2ème génération Garcia
        add_parent_child(garcia_family, grandpere_garcia, pere_garcia)
        add_parent_child(garcia_family, grandmere_garcia, pere_garcia)
        add_parent_child(garcia_family, grandpere_garcia, oncle_garcia)
        add_parent_child(garcia_family, grandmere_garcia, oncle_garcia)

        # Relation de couple - 2ème génération Garcia
        add_spouse(garcia_family, pere_garcia, mere_garcia, start_date=datetime.date(1985, 6, 12))

        # Troisième génération Garcia
        fils_garcia = create_member(
            garcia_family,
            "Marco",
            "Garcia",
            "male",
            birth_date=datetime.date(1990, 2, 14),
            birth_place="Paris, France",
            occupation="Avocat",
            bio="Spécialisé en droit international. Parle couramment cinq langues.",
            photo_url="https://randomuser.me/api/portraits/men/64.jpg"
        )

        fille_garcia = create_member(
            garcia_family,
            "Elena",
            "Garcia",
            "female",
            birth_date=datetime.date(1993, 7, 20),
            birth_place="Lyon, France",
            occupation="Danseuse",
            bio="Première danseuse au Ballet National de France. A commencé la danse à l'âge de quatre ans.",
            photo_url="https://randomuser.me/api/portraits/women/62.jpg"
        )

        # Relations de parenté - 3ème génération Garcia
        add_parent_child(garcia_family, pere_garcia, fils_garcia)
        add_parent_child(garcia_family, mere_garcia, fils_garcia)
        add_parent_child(garcia_family, pere_garcia, fille_garcia)
        add_parent_child(garcia_family, mere_garcia, fille_garcia)

        # Création des relations entre les familles (mariage inter-familles)
        conjoint_fils_dupont = create_member(
            dupont_family,
            "Clara",
            "Martinez",
            "female",
            birth_date=datetime.date(1988, 11, 3),
            birth_place="Marseille, France",
            occupation="Architecte d'intérieur",
            bio="Collabore avec son mari sur des projets de construction durable.",
            photo_url="https://randomuser.me/api/portraits/women/25.jpg"
        )

        add_spouse(dupont_family, fils_dupont, conjoint_fils_dupont, start_date=datetime.date(2015, 6, 18))

        # Mariage entre les familles
        add_spouse(dupont_family, cousin_dupont, fille_garcia, start_date=datetime.date(2018, 8, 25))

        # 3. Création de la famille Smith
        smith_family = Family.objects.create(
            name="Famille Smith",
            description="Une famille anglo-américaine établie en France",
            created_by=user
        )

        # Première génération - Grands-parents Smith
        grandpere_smith = create_member(
            smith_family,
            "William",
            "Smith",
            "male",
            birth_date=datetime.date(1935, 2, 8),
            death_date=datetime.date(2014, 10, 17),
            birth_place="Londres, Royaume-Uni",
            occupation="Diplomate",
            bio="Ancien ambassadeur britannique en France. A reçu l'Ordre de l'Empire britannique pour ses services.",
            photo_url="https://randomuser.me/api/portraits/men/71.jpg"
        )

        grandmere_smith = create_member(
            smith_family,
            "Elizabeth",
            "Johnson",
            "female",
            birth_date=datetime.date(1938, 4, 22),
            birth_place="Bath, Royaume-Uni",
            occupation="Écrivaine",
            bio="Auteure de plusieurs romans à succès. Ses œuvres ont été traduites en 25 langues.",
            photo_url="https://randomuser.me/api/portraits/women/70.jpg"
        )

        add_spouse(smith_family, grandpere_smith, grandmere_smith, start_date=datetime.date(1958, 7, 12))

        # Deuxième génération Smith
        pere_smith = create_member(
            smith_family,
            "James",
            "Smith",
            "male",
            birth_date=datetime.date(1965, 9, 30),
            birth_place="New York, États-Unis",
            occupation="Professeur d'université",
            bio="Enseigne la littérature anglaise à la Sorbonne. A étudié à Oxford et Harvard.",
            photo_url="https://randomuser.me/api/portraits/men/72.jpg"
        )

        mere_smith = create_member(
            smith_family,
            "Catherine",
            "Dubois",
            "female",
            birth_date=datetime.date(1968, 5, 15),
            birth_place="Paris, France",
            occupation="Traductrice",
            bio="Spécialisée en traduction littéraire. A traduit les œuvres de sa belle-mère en français.",
            photo_url="https://randomuser.me/api/portraits/women/71.jpg"
        )

        # Relations de parenté - 2ème génération Smith
        add_parent_child(smith_family, grandpere_smith, pere_smith)
        add_parent_child(smith_family, grandmere_smith, pere_smith)

        # Relation de couple - 2ème génération Smith
        add_spouse(smith_family, pere_smith, mere_smith, start_date=datetime.date(1990, 8, 4))

        # Troisième génération Smith
        fils_smith = create_member(
            smith_family,
            "Daniel",
            "Smith",
            "male",
            birth_date=datetime.date(1995, 11, 27),
            birth_place="Paris, France",
            occupation="Étudiant en médecine",
            bio="En dernière année de médecine. Souhaite se spécialiser en neurologie.",
            photo_url="https://randomuser.me/api/portraits/men/73.jpg"
        )

        fille_smith = create_member(
            smith_family,
            "Sophie",
            "Smith",
            "female",
            birth_date=datetime.date(1998, 3, 19),
            birth_place="Paris, France",
            occupation="Étudiante en art",
            bio="Étudie les beaux-arts. Talentueuse peintre qui a déjà exposé ses œuvres dans plusieurs galeries parisiennes.",
            photo_url="https://randomuser.me/api/portraits/women/72.jpg"
        )

        # Relations de parenté - 3ème génération Smith
        add_parent_child(smith_family, pere_smith, fils_smith)
        add_parent_child(smith_family, mere_smith, fils_smith)
        add_parent_child(smith_family, pere_smith, fille_smith)
        add_parent_child(smith_family, mere_smith, fille_smith)

        print(f"Génération des données terminée !")
        print(f"Nombre de familles créées: {Family.objects.count()}")
        print(f"Nombre de membres créés: {Member.objects.count()}")
        print(f"Nombre de relations créées: {Relation.objects.count()}")