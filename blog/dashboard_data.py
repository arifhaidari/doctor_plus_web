from django.utils.translation import gettext as _
import datetime
from .models import Post
from django.http import JsonResponse


def dashboard_charts_data(request):
    posts = Post.objects.filter(blogger__user=request.user)
    months = [
        _("Jan"),
        _("Feb"),
        _("Mar"),
        _("Apr"),
        _("May"),
        _("Jun"),
        _("Jul"),
        _("Aug"),
        _("Sep"),
        _("Oct"),
        _("Nov"),
        _("Des"),
    ]
    this_year_post_counts = [
        len(posts.filter(timestamp__year=datetime.datetime.now().year, timestamp__month=1)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, timestamp__month=2)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, timestamp__month=3)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, timestamp__month=4)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, timestamp__month=5)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, timestamp__month=6)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, timestamp__month=7)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, timestamp__month=8)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, timestamp__month=9)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, timestamp__month=10)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, timestamp__month=11)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, timestamp__month=12)),
    ]
    yearly_posts_label = [x.get("timestamp__year") for x in posts.values("timestamp__year").distinct()]
    yearly_posts_data = [posts.filter(timestamp__year=x).distinct().count() for x in yearly_posts_label]
    # print(this_year_post_counts)

    this_year_post_counts_eng = [
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=0, timestamp__month=1)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=0, timestamp__month=2)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=0, timestamp__month=3)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=0, timestamp__month=4)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=0, timestamp__month=5)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=0, timestamp__month=6)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=0, timestamp__month=7)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=0, timestamp__month=8)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=0, timestamp__month=9)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=0, timestamp__month=10)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=0, timestamp__month=11)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=0, timestamp__month=12)),
    ]
    this_year_post_counts_fa = [
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=1, timestamp__month=1)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=1, timestamp__month=2)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=1, timestamp__month=3)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=1, timestamp__month=4)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=1, timestamp__month=5)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=1, timestamp__month=6)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=1, timestamp__month=7)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=1, timestamp__month=8)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=1, timestamp__month=9)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=1, timestamp__month=10)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=1, timestamp__month=11)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=1, timestamp__month=12)),
    ]
    this_year_post_counts_ps = [
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=2, timestamp__month=1)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=2, timestamp__month=2)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=2, timestamp__month=3)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=2, timestamp__month=4)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=2, timestamp__month=5)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=2, timestamp__month=6)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=2, timestamp__month=7)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=2, timestamp__month=8)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=2, timestamp__month=9)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=2, timestamp__month=10)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=2, timestamp__month=11)),
        len(posts.filter(timestamp__year=datetime.datetime.now().year, language=2, timestamp__month=12)),
    ]
    yearly_posts_data_eng = [posts.filter(timestamp__year=x, language=0).distinct().count() for x in yearly_posts_label]
    yearly_posts_data_fa = [posts.filter(timestamp__year=x, language=1).distinct().count() for x in yearly_posts_label]
    yearly_posts_data_ps = [posts.filter(timestamp__year=x, language=2).distinct().count() for x in yearly_posts_label]
    data = {
        "months": months,
        "this_year_post_counts": this_year_post_counts,
        "yearly_posts_label": yearly_posts_label,
        "yearly_posts_data": yearly_posts_data,
        "this_year_post_counts_eng": this_year_post_counts_eng,
        "this_year_post_counts_fa": this_year_post_counts_fa,
        "this_year_post_counts_ps": this_year_post_counts_ps,
        "yearly_posts_data_eng": yearly_posts_data_eng,
        "yearly_posts_data_fa": yearly_posts_data_fa,
        "yearly_posts_data_ps": yearly_posts_data_ps,
    }
    return JsonResponse(data)
