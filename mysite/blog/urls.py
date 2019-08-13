from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    path('about/', views.About.as_view(), name='about'),
    path('sign-up/', views.SignUp.as_view(), name='signup'),
    path('sign-in/', views.SignIn.as_view(), name='login'),
    path('sign-forget/', views.Forget.as_view(), name='forget'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('message/', views.MessageView.as_view(), name='message'),
    path('me/', views.UserView.as_view(), name='user_info'),
    path('me/message/', views.MessageReply.as_view(), name='message_reply'),
    path('me/myblog/', views.UserBlog.as_view(), name='user_blog'),
    path('me/myblog/headpost/', views.HeadPostView.as_view(), name='headpost'),
    path('me/myblog/collect/', views.CollectBlog.as_view(), name='collect_blog'),
    path('me/myblog/add/', views.BlogAdd.as_view(), name='blog_add'),
    path('me/myblog/delete/', views.BlogDelete.as_view(), name='blog_delete'),
    path('me/comment/', views.CommentEdit.as_view(), name='comment'),
    path('share/xiaohei/', views.ShareView.as_view(), name='cat'),
    path('share/post/', views.SharePost.as_view(), name='share'),
    path('blog/', views.AllBlog.as_view(), name='all_blog'),
    path('blog/<str:blog_id>/', views.BlogView.as_view(), name='blog'),
    path('blog/<str:blog_id>/like/', views.LikeView.as_view(), name='like'),
    path('blog/<str:blog_id>/collect/', views.CollectView.as_view(), name='collect'),
    path('active/', views.UserActive.as_view(), name='active'),
    path('<str:user_id>/', views.OtherHome.as_view(), name='other_home'),
    path('<str:user_id>/blog/', views.OtherBlog.as_view(), name='other_blog'),

    path('', views.Index.as_view(), name='index'),
]
