# family/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Family, Member, Relation
import datetime


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.family = Family.objects.create(
            name='Doe Family',
            description='A test family',
            created_by=self.user
        )

        # Créer quelques membres
        self.father = Member.objects.create(
            family=self.family,
            first_name='John',
            last_name='Doe',
            gender='male',
            birth_date=timezone.now().date() - datetime.timedelta(days=365 * 40)
        )

        self.mother = Member.objects.create(
            family=self.family,
            first_name='Jane',
            last_name='Doe',
            gender='female',
            birth_date=timezone.now().date() - datetime.timedelta(days=365 * 38)
        )

        self.child = Member.objects.create(
            family=self.family,
            first_name='Junior',
            last_name='Doe',
            gender='male',
            birth_date=timezone.now().date() - datetime.timedelta(days=365 * 10)
        )

        # Créer des relations
        self.spouse_relation = Relation.objects.create(
            family=self.family,
            source=self.father,
            target=self.mother,
            type='spouse'
        )

        self.father_child_relation = Relation.objects.create(
            family=self.family,
            source=self.father,
            target=self.child,
            type='parent'
        )

        self.mother_child_relation = Relation.objects.create(
            family=self.family,
            source=self.mother,
            target=self.child,
            type='parent'
        )

    def test_member_age_calculation(self):
        """Test que le calcul d'âge fonctionne correctement"""
        self.assertEqual(self.father.age, 40)
        self.assertEqual(self.mother.age, 38)
        self.assertEqual(self.child.age, 10)

    def test_member_full_name(self):
        """Test que la propriété full_name fonctionne correctement"""
        self.assertEqual(self.father.full_name, 'John Doe')
        self.assertEqual(self.mother.full_name, 'Jane Doe')

        # Tester avec juste un prénom
        member = Member.objects.create(
            family=self.family,
            first_name='Madonna',
            gender='female'
        )
        self.assertEqual(member.full_name, 'Madonna')


class APITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)

        # Créer une famille
        self.family_data = {
            'name': 'Test Family',
            'description': 'A family for testing'
        }
        self.family_response = self.client.post(
            '/api/families/',
            self.family_data,
            format='json'
        )
        self.family_id = self.family_response.data['id']

        # Créer un membre
        self.member_data = {
            'family': self.family_id,
            'first_name': 'Test',
            'last_name': 'User',
            'gender': 'male',
            'birth_date': '1980-01-01'
        }
        self.member_response = self.client.post(
            '/api/members/',
            self.member_data,
            format='json'
        )
        self.member_id = self.member_response.data['id']

    def test_create_family(self):
        """Test la création d'une famille"""
        self.assertEqual(self.family_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.family_response.data['name'], 'Test Family')
        self.assertEqual(self.family_response.data['created_by'], self.user.id)

    def test_create_member(self):
        """Test la création d'un membre"""
        self.assertEqual(self.member_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.member_response.data['first_name'], 'Test')
        self.assertEqual(self.member_response.data['last_name'], 'User')
        self.assertEqual(self.member_response.data['full_name'], 'Test User')

    def test_create_relation(self):
        """Test la création d'une relation"""
        # Créer un autre membre
        member2_data = {
            'family': self.family_id,
            'first_name': 'Test2',
            'last_name': 'User',
            'gender': 'female'
        }
        member2_response = self.client.post(
            '/api/members/',
            member2_data,
            format='json'
        )
        member2_id = member2_response.data['id']

        # Créer une relation
        relation_data = {
            'family': self.family_id,
            'source': self.member_id,
            'target': member2_id,
            'type': 'spouse'
        }
        relation_response = self.client.post(
            '/api/relations/',
            relation_data,
            format='json'
        )

        self.assertEqual(relation_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(relation_response.data['source'], self.member_id)
        self.assertEqual(relation_response.data['target'], member2_id)