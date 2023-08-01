from rest_framework import serializers
from .models import Book, BookInstance, Author, Language, Genre

class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = '__all__'
        # fields = ['id', 'title', 'author', 'summary', 'isbn', 'genre', 'language']

class BookInstanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = BookInstance
        fields = '__all__'
        # fields = ['id', 'book', 'imprint', 'due_back', 'borrower', 'status']

class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Author
        fields = '__all__'
        # fields = ['id', 'first_name', 'last_name', 'date_of_birth', 'date_of_death']

class LanguageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Language
        fields = '__all__'
        # fields = ['id', 'name']

class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = '__all__'
        # fields = ['id', 'name']
