from django.urls import path
from . import views

urlpatterns = [
    path('', views.topic_list, name='topics_list'),
    path('thema/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('ausgabe/<int:expense_id>/bearbeiten/', views.expense_edit, name='expense_edit'),
]