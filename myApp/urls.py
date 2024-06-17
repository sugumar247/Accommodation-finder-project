from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('register/', views.register, name="register"),
    path('my-login/', views.my_login, name="my-login"),
    path('user-logout/', views.user_logout, name="user-logout"),
    path('accommodations/', views.search_accommodations, name='accommodations'),
    path('accommodations/<int:aw>/', views.accommodation_details, name='accommodation-details'),
    path('my-bookings/', views.my_bookings, name='my-bookings'),
    path('book/<int:aw>/', views.book_accommodation, name='book-accommodation'), 
    path('amenities-suggestions/', views.amenities_suggestions, name='amenities-suggestions'),
    path('filter-accommodations/', views.filter_accommodations, name='filter-accommodations'),
]
