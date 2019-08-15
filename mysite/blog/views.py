# Create your views here.
# coding=utf-8
from django.shortcuts import render, redirect, reverse, Http404
from django.http import JsonResponse
from .models import Articles, User, Comments, LikeCollect, Share, Message
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.template.loader import render_to_string
import re
import random
from uuid import uuid1
from utils.mixin import LoginRequiredMixIn
from django.db.models import Q              # or查询
# 分页模块
from django.core.paginator import Paginator

from celery_tasks.task import send_email

# 加密模块
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous.exc import SignatureExpired
serializer = Serializer('cjm666', 7200)


def get_user_info(user, self=True):
    """获取用户详细信息
    user: class:User
    self: [bool:True]表示自己访问
    """
    info = {}
    try:
        blog_all = user.articles_set.all().order_by('-update_time')
        if not self:
            # 不是用户自己只获取公开的博客
            blog_all = blog_all.filter(is_secret=False)
            info['not_self'] = True
        # 用户评论数
        info['comment_count'] = user.comments_set.all().count()
    except:
        return {'username': '厉害了亲，怎么访问的'}
    # 用户头像
    if user.head_ico:
        info['head_ico'] = user.head_ico.url
    else:
        # 随机头像
        info['head_ico'] = '/static/images/head_ico/head%s.jpeg' % random.randint(0, 27)
    # 用户创建时间
    info['create_time'] = user.create_time
    # 用户id
    info['user_id'] = user.user_id
    # 用户名
    info['username'] = user.username
    # 用户博客数
    info['blog_count'] = blog_all.count()
    info['blog_all'] = list()
    # 用户博客总获赞数
    info['love'] = 0
    # 用户被评论总数
    info['comments_count'] = 0
    for blog in blog_all:
        info['love'] += int(blog.love)
        comments = blog.comments_set.all()
        info['comments_count'] += comments.count()
        info['blog_all'].append({'blog': blog, 'comment_count': comments.count()})

    return info


def active_email(user):
    """发送激活邮件"""
    if user.is_active:
        return
    confirm = {'id': user.user_id}
    token = serializer.dumps(confirm).decode()
    send_email.delay(user.email, user.username, token)


# TODO 暂时先这样生成摘要，有待改进
def md2summary(content):
    """自动获取markdown摘要
    只获取其中标题文本"""
    return ','.join(re.findall('#+\s+(\S+)', content)[:6])[:50]


class ArticlesEditorModelForm(forms.ModelForm):
    description = forms.TextInput()

    class Meta:
        model = Articles
        fields = ('title', 'description', 'body', 'is_secret')          # []不行

        # 自定义表单格式
        widgets = {
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 2, 'placeholder': '为空时自动生成摘要'}),
        }


class CommentsEditorModelForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('content',)


class HeadPostModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('head_ico',)


class SharePostForm(forms.ModelForm):
    class Meta:
        model = Share
        fields = ('description', 'img')
        # 自定义表单格式
        widgets = {
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 2, 'placeholder': '这么好看的你有什么想分享下呢'}),
        }


class Index(View):
    '''主界面类视图'''
    def get(self, request):
        try:
            # 首页大图博客
            blog_index = Articles.objects.get(blog_id='top')
        except:
            blog_index = Articles.objects.get(blog_id='1')       
        blog = Articles.objects.filter(is_secret=False)
        blog_love = Paginator(blog.order_by('love'), 5).page(1)
        blog_time = Paginator(blog.order_by('-update_time'), 10).page(1)
        share = Paginator(Share.objects.all().order_by('-update_time'), 2).page(1)

        return render(request, 'index.html', {'blog_index': blog_index, 'blog_time': blog_time,
                                              'blog_like': blog_love, 'share': share})


class About(View):
    """
    关于我类视图
    """
    def get(self, request):

        return render(request, 'about.html')


