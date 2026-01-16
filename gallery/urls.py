from django.urls import path
from . import views
urlpatterns = [
    path('', views.landing, name='landing'),
    path('photographer/dashboard/', views.dashboard, name='dashboard'),
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
    path('photographer/gallery/<int:pk>/analytics/', views.gallery_analytics, name='gallery_analytics'),
    path('author/<int:author_id>/gallery/<int:pk>/', views.gallery_detail, name='gallery_detail'),
    path('photographer/gallery/new/', views.GalleryCreateView.as_view(), name='gallery_create'),
    path('photographer/gallery/<int:pk>/settings/', views.gallery_settings, name='gallery_settings'),
    path('photographer/gallery/<int:pk>/access/', views.gallery_access, name='gallery_access'),
    path('photographer/gallery/<int:pk>/delete/', views.gallery_delete, name='gallery_delete'),
    path('author/<int:author_id>/gallery/<int:pk>/upload/', views.gallery_upload_photos, name='gallery_upload'),
    path('photo/<int:pk>/delete/', views.photo_delete, name='photo_delete'),
    path('api/check_user/', views.check_username_api, name='check_username_api'),
    path('api/reorder_photos/', views.reorder_photos_api, name='reorder_photos_api'),
    path('api/like/<int:photo_id>/', views.toggle_like, name='toggle_like'),
    path('api/track_view/<int:photo_id>/', views.track_photo_view, name='track_photo_view'),
    path('api/comment/<int:photo_id>/', views.save_comment, name='save_comment'),
    path('api/note/<int:photo_id>/', views.save_photographer_note, name='save_note'),
    path('api/access/<int:pk>/update-role/', views.update_access_role, name='update_access_role'),
    path('invite/<uuid:token>/', views.accept_invite, name='accept_invite'),
]