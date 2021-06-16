from django.urls import path

from .views import PostList, PostDetail, PostCreate, PostUpdate, PostDelete, PostSearch, CategorySubscribe


urlpatterns = [
    path('', PostList.as_view()),
    path('<int:pk>/', PostDetail.as_view(), name='post_detail'),
    path('create/', PostCreate.as_view(), name='post_create'),
    path('<int:pk>/edit/', PostUpdate.as_view(), name='post_edit'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('search/', PostSearch.as_view(), name='post_search'),
    path('category/<int:pk>/subscribe', CategorySubscribe.as_view(), name='subscribe'),
]
