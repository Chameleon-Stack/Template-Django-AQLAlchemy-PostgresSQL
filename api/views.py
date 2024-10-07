import json
from datetime import datetime
from uuid import uuid4

from django.http import JsonResponse
from django.views.generic import View

from .models import Card, CardCategory, User
from bcrypt import gensalt, hashpw


def required_fields(*fields):
    def decorator(function):
        def inner(view, request, *args, **kwargs):
            request_json = json.loads(request.body)
            for field in fields:
                if request_json.get(field) is None:
                    return JsonResponse(
                        {'error': f'required field "{field}"'}, status=400
                    )
            return function(view, request, *args, **kwargs)
        return inner

    return decorator


def token_required(function):
    def decorator(view, request, *args, **kwargs):
        request_json = json.loads(request.body)
        if request_json.get('user_id') is None:
            return JsonResponse(
                {'error': 'required field "user_id"'}, status=400
            )
        user = User.objects.filter(id=request_json['user_id']).first()
        if user is None:
            return JsonResponse({'error': 'invalid user_id'}, status=400)
        return function(view, request, *args, **kwargs)

    return decorator


class UserView(View):
    @token_required
    def get(self, request):
        request_json = json.loads(request.body)
        user = User.objects.filter(id=request_json['user_id']).first()
        return JsonResponse(user.to_dict())

    @required_fields('name', 'email', 'password')
    def post(self, request):
        request_json = json.loads(request.body)
        salt = gensalt(8)
        password = hashpw(
            request_json['password'].encode('utf-8'), salt
        ).decode('utf-8')
        user_uuid = str(uuid4())
        user = User.objects.create(
            id=user_uuid,
            name=request_json['name'],
            email=request_json['email'],
            password=password,
            photo=request_json.get('photo', ''),
        )
        return JsonResponse(user.to_dict())

    @token_required
    @required_fields('name', 'password', 'email')
    def put(self, request):
        request_json = json.loads(request.body)
        user = User.objects.filter(id=request_json['user_id']).first()
        salt = gensalt(8)
        password = hashpw(
            request_json['password'].encode('utf-8'), salt
        ).decode('utf-8')
        user.name = request_json['name']
        user.password = password
        user.email = request_json['email']
        user.photo = request_json.get('photo', '')
        user.update_at = datetime.now()
        user.save()
        return JsonResponse(user.to_dict())

    @token_required
    def delete(self, request):
        request_json = json.loads(request.body)
        user = User.objects.filter(id=request_json['user_id']).first()
        response = user.to_dict()
        user.delete()
        return JsonResponse(response)


class CardView(View):
    @token_required
    def get(self, request):
        request_json = json.loads(request.body)
        user = User.objects.filter(id=request_json['user_id']).first()
        cards = [card.to_dict() for card in user.card_set.all()]
        return JsonResponse(cards, safe=False)

    @token_required
    @required_fields('title', 'category_id', 'status')
    def post(self, request):
        request_json = json.loads(request.body)
        user = User.objects.filter(id=request_json['user_id']).first()
        category = CardCategory.objects.get(pk=request_json['category_id'])
        if category is None:
            return JsonResponse({'error': 'invalid category_id'}, status=400)
        card = Card.objects.create(
            status=request_json['status'],
            title=request_json['title'],
            description=request_json.get('description', ''),
            category_id=category.id,
            id=str(uuid4()),
            user_id=user.id,
        )
        return JsonResponse(card.to_dict())

    @token_required
    @required_fields('id', 'status', 'title', 'category_id')
    def put(self, request):
        request_json = json.loads(request.body)
        card = Card.objects.get(pk=request_json['id'])
        if card:
            card.status = request_json['status']
            card.title = request_json['title']
            card.description = request_json.get('description', '')
            card.update_at = datetime.now()
            card.category_id = request_json['category_id']
            card.save()
            return JsonResponse(card.to_dict())
        else:
            return JsonResponse({'error': 'card not found'}, status=404)

    @token_required
    @required_fields('id')
    def delete(self, request):
        request_json = json.loads(request.body)
        card = Card.objects.get(pk=request_json['id'])
        if card is None:
            return JsonResponse({'error': 'card not found'}, status=404)
        response = card.to_dict()
        card.delete()
        return JsonResponse(response)


class CardItemView(View):
    @token_required
    def get(self, request, card_id):
        request_json = json.loads(request.body)
        user = User.objects.filter(id=request_json['user_id']).first()
        card = Card.objects.get(pk=card_id)
        if card and card.user.id == user.id:
            return JsonResponse(card.to_dict())
        else:
            return JsonResponse({'error': 'card not found'}, status=404)


class CardCategoryView(View):
    @token_required
    def get(self, request):
        request_json = json.loads(request.body)
        user = User.objects.filter(id=request_json['user_id']).first()
        cards_categories = [
            card_category.to_dict()
            for card_category in user.cardcategory.all()
        ]
        return JsonResponse(cards_categories, safe=False)

    @token_required
    @required_fields('name', 'color')
    def post(self, request):
        request_json = json.loads(request.body)
        user = User.objects.filter(id=request_json['user_id']).first()
        card_category = CardCategory.objects.create(
            name=request_json['name'],
            color=request_json['color'],
            user_id=user.id,
            id=str(uuid4())
        )
        return JsonResponse(card_category.to_dict())

    @token_required
    @required_fields('category_id', 'name', 'color')
    def put(self, request):
        request_json = json.loads(request.body)
        card_category = CardCategory.objects.get(pk=request_json['category_id'])
        if card_category:
            card_category.name = request_json['name']
            card_category.color = request_json['color']
            card_category.update_at = datetime.now()
            card_category.save()
            return JsonResponse(card_category.to_dict())
        else:
            return JsonResponse(
                {'error': 'card category not found'}, status=404
            )

    @token_required
    @required_fields('category_id')
    def delete(self, request):
        request_json = json.loads(request.body)
        card_category = CardCategory.objects.get(pk=request_json['category_id'])
        if card_category is None:
            return JsonResponse(
                {'error': 'card category not found'}, status=404
            )
        response = card_category.to_dict()
        card_category.delete()
        return JsonResponse(response)


class CardCategoryItemView(View):
    @token_required
    def get(self, request, card_category_id):
        request_json = json.loads(request.body)
        user = User.objects.filter(id=request_json['user_id']).first()
        card_category = CardCategory.objects.get(pk=card_category_id)
        if card_category and card_category.user.id == user.id:
            return JsonResponse(card_category.to_dict())
        else:
            return JsonResponse(
                {'error': 'card category not found'}, status=404
            )
