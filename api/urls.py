from django.urls import path

from . import views

urlpatterns = [
    path('user', views.UserView.as_view(), name='user'),
    path('card', views.CardView.as_view(), name='card'),
    path(
        'card/<card_id>', views.CardItemView.as_view(), name='card_item'
    ),
    path(
        'card-category',
        views.CardCategoryView.as_view(),
        name='card_category',
    ),
    path(
        'card-category/<card_category_id>',
        views.CardCategoryItemView.as_view(),
        name='card_category_item',
    ),
]
