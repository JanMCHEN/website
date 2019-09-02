## 关于本站
### 名字
dreaming，本意是想写个人网站，本人名字和这个英文谐音，同时也代表梦想和远方，哈哈哈
### 域名
chdreaming.top,暂时只能选这个域名，抢不到dreaming呀，也是好贵，然后未备案，所以绑定的是国外的服务器
### 服务器
阿里轻量作为主要服务器，国外sky服务器作为域名绑定，同时利用nginx调度两台服务器，所以有时候访问会很卡，刷新一下就好了,或者直接访问ip [139.224.13.150](http://139.224.13.150 "139.224.13.150")
### 设计
目前支持用户邮箱注册、邮箱激活、登录、写文章、评论、点赞、收藏、互发消息、ip代理池……
#### 注册 激活 登录
采用django默认的用户认证系统，用户只有在登录并且激活状态下才能发表博客、点赞、评论、收藏，激活时采用celery配合redis中间人异步发送带有个人注册信息的激活邮箱，在有效期内点击即可激活
#### 写博客
界面用的是markdown编辑器，摘要可以根据正文自动生成也可以自己提供，目前自动生成摘要根据正文小标题生成，博客作者可以设置仅自己可见、编辑、删除操作
#### 评论
评论前端显示采用ajax异步请求，在主页面加载出来后主动把第一页评论加载出来，后续可以点击查看更多继续获取评论
#### 主页
主页大图为一些我个人置顶博客，并且采用类似加载评论的方式获取所有公开博客，滚动到底部自动加载下一页
#### ip代理池
来源于网络免费代理，只是做一个简单的维护，定时检测代理可用性，采用redis sort set结构将代理分数进行维护，并将所有代理存入MySQL数据库，获取代理ip时可以根据获取数量选择读取redis还是MySQL。由于长时间没有更新爬取规则，故可能效果不好，
有时间继续维护……
#### 此处省略一万字。。。
### 还有很多问题，后续会慢慢修复并丰富功能


## 后端
### 本站采用开源python web框架django设计
[django官网](https://www.djangoproject.com/ "django官网")，[官方中文文档](https://docs.djangoproject.com/zh-hans/2.2/ "官方中文文档")
### 数据库
MySQL存储数据，redis缓存
## 前端
[bootstrap](https://v4.bootcss.com/ "bootstrap")作为主要框架，编辑器采用[markdown](https://github.com/pandao/editor.md "md")，同时参考[django-mditor](https://github.com/pylixm/django-mdeditor "django-mditor")
## 网站部分源码
[GitHub](https://github.com/JanMCHEN/website "GitHub")
## 后续……
