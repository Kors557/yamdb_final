from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from django.db.models import Avg

import datetime as dt
from reviews.models import Category, Genre, Title, Comment, Review


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)

    rating = serializers.SerializerMethodField()

    def validate(self, data):
        try:
            slug = self.context['request'].data.get('category')
            category = Category.objects.get(slug=slug)
            data['category'] = category
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Категории нет в базе данных!')
        try:
            genres = []
            slugs = self.context['request'].data.getlist('genre')
            for slug in slugs:
                genre = Genre.objects.get(slug=slug)
                genres.append(genre)
            data['genre'] = genres
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Жанра нет в базе данных!')
        return data

    def validate_year(self, value):
        year = dt.date.today().year
        if not (value <= year):
            raise serializers.ValidationError('Произведение из будущего?')
        return value

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        title.genre.set(genres)
        return title

    def get_rating(self, title):
        reviews = Review.objects.filter(
            title=title)
        if reviews is None:
            rating = None
            return rating
        rating = reviews.all().aggregate(Avg('score'))['score__avg']
        return rating

    class Meta:
        fields = (
            'id', 'category', 'genre', 'name', 'year', 'description', 'rating',
        )
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    title = serializers.HiddenField(default=None)

    score = serializers.IntegerField(max_value=10, min_value=1)

    def validate(self, data):
        title_id = self.context['view'].kwargs['title_id']
        title = get_object_or_404(Title, pk=title_id)
        if (self.context['view'].request.method == 'POST'
                and title.reviews.filter(
                    author=self.context['request'].user).exists()):
            raise serializers.ValidationError(
                'Нельзя добавить второй отзыв на одно произведение.')
        return data

    class Meta:
        model = Review
        fields = ('__all__')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        fields = ('id', 'author', 'text', 'pub_date')
        model = Comment
