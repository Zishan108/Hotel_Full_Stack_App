# hotel/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home_default'),
    path('<slug:hotel_slug>/', views.home, name='home_with_slug'),
    path('hotels/list/', views.hotel_list, name='hotel_list'),

     # Cookie and storage API endpoints
    path('api/set-preference/', views.set_preference, name='set_preference'),
    path('api/clear-preferences/', views.clear_preferences, name='clear_preferences'),
    path('api/get-user-data/', views.get_user_data, name='get_user_data'),
    path('api/set-comparison/', views.set_hotel_comparison, name='set_hotel_comparison'),
    path('api/save-booking/', views.save_booking_data, name='save_booking_data'),
    path('api/get-booking/', views.get_booking_data, name='get_booking_data'),
    path('api/cookie-consent/', views.cookie_consent, name='cookie_consent'),
    path('api/check-consent/', views.check_consent, name='check_consent'),
]