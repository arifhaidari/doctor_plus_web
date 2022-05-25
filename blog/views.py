from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, JsonResponse
from django.views import generic
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Post
from .forms import UpdateBlogForm, ImagesFormSet, UpdateBloggerForm
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your views here.
class BlogListView(generic.ListView):
    model = Post
    ordering = ("-timestamp",)
    template_name = "blog/blog_list.html"
    paginate_by = 20


class BlogDetailView(generic.DetailView):
    model = Post
    ordering = ("-timestamp",)
    template_name = "blog/blog_details.html"
    context_object_name = "blog"


class BlogSearchView(generic.View):
    model = Post
    ordering = ("-timestamp",)
    template_name = "blog/blog_search.html"
    data = {}

    def get(self, request, *args, **kwargs):
        posts = self.search(self.get_query(request))
        paginator = Paginator(posts, 35)
        page = request.GET.get("page")
        posts = paginator.get_page(page)
        self.data.update({"posts": posts})
        return render(request, self.template_name, self.data)

    def search(self, query):
        return Post.objects.filter(
            Q(title__icontains=query)
            | Q(category__name__icontains=query)
            | Q(category__farsi_name__icontains=query)
            | Q(category__pashto_name__icontains=query)
            # blogger related searches
            | Q(blogger__user__full_name__icontains=query)
            | Q(blogger__user__rtl_full_name__icontains=query)
        ).distinct()

    def get_query(self, request):
        query = request.GET.get("q")
        if query:
            request.session["q"] = query
        else:
            query = request.session["q"]
        return query


class BlogDashboardView(generic.TemplateView):
    template_name = "blog/blog_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(BlogDashboardView, self).get_context_data(**kwargs)
        total_posts = Post.objects.filter(blogger__user=self.request.user)
        print(total_posts)
        data = {
            "total_posts": len(total_posts),
            "engilsh_posts": len(total_posts.filter(language=0)),
            "persian_posts": len(total_posts.filter(language=1)),
            "pashto_posts": len(total_posts.filter(language=2)),
            # "lastweek_posts":
        }
        context.update(data)
        return context


class BlogDashboardPostsListView(generic.ListView):
    model = Post
    ordering = ("-timestamp",)
    paginate_by = 20
    template_name = "blog/dashboard_components/blog_dashboard_posts.html"
    get_queryset = lambda self: Post.objects.filter(blogger__user=self.request.user)

    def post(self, request, *args, **kwargs):
        if request.POST.get("delete_post"):
            print("this post id should be deleted ", request.POST.get("delete_post"))
            get_object_or_404(Post, id=request.POST.get("delete_post")).delete()
            return JsonResponse({"status": "success", "id": request.POST.get("delete_post")})
        return render(request, self.template_name, {})


class BlogUpdateView(generic.UpdateView):
    model = Post
    form_class = UpdateBlogForm
    success_url = "."
    template_name = "blog/dashboard_components/blog_dashboard_eidtpost.html"

    def get_context_data(self, **kwargs):
        context = super(BlogUpdateView, self).get_context_data(**kwargs)
        context["images_form"] = ImagesFormSet(instance=get_object_or_404(Post, id=self.kwargs.get("pk")))
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            form.save()
            image_instances = ImagesFormSet(
                request.POST, request.FILES or None, instance=get_object_or_404(Post, id=self.kwargs.get("pk"))
            )
            if image_instances.is_valid():
                image_instances.save()
                return redirect("blog:dashboard_posts")


class BlogCreateView(generic.CreateView):
    model = Post
    form_class = UpdateBlogForm
    success_url = "."
    template_name = "blog/dashboard_components/blog_dashboard_addpost.html"

    def get_context_data(self, **kwargs):
        context = super(BlogCreateView, self).get_context_data(**kwargs)
        context["images_form"] = ImagesFormSet()
        return context

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.blogger = request.user.blogger
            images_form = ImagesFormSet(request.POST, request.FILES or None, instance=form_instance)
            if images_form.is_valid():
                form_instance.save()
                images_form.save()
                return redirect("blog:dashboard_posts")


class BlogDashboardSearchView(generic.View):
    model = Post
    ordering = ("-timestamp",)
    template_name = "blog/dashboard_components/blog_dashboard_search.html"
    data = {}

    def get(self, request, *args, **kwargs):
        posts = self.search(self.get_query(request))
        paginator = Paginator(posts, 35)
        page = request.GET.get("page")
        posts = paginator.get_page(page)
        self.data.update({"posts": posts})
        return render(request, self.template_name, self.data)

    def search(self, query):
        return Post.objects.filter(
            Q(title__icontains=query)
            | Q(category__name__icontains=query)
            | Q(category__farsi_name__icontains=query)
            | Q(category__pashto_name__icontains=query)
            # blogger related searches
            | Q(blogger__user__full_name__icontains=query)
            | Q(blogger__user__rtl_full_name__icontains=query)
        ).distinct()

    def get_query(self, request):
        query = request.GET.get("q")
        if query:
            request.session["q"] = query
        else:
            query = request.session["q"]
        return query


class BloggerUpdateView(generic.UpdateView):
    model = User
    form_class = UpdateBloggerForm
    success_url = "/blog/dashboard/"
    template_name = "blog/dashboard_components/blog_dashboard_profilesettings.html"

    def get(self, request, *args, **kwargs):
        if not self.kwargs.get("pk") == self.request.user.id:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return render(request, self.template_name, {"form": form})

    forbidden = lambda self: HttpResponseForbidden()
