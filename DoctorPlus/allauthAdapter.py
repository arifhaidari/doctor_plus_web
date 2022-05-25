from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class MyDefaultAccountAdapter(DefaultAccountAdapter):
    # def get_login_redirect_url(self, request):
    #     path = reverse("user:social_user_adp", kwargs={"pk": request.user.id})
    #     print("REEETURN path -- ", path)
    #     return path
    # def get_connect_redirect_url(self, request, socialaccount):
    #     return "/some/text/"
    pass


class MyDefaultSocialAccountAdapter(DefaultSocialAccountAdapter):
    # only calls for the first time
    # def new_user(self, request, sociallogin):
    #     pass
    # def get_connect_redirect_url(self, request, socialaccount):
    #     # url = super().get_connect_redirect_url(request, socialaccount)
    #     url = reverse("user:social_user_adp", kwargs={"pk": request.user.id})
    #     print("the ----- path ---- to redirect ---- : ", url)
    #     return url
    # path = "/accounts/{username}/"
    # return path.format(username=request.user.username)

    # def get_connect_redirect_url(self, request, socialaccount):
    #     r = reverse("user:social_user_adp", kwargs={"pk": request.user.id})
    #     print("p1 > r :  ", r)
    #     return r

    # def save_user(self, request, sociallogin, form=None):
    #     super(self.__class__, self).save_user(request, sociallogin, form=form)
    #     r = reverse("user:social_user_adp", kwargs={"pk": request.user.id})
    #     print("p2 > r :  ", r)
    #     return r

    pass
