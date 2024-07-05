from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('locations/', views.locations_list, name='locations_list'),
    path('reservations/', views.reservations_list, name='reservations_list'),
    path('reservations/new-reservation/', views.new_reservation, name='new_reservation'),
    path('reservations/past-reservations/', views.past_reservations, name='past_reservations'),
    path('reservations/cancelled-reservations/', views.cancelled_reservations, name='cancelled_reservations'),
    path('reservations/<int:id>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('my_account/', views.my_account, name='my_account'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify_email/', views.verify_email, name='verify_email'),
    path('resend_code/', views.resend_code, name='resend_code'),
]