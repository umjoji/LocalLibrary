import datetime
from typing import Any
from django.contrib import messages
from django.contrib.auth import login
from .forms import NewUserForm,RenewBookModelForm, RenewBookForm
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from .models import Book, BookInstance, Author, Genre
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import BookInstanceSerializer, BookSerializer, AuthorSerializer, LanguageSerializer, GenreSerializer

# Create your views here.
def index(request):
    """View function for home page of site"""

    # Generate counts of main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default
    num_authors = Author.objects.count()

    # number of visits to this view counted by session variable
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits' : num_visits,
    }

    # Render the HTML template with data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user"""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )

class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class based view listing all books on loan"""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinginstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

     # process data if POST request
    if request.method == 'POST':
        # create form instance and populate data
        form = RenewBookModelForm(request.POST)
        if form.is_valid():
        # process data as required
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()

            # redirect to a new url
            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        # if any other method
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})


    context = {
        'form' : form,
        'book_instance' : book_instance,
    }
    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_mark_returned'
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': str(datetime.date.today())}

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_mark_returned'
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_mark_returned'
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_mark_returned'
    model = Book
    fields = '__all__'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_mark_returned'
    model = Book
    fields = '__all__'

class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_mark_returned'
    model = Book
    success_url = reverse_lazy('books')

def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("main:homepage")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="registration/register.html", context={"register_form":form})

@api_view(['GET', 'POST'])
def books_list(request):
    if request.method == 'GET':
        data = Book.objects.all()

        serializer = BookSerializer(data, context={'request': request}, many=True)

        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def book_detail(request, pk):
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BookSerializer(book, data=request.data, context={'request': request})
        if serializer.is_valid():
            return Response(serializer.data)

    if request.method == 'PUT':
        serializer = BookSerializer(book, data=request.data, context={'request': request})
        if serializer.is_valid:
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

