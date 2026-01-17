import io, json, os
import urllib, base64
import matplotlib.pyplot as plt
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Max, Count, Sum, Q, Prefetch
from django.db.models.functions import TruncDate
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.contrib import messages
from .models import Gallery, Photo, ClientChoice, GalleryAccess, GalleryInvite
from .forms import GallerySettingsForm, GalleryAccessForm, PhotoUploadForm, InviteCreateForm
from users.models import CustomUser
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView
@login_required
def check_username_api(request):
    username = request.GET.get('username', '').strip()
    exists = CustomUser.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})
@require_POST
@login_required
def reorder_photos_api(request):
    try:
        data = json.loads(request.body)
        order_map = data.get('order', [])
        if not order_map: return JsonResponse({'status': 'ok'})
        first_photo = Photo.objects.get(pk=order_map[0])
        if first_photo.gallery.photographer != request.user and not request.user.is_superuser:
            return JsonResponse({'error': 'Forbidden'}, status=403)
        photos_to_update = [Photo(id=pid, sequence_number=i) for i, pid in enumerate(order_map)]
        Photo.objects.bulk_update(photos_to_update, ['sequence_number'])
        return JsonResponse({'status': 'ok'})
    except Exception as e: return JsonResponse({'error': str(e)}, status=400)
@require_POST
@login_required
def track_photo_view(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    choice, created = ClientChoice.objects.get_or_create(photo=photo, client=request.user)
    if not choice.is_viewed:
        choice.is_viewed = True
        choice.save()
    return JsonResponse({'status': 'ok'})
def landing(request): return render(request, 'gallery/landing.html')
@require_POST
@login_required
def update_access_role(request, pk):
    access = get_object_or_404(GalleryAccess, pk=pk)
    if access.gallery.photographer != request.user and not request.user.is_superuser:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    
    data = json.loads(request.body)
    new_role = data.get('role')
    if new_role not in ['CLIENT', 'VIEWER']:
        return JsonResponse({'error': 'Invalid role'}, status=400)
    
    access.role = new_role
    access.save()
    return JsonResponse({'status': 'ok'})

@require_POST
@login_required
def save_photographer_note(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    if photo.gallery.photographer != request.user and not request.user.is_superuser:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    data = json.loads(request.body)
    note = data.get('note', '').strip()
    photo.photographer_note = note
    photo.save()
    return JsonResponse({'status': 'ok'})

@require_POST
@login_required
def save_comment(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    data = json.loads(request.body)
    comment = data.get('comment', '').strip()
    choice, created = ClientChoice.objects.get_or_create(photo=photo, client=request.user)
    choice.comment = comment
    choice.save()
    return JsonResponse({'status': 'ok'})

def check_gallery_expiration(gallery):
    if gallery.is_active and gallery.is_expired:
        gallery.is_active = False
        gallery.save()
    return gallery.is_active

@login_required
def dashboard(request):
    if request.user.role == CustomUser.Role.CLIENT: return redirect('client_dashboard')
    if request.user.role != CustomUser.Role.PHOTOGRAPHER and not request.user.is_superuser: return HttpResponseForbidden()
    
    galleries_qs = Gallery.objects.filter(photographer=request.user)
    for g in galleries_qs:
        check_gallery_expiration(g)
        
    include_author = request.GET.get('include_author') == 'true'
    likes_filter = Q(photos__choice__is_liked=True)
    if not include_author:
        likes_filter &= ~Q(photos__choice__client=request.user)
    
    galleries = Gallery.objects.filter(photographer=request.user).annotate(
        total_likes_count=Count('photos__choice', filter=likes_filter)
    ).order_by('-created_at')
    
    total_galleries = galleries.count()
    total_likes_global = sum(g.total_likes_count for g in galleries)
    top_galleries = sorted(galleries, key=lambda x: x.total_likes_count, reverse=True)[:5]
    chart_top_labels = [g.title for g in top_galleries]
    chart_top_data = [g.total_likes_count for g in top_galleries]
    active_count = galleries.filter(is_active=True).count()
    inactive_count = total_galleries - active_count
    chart_status_data = [active_count, inactive_count]
    context = {
        'galleries': galleries,
        'total_galleries': total_galleries,
        'total_likes_global': total_likes_global,
        'include_author': include_author,
        'chart_top_labels': json.dumps(chart_top_labels),
        'chart_top_data': json.dumps(chart_top_data),
        'chart_status_data': json.dumps(chart_status_data),
    }
    return render(request, 'gallery/dashboard.html', context)
@login_required
def gallery_analytics(request, pk):
    gallery = get_object_or_404(Gallery, pk=pk)
    if gallery.photographer != request.user and not request.user.is_superuser:
        return HttpResponseForbidden()
    include_author = request.GET.get('include_author') == 'true'
    cc_filter = Q(photo__gallery=gallery)
    if not include_author:
        cc_filter &= ~Q(client=request.user)
    access_filter = Q(gallery=gallery, last_viewed_at__isnull=False)
    if not include_author:
        access_filter &= ~Q(user=request.user)
    total_photos = gallery.photos.count()
    unique_selected = ClientChoice.objects.filter(cc_filter, is_liked=True).values('photo').distinct().count()
    viewed_ids = set(ClientChoice.objects.filter(cc_filter, is_viewed=True).values_list('photo', flat=True))
    liked_ids = set(ClientChoice.objects.filter(cc_filter, is_liked=True).values_list('photo', flat=True))
    just_viewed_count = len(viewed_ids - liked_ids)
    unviewed_count = total_photos - unique_selected - just_viewed_count
    if unviewed_count < 0: unviewed_count = 0
    viewers_list = GalleryAccess.objects.filter(access_filter).select_related('user').order_by('-last_viewed_at')
    likers_ids = ClientChoice.objects.filter(cc_filter, is_liked=True).values_list('client', flat=True).distinct()
    likers_users = CustomUser.objects.filter(id__in=likers_ids)
    likers_data = []
    for user in likers_users:
        count = ClientChoice.objects.filter(photo__gallery=gallery, client=user, is_liked=True).count()
        likers_data.append({'user': user, 'count': count})
    likers_data.sort(key=lambda x: x['count'], reverse=True)
    liked_photos_map = set(ClientChoice.objects.filter(cc_filter, is_liked=True).values_list('photo_id', flat=True))
    import os
    photos_qs = gallery.photos.all().order_by('sequence_number').prefetch_related('choice__client')
    photos_data = []
    for p in photos_qs:
        choices = p.choice.exclude(comment='')
        comment_list = [f"{c.client.username}: {c.comment}" for c in choices]
        all_comments = " | ".join(comment_list)
        photos_data.append({
            'id': p.id,
            'thumbnail': p.thumbnail.url if p.thumbnail else p.image.url,
            'full_url': p.image.url,
            'sequence_number': p.sequence_number,
            'is_liked': p.id in liked_photos_map,
            'comment': all_comments,
            'photographer_note': p.photographer_note,
            'filename': p.original_filename or os.path.basename(p.image.name)
        })
    activity_likes = ClientChoice.objects.filter(cc_filter, is_liked=True).annotate(date=TruncDate('timestamp')).values('date').annotate(count=Count('id')).order_by('date')
    activity_views = ClientChoice.objects.filter(cc_filter, is_viewed=True).annotate(date=TruncDate('timestamp')).values('date').annotate(count=Count('id')).order_by('date')
    activity_comments = ClientChoice.objects.filter(cc_filter).exclude(comment='').annotate(date=TruncDate('timestamp')).values('date').annotate(count=Count('id')).order_by('date')
    
    all_dates = sorted(list(set(
        [item['date'] for item in activity_likes] + 
        [item['date'] for item in activity_views] + 
        [item['date'] for item in activity_comments]
    )))
    
    def get_count_for_date(qs, date):
        for item in qs:
            if item['date'] == date: return item['count']
        return 0

    chart_likes = [get_count_for_date(activity_likes, d) for d in all_dates]
    chart_views = [get_count_for_date(activity_views, d) for d in all_dates]
    chart_comments = [get_count_for_date(activity_comments, d) for d in all_dates]

    activity_log = ClientChoice.objects.filter(cc_filter).select_related('client', 'photo').order_by('-timestamp')
    
    all_comments_list = activity_log.exclude(comment='')

    top_filter = Q(choice__is_liked=True)
    if not include_author:
        top_filter &= ~Q(choice__client=request.user)
    top_photos_qs = gallery.photos.annotate(
        likes_count=Count('choice', filter=top_filter)
    ).filter(likes_count__gt=0).order_by('-likes_count')[:10]
    top_labels = [f"#{p.sequence_number}" for p in top_photos_qs]
    top_data = [p.likes_count for p in top_photos_qs]
    context = {
        'gallery': gallery,
        'total_photos': total_photos,
        'selected_count': unique_selected,
        'viewed_count': just_viewed_count,
        'unviewed_count': unviewed_count,
        'photos_data': photos_data,
        'viewers_list': viewers_list,
        'likers_data': likers_data,
        'include_author': include_author,
        'top_labels': json.dumps(top_labels),
        'top_data': json.dumps(top_data),
        'all_comments_list': all_comments_list,
        'activity_log': activity_log,
        'activity_dates': json.dumps(all_dates, cls=DjangoJSONEncoder),
        'activity_likes': json.dumps(chart_likes),
        'activity_views': json.dumps(chart_views),
        'activity_comments': json.dumps(chart_comments),
    }
    return render(request, 'gallery/gallery_analytics.html', context)
@login_required
def client_dashboard(request):
    if request.user.role != CustomUser.Role.CLIENT: return redirect('dashboard')
    accesses = GalleryAccess.objects.filter(user=request.user, gallery__is_active=True)
    return render(request, 'gallery/client_dashboard.html', {'accesses': accesses})
@login_required
def gallery_detail(request, author_id, pk):
    gallery = get_object_or_404(Gallery, pk=pk)
    if gallery.photographer.id != author_id: return HttpResponseForbidden("Неверная ссылка")
    
    check_gallery_expiration(gallery)
    
    user = request.user
    is_owner = (user == gallery.photographer or user.is_superuser)
    can_view = False
    can_like = False
    role_name = "Гость"
    if is_owner:
        can_view = True
        can_like = True
        role_name = "Владелец"
    elif gallery.is_public:
        can_view = True
        role_name = "Публичный"
    access = GalleryAccess.objects.filter(gallery=gallery, user=user).first()
    if access:
        can_view = True
        role_name = access.get_role_display()
        if access.role == 'CLIENT': can_like = True
        access.last_viewed_at = timezone.now()
        access.save()
    if not can_view: return render(request, 'gallery/access_denied.html', status=403)
    can_see_others = False
    if is_owner: can_see_others = True
    elif gallery.viewers_see_likes: can_see_others = True
    elif access and access.role == 'CLIENT':
        if gallery.is_common_likes or gallery.clients_see_others: can_see_others = True
    photos = gallery.photos.all()
    view_filter = request.GET.get('filter', 'ALL')
    if gallery.is_common_likes:
        my_likes_ids = set(ClientChoice.objects.filter(photo__gallery=gallery, is_liked=True).values_list('photo_id', flat=True))
    else:
        my_likes_ids = set(ClientChoice.objects.filter(photo__gallery=gallery, client=user, is_liked=True).values_list('photo_id', flat=True))
    
    photos = photos.prefetch_related('choice__client')
    
    others_likes_map = {}
    if can_see_others:
        counts = ClientChoice.objects.filter(photo__gallery=gallery, is_liked=True).values('photo_id').annotate(count=Count('id'))
        for item in counts: others_likes_map[item['photo_id']] = item['count']
    if view_filter == 'LIKED':
        if is_owner and not gallery.is_common_likes:
            client_filter_id = request.GET.get('client_id')
            if client_filter_id:
                photos = photos.filter(choice__client_id=client_filter_id, choice__is_liked=True)
            else:
                photos = photos.filter(choice__is_liked=True).distinct()
        else:
            photos = photos.filter(id__in=my_likes_ids)
    photo_states = {}
    for photo in photos:
        is_liked_by_me = photo.id in my_likes_ids
        total_count = others_likes_map.get(photo.id, 0)
        if not can_see_others: total_count = 1 if is_liked_by_me else 0
        show_count = False
        if gallery.is_common_likes:
            if not can_like and can_see_others and total_count > 0: show_count = True
        else:
            if can_see_others and total_count > 0: show_count = True
        photo_states[photo.id] = {'liked_by_me': is_liked_by_me, 'total_likes': total_count, 'show_count': show_count}
    clients_with_likes = []
    if is_owner:
        clients_with_likes = CustomUser.objects.filter(client_choices__photo__gallery=gallery, client_choices__is_liked=True).distinct()
    context = {
        'gallery': gallery,
        'photos': photos,
        'photo_states': photo_states,
        'liked_count': len(my_likes_ids),
        'is_owner': is_owner,
        'can_like': can_like and gallery.is_active,
        'role_name': role_name,
        'upload_form': PhotoUploadForm() if is_owner else None,
        'view_filter': view_filter,
        'clients_with_likes': clients_with_likes,
        'current_client_id': int(request.GET.get('client_id')) if request.GET.get('client_id') else None
    }
    return render(request, 'gallery/detail.html', context)
@require_POST
@login_required
def toggle_like(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    gallery = photo.gallery
    user = request.user
    if not gallery.is_active and user != gallery.photographer: return JsonResponse({'error': 'Gallery is closed'}, status=403)
    is_owner = (user == gallery.photographer or user.is_superuser)
    access = GalleryAccess.objects.filter(gallery=gallery, user=user).first()
    can_like = is_owner or (access and access.role == 'CLIENT')
    if not can_like: return JsonResponse({'error': 'Forbidden'}, status=403)
    if gallery.is_expired: return JsonResponse({'error': 'Expired'}, status=403)
    choice, created = ClientChoice.objects.get_or_create(photo=photo, client=user)
    if not choice.is_viewed: choice.is_viewed = True; choice.save()
    if gallery.is_common_likes:
        is_already_selected = ClientChoice.objects.filter(photo=photo, is_liked=True).exists()
        if is_already_selected:
            ClientChoice.objects.filter(photo=photo).update(is_liked=False)
            is_liked_now = False
        else:
            if gallery.total_selection_limit > 0:
                total = ClientChoice.objects.filter(photo__gallery=gallery, is_liked=True).values('photo').distinct().count()
                if total >= gallery.total_selection_limit: return JsonResponse({'error': 'Total limit reached'}, status=400)
            choice.is_liked = True
            choice.is_viewed = True
            choice.save()
            is_liked_now = True
        total_count = ClientChoice.objects.filter(photo__gallery=gallery, is_liked=True).values('photo').distinct().count()
        return JsonResponse({'liked': is_liked_now, 'my_total_count': total_count, 'photo_total_likes': 0, 'can_see_others': False})
    else:
        if not choice.is_liked:
            user_likes = ClientChoice.objects.filter(photo__gallery=gallery, client=user, is_liked=True).count()
            if user_likes >= gallery.max_selection_count: return JsonResponse({'error': 'Personal limit reached'}, status=400)
            if gallery.total_selection_limit > 0:
                total = ClientChoice.objects.filter(photo__gallery=gallery, is_liked=True).count()
                if total >= gallery.total_selection_limit: return JsonResponse({'error': 'Gallery total limit reached'}, status=400)
        choice.is_liked = not choice.is_liked
        choice.save()
        can_see_others = False
        if is_owner: can_see_others = True
        elif gallery.viewers_see_likes: can_see_others = True
        elif access and access.role == 'CLIENT' and gallery.clients_see_others: can_see_others = True
        my_total = ClientChoice.objects.filter(photo__gallery=gallery, client=user, is_liked=True).count()
        photo_total = ClientChoice.objects.filter(photo=photo, is_liked=True).count() if can_see_others else (1 if choice.is_liked else 0)
        return JsonResponse({'liked': choice.is_liked, 'my_total_count': my_total, 'photo_total_likes': photo_total, 'can_see_others': can_see_others})
@login_required
def gallery_upload_photos(request, author_id, pk):
    gallery = get_object_or_404(Gallery, pk=pk)
    if gallery.photographer != request.user and not request.user.is_superuser:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Forbidden'}, status=403)
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        if images:
            last_seq = gallery.photos.aggregate(Max('sequence_number'))['sequence_number__max'] or 0
            for i, image in enumerate(images):
                p = Photo(
                    gallery=gallery, 
                    image=image, 
                    original_filename=image.name, # Сохраняем имя
                    sequence_number=last_seq + i + 1, 
                    status='UNVIEWED'
                )
                p.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok', 'count': len(images)})
            
            messages.success(request, f'Загружено {len(images)} фото.')
    return redirect('gallery_detail', author_id=author_id, pk=pk)
@login_required
def photo_delete(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    gallery = photo.gallery
    if gallery.photographer != request.user and not request.user.is_superuser: return HttpResponseForbidden()
    if request.method == 'POST': photo.delete(); messages.success(request, 'Фото удалено.')
    return redirect('gallery_detail', author_id=gallery.photographer.id, pk=gallery.id)
class GalleryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Gallery
    form_class = GallerySettingsForm
    template_name = 'gallery/gallery_settings.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs); ctx['is_create'] = True; ctx['access_form'] = GalleryAccessForm(self.request.POST or None); return ctx
    def form_valid(self, form):
        ctx = self.get_context_data()
        if ctx['access_form'].is_valid():
            self.object = form.save(commit=False); self.object.photographer = self.request.user; self.object.is_public = ctx['access_form'].cleaned_data['is_public']; self.object.save()
            users_data = ctx['access_form'].cleaned_data.get('users_data', '')
            if users_data:
                for uname in [u.strip() for u in users_data.split(',') if u.strip()]:
                    try: u = CustomUser.objects.get(username=uname); GalleryAccess.objects.get_or_create(gallery=self.object, user=u, defaults={'role': 'CLIENT'})
                    except: pass
            messages.success(self.request, 'Создано.'); return redirect('gallery_detail', author_id=self.request.user.id, pk=self.object.pk)
        return self.render_to_response(self.get_context_data(form=form))
    def test_func(self): return self.request.user.role == CustomUser.Role.PHOTOGRAPHER or self.request.user.is_superuser
@login_required
def gallery_settings(request, pk):
    gallery = get_object_or_404(Gallery, pk=pk)
    if gallery.photographer != request.user and not request.user.is_superuser: return HttpResponseForbidden()
    if request.method == 'POST':
        form = GallerySettingsForm(request.POST, instance=gallery)
        if form.is_valid(): form.save(); messages.success(request, 'Сохранено'); return redirect('dashboard')
    else: form = GallerySettingsForm(instance=gallery)
    return render(request, 'gallery/gallery_settings.html', {'form': form, 'gallery': gallery, 'is_create': False})
@login_required
def gallery_access(request, pk):
    gallery = get_object_or_404(Gallery, pk=pk)
    if gallery.photographer != request.user and not request.user.is_superuser: return HttpResponseForbidden()
    if request.method == 'POST' and 'access_submit' in request.POST:
        f = GalleryAccessForm(request.POST, instance=gallery)
        if f.is_valid():
            f.save()
            is_public_new = f.cleaned_data['is_public']
            if is_public_new:
                for access_obj in GalleryAccess.objects.filter(gallery=gallery):
                    if access_obj.role != 'CLIENT':
                        access_obj.original_role = access_obj.role
                        access_obj.role = 'CLIENT'
                        access_obj.save()
            else:
                for access_obj in GalleryAccess.objects.filter(gallery=gallery):
                    if access_obj.original_role:
                        access_obj.role = access_obj.original_role
                        access_obj.original_role = None
                        access_obj.save()
                    elif access_obj.role == 'CLIENT': # Если не было original_role, но текущая роль CLIENT (была принудительно поставлена), то возвращаем на VIEWER
                        access_obj.role = 'VIEWER'
                        access_obj.save()
            
            users_data = f.cleaned_data.get('users_data', '')
            new_user_role = request.POST.get('new_user_role', 'VIEWER') # Получаем роль для новых пользователей
            if users_data:
                for uname in [u.strip() for u in users_data.split(',') if u.strip()]:
                    try: u = CustomUser.objects.get(username=uname); GalleryAccess.objects.get_or_create(gallery=gallery, user=u, defaults={'role': new_user_role})
                    except: pass
            messages.success(request, 'Обновлено.'); return redirect('gallery_access', pk=pk)
    if request.method == 'POST' and 'invite_submit' in request.POST:
        f = InviteCreateForm(request.POST)
        if f.is_valid(): i = f.save(commit=False); i.gallery = gallery; i.save(); messages.success(request, 'Ссылка создана.'); return redirect('gallery_access', pk=pk)
    if request.method == 'POST' and 'remove_user_access' in request.POST:
        GalleryAccess.objects.filter(gallery=gallery, user_id=request.POST.get('remove_user_access')).delete(); return redirect('gallery_access', pk=pk)
    if request.method == 'POST' and 'delete_invite' in request.POST:
        GalleryInvite.objects.filter(gallery=gallery, id=request.POST.get('delete_invite')).delete(); return redirect('gallery_access', pk=pk)
    return render(request, 'gallery/gallery_access.html', {'gallery': gallery, 'access_form': GalleryAccessForm(instance=gallery), 'invite_form': InviteCreateForm(), 'invites': gallery.invites.all(), 'access_list': gallery.access_list.all()})
@login_required
def gallery_delete(request, pk):
    gallery = get_object_or_404(Gallery, pk=pk)
    if gallery.photographer != request.user and not request.user.is_superuser: return HttpResponseForbidden()
    if request.method == 'POST': gallery.delete(); return redirect('dashboard')
    return render(request, 'gallery/gallery_confirm_delete.html', {'object': gallery})
@login_required
def accept_invite(request, token):
    invite = get_object_or_404(GalleryInvite, token=token)
    if not invite.is_valid: messages.error(request, 'Invalid link'); return redirect('landing')
    if not GalleryAccess.objects.filter(gallery=invite.gallery, user=request.user).exists():
        GalleryAccess.objects.create(gallery=invite.gallery, user=request.user, role=invite.role)
        if invite.usage_limit > 0: invite.usage_count += 1; invite.save()
    return redirect('gallery_detail', author_id=invite.gallery.photographer.id, pk=invite.gallery.pk)