class ShareView(View):
    """
    分享类视图
    """
    def get(self, request):
        share = Share.objects.all().order_by('-update_time')
        share_page = Paginator(share, 5)
        # 获取页码
        try:
            page = int(request.GET.get('page', 1))
        except:
            page = 1
        if page > share_page.num_pages:
            # 页码超出范围则置为1
            page = 1

        page_item = share_page.page(page)
        info = {'share_page': page_item.object_list}        # 这里.object_list没拿的话会丢死一页数据，好像是字典传值引起的，暂时不知道具体原因

        # 页码控制
        info.update({'page_range_left': range(1, page)})
        info.update({'page_range_right': range(page+1, share_page.num_pages+1)})
        info['c_page'] = page
        if not page_item.has_previous():
            info['previous'] = 'disabled'
        else:
            info['p_page'] = page_item.previous_page_number()

        if not page_item.has_next():
            info['next'] = 'disabled'
        else:
            info['n_page'] = page_item.next_page_number()

        return render(request, 'share.html', info)

    def post(self, request):
        form = SharePostForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, 'share_post.html', {'form': form})
        # form.save()           官方方法应该是新建一个User对象且只传了一个img参数
        # Share.objects.create(user=request.user, )
        form.save()
        # request.user.head_ico.save(form.data.get('head_ico'), request.FILES.get('head_ico'))
        return redirect(reverse('blog:cat'))


class SharePost(LoginRequiredMixIn, View):
    """
    上传分享
    """
    def get(self, request):
        form = SharePostForm()
        return render(request, 'share_post.html', {'form': form})

    def post(self, request):
        form = SharePostForm(request.POST, request.FILES, instance=Share(auth=request.user))
        if not form.is_valid():
            return render(request, 'share_post.html', {'form': form})
        # form.save()           官方方法应该是新建一个User对象且只传了一个img参数
        # Share.objects.create(user=request.user, )
        form.save()
        # request.user.head_ico.save(form.data.get('head_ico'), request.FILES.get('head_ico'))
        return redirect(reverse('blog:cat'))


class AllBlog(View):
    def get(self, request):
        blog_all = Articles.objects.filter(is_secret=False).order_by('-update_time')
        blog_page = Paginator(blog_all, 15)
        try:
            page = int(request.GET.get('page', 1))
        except:
            page = 1
        if page > blog_page.num_pages:
            # 页码超出范围则置为1
            page = 1
        page_item = blog_page.page(page)
        info = {'blog_page': page_item.object_list}
        # 页码控制
        info.update({'page_range_left': range(1, page)})
        info.update({'page_range_right': range(page + 1, blog_page.num_pages + 1)})
        info['c_page'] = page
        if not page_item.has_previous():
            info['previous'] = 'disabled'
        else:
            info['p_page'] = page_item.previous_page_number()

        if not page_item.has_next():
            info['next'] = 'disabled'
        else:
            info['n_page'] = page_item.next_page_number()
        info['head_ico'] = '/static/images/head_ico/head%s.jpeg' % random.randint(0, 27)
        return render(request, 'all_blog.html', info)


class UserBlog(LoginRequiredMixIn, View):
    """
    用户个人博客管理类视图
    """
    def get(self, request):
        # 所有博客
        blog_all = request.user.articles_set.all().order_by('-create_time')
        # 分页，10个每页
        blog_page = Paginator(blog_all, 3)
        # 获取页码
        try:
            page = int(request.GET.get('page', 1))
        except:
            page = 1
        if page > blog_page.num_pages:
            # 页码超出范围则置为1
            page = 1

        return render(request, 'blog_list.html', {'blog_page': blog_page.page(page)})


class CollectBlog(LoginRequiredMixIn, View):
    """
    用户个人收藏显示管理类视图
    """
    def get(self, request):
        # 下面获取到的只是一个LikeCollect对象
        blog_all_collect = request.user.likecollect_set.filter(collected=True)
        # 获取Articles对象
        blog_all = [blog.article for blog in blog_all_collect]

        blog_page = Paginator(blog_all, 5)
        try:
            page = int(request.GET.get('page', 1))
        except:
            page = 1
        if page > blog_page.num_pages:
            # 页码超出范围则置为1
            page = 1
        info = dict()

        info['blog_page'] = blog_page.page(page)
        info['my_collect'] = True
        info['edit_stop'] = True
        return render(request, 'blog_list.html', info)


