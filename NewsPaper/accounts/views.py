from django.shortcuts import redirect
from django.contrib.auth.models import User, Group
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .forms import BaseRegisterForm
from news.models import Author, Category


class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/news/'


class UserProfile(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        context['subscribed_categories'] = Category.objects.filter(subscriber=self.request.user.id)
        context['subscribers_list'] = [i.get('pk') for i in self.request.user.category_set.all().values('pk')]

        return context


@login_required
def upgrade_me(request):
    user = request.user
    author_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        author_group.user_set.add(user)
        Author.objects.create(author=user)
    else:
        author_group.user_set.remove(user)
        Author.objects.get(author=user).delete()
    return redirect('/sign/profile/')
