from django.utils import timezone

from django.db import models

# Create your models here.

class User(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    photo = models.CharField(max_length=255, null=True, blank=True)
    create_at = models.DateTimeField(default=timezone.now)
    update_at = models.DateTimeField(default=timezone.now)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'password': self.password,
            'email': self.email,
            'photo': self.photo,
            'create_at': self.create_at,
            'update_at': self.update_at,
            'card': [card.id for card in self.card_set.all()] if hasattr(self, 'card_set') else [],
            'card_category': [category.id for category in self.cardcategory.all()] if hasattr(self, 'cardcategory') else [],
        }


class Card(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    status = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    create_at = models.DateTimeField(default=timezone.now)
    update_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, related_name='card_set', on_delete=models.CASCADE)
    category = models.ForeignKey('CardCategory', related_name='card', on_delete=models.CASCADE)

    def to_dict(self):
        return {
            'id': str(self.id),
            'status': self.status,
            'title': self.title,
            'description': self.description,
            'create_at': self.create_at,
            'update_at': self.update_at,
            'user_id': str(self.user.id),
            'category_id': str(self.category.id),
        }


class CardCategory(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    create_at = models.DateTimeField(default=timezone.now)
    update_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, related_name='cardcategory', on_delete=models.CASCADE)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'color': self.color,
            'create_at': self.create_at,
            'update_at': self.update_at,
            'card_id': [card.id for card in self.card_set.all()] if hasattr(self, 'card_set') else [],
        }