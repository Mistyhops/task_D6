from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from datetime import datetime
from django.views import View
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User

from .models import Post, Category, Author
from .filters import PostFilter
from .forms import PostForm


class PostList(ListView):
    model = Post
    template_name = 'news/post_list.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-time')
    paginate_by = 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['all_news'] = Post.objects.all()

        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'news/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['time'] = datetime.utcnow()
        context['categories'] = Category.objects.filter(post=self.kwargs.get('pk'))
        if self.request.user.is_authenticated:
            context['subscribers_list'] = [i['pk'] for i in self.request.user.category_set.all().values('pk')]

        return context


class PostSearch(ListView):
    model = Post
    template_name = 'news/post_search.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-time')
    paginate_by = 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post_list = PostFilter(self.request.GET, queryset=Post.objects.all()).qs
        paginator = Paginator(post_list, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            post_filter = paginator.page(page)
        except PageNotAnInteger:
            post_filter = paginator.page(1)
        except EmptyPage:
            post_filter = paginator.page(paginator.num_pages)

        context['all_news'] = Post.objects.all()
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['filterset'] = post_filter

        return context


class PostCreate(PermissionRequiredMixin, CreateView):
    template_name = 'news/post_create.html'
    form_class = PostForm
    permission_required = ('news.add_post')

    # def post(self, request, *args, **kwargs):


    def form_valid(self, form):
        post = form.save()
        category_list = post.category.all().values('subscriber')
        user_list = User.objects.filter(id__in=category_list)

        for user in user_list:
            html_content = render_to_string(
                'news/send_notify_post_create.html',
                {
                    'post_text': post.text[:50],
                    'post': post,
                    'username': user.username,
                }
            )

            email_text = EmailMultiAlternatives(
                subject=post.header,
                body='text',
                from_email='nedgalkin@gmail.com',
                to=[user.email],
            )
            email_text.attach_alternative(html_content, "text/html")
            email_text.send()

        return super(PostCreate, self).form_valid(form)


class PostUpdate(PermissionRequiredMixin, UpdateView):
    template_name = 'news/post_edit.html'
    form_class = PostForm
    queryset = Post.objects.all()
    permission_required = ('news.change_post')


class PostDelete(PermissionRequiredMixin, DeleteView):
    template_name = 'news/post_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'
    permission_required = ('news.delete_post')


class CategorySubscribe(LoginRequiredMixin, View):
    model = Category

    def post(self, request, *args, **kwargs):
        user = self.request.user
        category = get_object_or_404(Category, id=self.kwargs['pk'])
        if category.subscriber.filter(username=self.request.user).exists():
            category.subscriber.remove(user)
        else:
            category.subscriber.add(user)
        return redirect(request.META.get('HTTP_REFERER'))
