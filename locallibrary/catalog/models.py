from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import uuid
from datetime import date

# Create your models here.

class Genre(models.Model):
    """Model representing a book genre."""
    name = models.CharField(max_length=200, help_text='Enter a book genre')

    def __str__(self) -> str:
        """String for representing model object"""
        return self.name

class Book(models.Model):
    """Model representing a book (non specific)"""
    title = models.CharField(max_length=200)

    # Foreign Key used because book can only have one author, but authors can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in the file
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN', max_length=13, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

    # ManyToManyField used because genre can contain many books. Books can cover many genres.
    # Genre class has already been defined so we can specify the object above
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')

    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin"""
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'Genre'

    def __str__(self) -> str:
        """String for representing model object"""
        return self.title

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('book-detail', args=[str(self.id)]) # type: ignore

class BookInstance(models.Model):
    """Model representing a specific copy of a book that can be borrowed"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book')
    book = models.ForeignKey(Book, on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On Loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Book Availability',
    )

    class Meta:
        ordering = ['due_back']
        permissions = (('can_mark_returned', 'Set book as returned'),)

    @property
    def is_overdue(self):
        """Determines if the book is overdue based on due date and current date"""
        return bool(self.due_back and date.today() > self.due_back)

    def __str__(self) -> str:
        """String for representing model object"""
        return f'{self.id} ({self.book.title})' # type:ignore

class Author(models.Model):
    """Model representing an author"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField('Date of Birth', null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance"""
        return reverse('author-detail', args=[str(self.id)]) # type: ignore

    def __str__(self) -> str:
        """String for representing model object"""
        return f'{self.first_name}, {self.last_name}'

class Language(models.Model):
    """Model representing a language"""
    name = models.CharField(max_length=200, help_text='Enter the book\'s natural language')

    def __str__(self) -> str:
        """String for representing model object"""
        return self.name