class OtherBlog(View):
    """
    浏览其他用户博客列表类视图
    """
    def get(self, request, user_id):
        # 所有博客
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            raise Http404('找不到此用户')
        if request.user == user:
            # 如果是本人访问则跳转到自己的博客页
            return redirect(reverse('blog:user_blog'))
        blog_all = user.articles_set.filter(is_secret=False).order_by('-create_time')

        # 分页，10个每页
        blog_page = Paginator(blog_all, 10)
        # 获取页码
        try:
            page = int(request.GET.get('page', 1))
        except:
            page = 1
        if page > blog_page.num_pages:
            # 页码超出范围则置为1
            page = 1

        return render(request, 'blog_list.html', {'blog_page': blog_page.page(page),
                                                  'edit_stop': True, 'username': user.username})


class UserView(LoginRequiredMixIn, View):
    """
    用户界面管理类
    """
    def get(self, request):
        info = get_user_info(request.user)
        # 收藏数
        info['collect_count'] = request.user.likecollect_set.filter(collected=True).count()
        # 未读消息数量
        info['message'] = request.user.own_message.filter(has_read=False).count()
        # 所有消息数量
        info['message_all'] = request.user.own_message.all().count()
        return render(request, 'user_info.html', info)


class HeadPostView(LoginRequiredMixIn, View):
    """
    上传图像类视图
    """
    def get(self, request):
        return render(request, 'headpost.html', {'form': HeadPostModelForm()})

    def post(self, request):
        form = HeadPostModelForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, 'headpost.html', {'form': form})
        # form.save()           官方方法应该是新建一个User对象且只传了一个img参数
        request.user.head_ico = request.FILES.get('head_ico')
        request.user.save()
        # request.user.head_ico.save(form.data.get('head_ico'), request.FILES.get('head_ico'))
        return redirect(reverse('blog:user_info'))


class OtherHome(View):
    """
    其他用户信息浏览类视图
    """
    def get(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            raise Http404('找不到此用户')
        if request.user == user:
            # 如果是本人访问则跳转到自己的详情页
            return redirect(reverse('blog:user_info'))
        info = get_user_info(user, False)

        return render(request, 'user_info.html', info)


class BlogView(View):
    """
    博客详细信息显示类视图
    """
    def get(self, request, blog_id):
        try:
            blog = Articles.objects.get(blog_id=blog_id)
        except Articles.DoesNotExist:
            raise Http404()

        comments_count = blog.comments_set.count()
        print(comments_count)

        # 不是自己浏览则浏览次数加一
        if not request.user == blog.author_name:
            look_times = blog.look_times + 1
            # 不更新时间
            Articles.objects.filter(blog_id=blog_id).update(look_times=look_times)
            blog = Articles.objects.get(blog_id=blog_id)
        form = CommentsEditorModelForm()
        info = {'blog': blog, 'comments_count': comments_count, 'form': form, 'path': request.path}
        # 判断有无删除权限
        if request.user == blog.author_name:
            info['delete_able'] = True

        # 没有删除权限则判断用户是否已登录决定是否可以收藏
        elif request.user.is_authenticated:
            info['collect_able'] = True
            collect = LikeCollect.objects.filter(article=blog, username=request.user)
            # print(collect, type(collect), list(collect))
            if not collect:
                ret = '收藏'
            elif collect[0].collected:
                ret = '取消收藏'
            else:
                ret = '收藏'
            info['ret'] = ret

        return render(request, 'blog.html', info)


class LikeView(LoginRequiredMixIn, View):
    """
    点赞类视图
    自己可已给自己点赞
    """
    def post(self, request, blog_id):
        try:
            blog = Articles.objects.get(blog_id=blog_id)
        except Articles.DoesNotExist:
            return JsonResponse({'msg': 'error'})
        obj, created = blog.likecollect_set.get_or_create(username=request.user, article=blog)

        if obj.liked:
            # 如果已经点过赞，则取消赞
            obj.liked = False
            obj.save()
            # 并更新blog.love
            love = blog.love - 1
            # 不更新时间
            Articles.objects.filter(blog_id=blog_id).update(love=love)
        else:
            # 否则点赞
            obj.liked = True
            obj.save()
            # 并更新blog.love
            love = blog.love + 1
            # 不更新时间
            Articles.objects.filter(blog_id=blog_id).update(love=love)

        return JsonResponse({'msg': 'ok', 'likes': love})


class CollectView(LoginRequiredMixIn, View):
    """
    收藏类视图
    自己不可以收藏自己的
    """
    def post(self, request, blog_id):
        try:
            blog = Articles.objects.get(blog_id=blog_id)
        except Articles.DoesNotExist:
            return JsonResponse({'msg': 'error'})
        obj, created = blog.likecollect_set.get_or_create(username=request.user, article=blog)

        if obj.collected:
            obj.collected = False
            info = '收藏'
        else:
            obj.collected = True
            info = '取消收藏'
        obj.save()
        return JsonResponse({'msg': 'ok', 'ret': info})


class BlogAdd(LoginRequiredMixIn, View):
    """
    写博客类视图
    """
    def get(self, request):
        if not request.user.is_active:
            raise Http404('账户未激活，请查看激活邮件')
        # 判断url后面'？blog_id='有无内容决定是添加博客还是编辑博客
        if request.GET.get('blog_id'):
            # 有则判断博客存在否并提交给post
            try:
                blog = Articles.objects.get(blog_id=request.GET.get('blog_id'))
                form = ArticlesEditorModelForm(instance=blog)
            except Articles.DoesNotExist:
                raise Http404('找不到文章')
        else:
            form = ArticlesEditorModelForm()
        return render(request, 'blog_edit.html', {'form': form})

    def post(self, request):
        if not request.user.is_active:
            raise Http404('账户未激活，请查看激活邮件')
        form = ArticlesEditorModelForm(request.POST)
        if not form.is_valid():
            return render(request, 'blog_edit.html', {'form': form})

        title = form.cleaned_data.get('title')
        body = form.cleaned_data.get('body')
        description = form.cleaned_data.get('description')
        if not description:
            description = md2summary(body)

        if request.GET.get('blog_id'):
            # 编辑博客
            try:
                blog = request.user.articles_set.get(blog_id=request.GET.get('blog_id'))
            except Articles.DoesNotExist:
                raise Http404('没有该文章')
            blog.title = title
            blog.body = body
            blog.description = description
            if form.cleaned_data.get('is_secret') == 'on':
                blog.is_secret = True
            blog.save()
            return redirect(reverse('blog:user_blog'))

        else:
            # 添加博客
            is_secret = form.cleaned_data.get('is_secret')
            uuid = str(uuid1()).split('-')[0]
            Articles.objects.create(author_name=request.user, title=title, body=body,
                                    is_secret=is_secret, description=description, blog_id=uuid)
            return redirect(reverse('blog:user_blog'))


class BlogDelete(LoginRequiredMixIn, View):
    """删除博客"""
    def get(self, request):
        blog_id = request.GET.get('blog')
        try:
            a = request.user.articles_set.filter(pk=blog_id).delete()
            # print('sucessful', a)
        except Exception as e:
            print(e)
        return redirect(reverse('blog:user_blog'))


class CommentEdit(View):
    """
    评论提交类视图
    """
    def get(self, request):
        blog_id = request.GET.get('blog_id', 'bad guy')
        try:
            blog = Articles.objects.get(blog_id=blog_id)
        except Articles.DoesNotExist:
            raise Http404()

        comments = blog.comments_set.all().order_by('-create_time')

        try:
            page = int(request.GET.get('page', 1))
        except (ValueError, TypeError):
            page = 1

        comments_page = Paginator(comments, 10)
        rendered = render_to_string('comments.html', {'comments': comments_page.page(page)})

        return JsonResponse({'comment': rendered})

    def post(self, request):
        if not request.user.is_active:
            raise Http404('账户未激活，请查看激活邮件')

        # # TODO ajax提交评论
        blog_id = request.GET.get('blog_id', '')
        if blog_id:
            try:
                article = Articles.objects.get(blog_id=blog_id)

            except Articles.DoesNotExist:
                raise Http404()

            form = CommentsEditorModelForm(request.POST)
            content = form.data.get('content')
            if not content:
                raise Http404('提交错误')
            Comments.objects.create(commenter=request.user, article=article, content=content)
            return render(request, 'redirect.html', {'next': request.GET.get('next'), 'info': '评论成功'})
        else:
            return Http404()


class MessageView(View):
    """
    消息管理类视图
    """
    def get(self, request):
        # 消息列表
        info = {'notice': '我的消息'}
        if request.user.is_authenticated:
            message = request.user.own_message.all().order_by('-send_time')
            no_read_message = message.filter(has_read=False)
            if request.GET.get('no_read'):
                message = no_read_message

                # ## 默认点开视为已读          这里直接刷新会清空message，不知道原因(取消)
                # a = message.update(has_read=True)
                # info['messages'].filter(has_read=False).update(has_read=True)

                info['notice'] = '未读消息'

            info['messages'] = message
            info['head_ico'] = '/static/images/head_ico/head%s.jpeg' % random.randint(0, 27)
            # info['no_read_id'] = ','.join(str(i.id) for i in no_read_message)
            return render(request, 'message_list.html', info)
        else:
            return render(request, 'sign/sign-in.html', {'next': reverse('blog:message')})

    def post(self, request):
        # 发消息
        username = request.POST.get('@')
        contact_way = request.POST.get('contact', '')
        content = request.POST.get('message')
        info = {'info': '谢谢您的来信,我会尽快回复您', 'next': request.GET.get('next', reverse('blog:index'))}
        if not content:
            # 没有内容返回上一个页面
            return redirect(info['next'])

        if request.user.is_authenticated:
            # 用户登录了才可以互发消息
            if not username:
                # 没有指定发给谁默认表示联系管理员
                for_user = User.objects.get(user_id=1)
                content = contact_way + ':' + content
            else:
                try:
                    for_user = User.objects.get(username=username)
                    info['info'] = '发送成功'
                except User.DoesNotExist:
                    return Http404()
            Message.objects.create(user=for_user, from_who=request.user, content=content)

        else:
            # 没登陆默认发给管理员，可以加个邮件提醒
            content = contact_way + ':' + content
            Message.objects.create(user=User.objects.get(user_id=1), content=content)
        return render(request, 'redirect.html', info)


class MessageReply(LoginRequiredMixIn, View):
    """发送消息"""
    def get(self, request):
        username = request.GET.get('to')
        if username:
            try:
                reply_for = User.objects.get(username=username)
            except User.DoesNotExist:
                return Http404('用户不存在')
            message_all = Message.objects.filter(Q(user=request.user, from_who=reply_for) |
                                                 Q(user=reply_for, from_who=request.user)).order_by('-send_time')
            # 标记为已读
            message_all.filter(user=request.user, has_read=False).update(has_read=True)
            return render(request, 'message_reply.html', {'messages': message_all, 'username': reply_for.username})
        else:
            # 没有指定发给谁表示匿名消息或则标记已读
            ret = Message.objects.filter(has_read=False).update(has_read=True)
            return redirect(reverse('blog:message'))


class SignUp(View):
    """
    注册类视图
    """
    def get(self, request):
        # 处理get请求
        return render(request, 'sign/sign-up.html')

    def post(self, request):
        # 处理post请求
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repswd = request.POST.get('repd')
        remember = request.POST.get('remember')

        info = {}
        cookies_age = 7 * 24 * 3600
        if remember == 'on':
            info['username'] = username
            info['email'] = email
            info['password'] = password
            info['checked'] = 'checked'

        if not all([username, email, password]):
            info['notice'] = '请补全以下信息'
        elif not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', str(email)):
            # 匹配邮箱
            info['notice'] = '邮箱格式不正确'
        elif password == repswd:
            # 检验用户名是否重复
            try:
                exist_user = User.objects.get(username=username)
                # 不报错则表示能找到用户名
                info['notice'] = '用户名已存在'
            except User.DoesNotExist:
                # 用户不存在则判断邮箱是否已注册
                try:
                    exist_user = User.objects.get(email=email)
                    info['notice'] = '邮箱已被注册，请重试'
                except User.DoesNotExist:
                    exist_user = ''
            if not exist_user:
                # 生成用户uuid
                user_id = str(uuid1()).split('-')[0]
                User.objects.create_user(username=username, email=email, password=password, user_id=user_id,
                                         is_active=False)
                response = redirect(reverse('blog:index'))
                # 判断是否记住用户名,只在注册成功后加cookies
                if remember == 'on':
                    # 只能一条一条加和删
                    response.set_cookie('username', username, max_age=cookies_age)
                else:
                    response.delete_cookie('username')

                user = User.objects.get(username=username)

                # 邮件发送
                active_email(user)

                # 登录
                login(request, user)
                return response
        else:
            info['notice'] = '两次密码不一致'

        return render(request, 'sign/sign-up.html', info)


class SignIn(View):
    """登录类视图"""
    def get(self, request):
        # 判断用户是否已登陆 登录后跳转到
        if request.user.is_authenticated:
            return redirect(reverse('blog:user_info'))
        # 获取历史用户名密码 没有则置空
        username = request.COOKIES.get('username', '')
        password = request.COOKIES.get('password', '')

        return render(request, 'sign/sign-in.html', {'username': username, 'password': password})

    def post(self, request):
        # 判断用户是否已登陆 避免重复登录
        if request.user.is_authenticated:
            return redirect(reverse('blog:user_info'))

        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 跳转页面
        next_url = request.GET.get('next', reverse('blog:user_info'))

        info = {}
        cookies_age = 7 * 24 * 3600
        if not all([username, password]):
            info['notice'] = '请输入用户名和密码'
        remember = request.POST.get('remember')
        if remember == 'on':
            info['username'] = username
            info['password'] = password
            info['checked'] = 'checked'

        # 验证用户名密码
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户密码正确
            # 判断是否记住用户名
            response = redirect(next_url)
            if remember == 'on':
                response.set_cookie('username', username, max_age=cookies_age)
                response.set_cookie('password', password, max_age=cookies_age)
            else:
                response.delete_cookie('username')
                response.delete_cookie('password')
            login(request, user)
            return response
        else:
            # 密码错误
            info['notice'] = '用户名密码不正确'
            return render(request, 'sign/sign-in.html', info)


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('blog:login'))


# TODO 修改资料还未实现
class Forget(View):
    '''找回密码类视图，未实现'''
    def get(self, request):
        return render(request, 'sign/forget.html')

    def post(self, request):
        # 接收数据
        username = request.POST.get('username')
        # 其他验证身份方式  验证码 发修改邮件
        # newpass = request.POST.get('pass')
        return redirect(reverse('blog:login'))


class UserActive(View):
    def get(self, request):
        token = request.GET.get('token')
        try:
            user_id = serializer.loads(token)['id']
            user = User.objects.get(user_id=user_id)
            user.is_active = True
            user.save()
            login(request, user)
            return redirect(reverse('blog:user_info'))
        except SignatureExpired:
            if request.user.is_authenticated and not request.user.is_active:
                # 重新邮件发送
                active_email(request.user)
            return render(request, 'redirect.html', {'info': '链接已过期，请在登录状态下点击此链接即可重新发送激活邮件',
                                                     'next': reverse('blog:user_info')})
        except:
            return redirect(reverse('blog:index'))










