from uuid import uuid4
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Feed, Reply, Like, Bookmark
from user.models import User
import os
from palmTreeSns.settings import MEDIA_ROOT

#메인페이지로 이동하는 Class
class Main(APIView):
    def get(self, request):
        #지금 로그인한 사용자의 정보
        email = request.session.get('email', None)

        if email is None:
            return render(request, "user/login.html")

        user = User.objects.filter(email=email).first() #현재 접속자

        if user is None:
            return render(request, "user/login.html")

        #Comment에 있는 모든 데이터를 가져오겠다.
        #order_by('-id') id역순으로 가져옴 : 새 피드가 위로 올라오게
        feed_object_list = Feed.objects.all().order_by('-id')  # select  * from content_feed;
        feed_list = []

        # 이메일 아이디값에 저장된 값들을 통해서 나머지 값들을 불러온다
        for feed in feed_object_list: #테이블에 있는 피드 검사
            user_feed = User.objects.filter(email=feed.email).first() #각 피드를 작성한 사람
            reply_object_list = Reply.objects.filter(feed_id=feed.id)
            reply_list = []
            for reply in reply_object_list:
                # 이메일로 값 찾아서 가져오기
                user_reply = User.objects.filter(email=reply.email).first() #각 답글을 작성한 사람
                reply_list.append(dict(reply_content=reply.reply_content,
                                       nickname=user_reply.nickname))
            #한개의 아이디에 is_like가 True인 것들의 개수를 센다                           
            like_count=Like.objects.filter(feed_id=feed.id, is_like=True).count()
            #내가 이 게시글을 좋아요를 눌렀는지 안눌렀는지를 조회(exists 좋아요를 눌렀으면 True 안누르면 False로 반환)
            #하트 불 들어오는지 안들어오는지 + like개수 카운트 기능
            is_liked=Like.objects.filter(feed_id=feed.id, email=email, is_like=True).exists()
            is_marked=Bookmark.objects.filter(feed_id=feed.id, email=email, is_marked=True).exists()
            feed_list.append(dict(id=feed.id,
                                  image=feed.image,
                                  content=feed.content,
                                  like_count=like_count,
                                  profile_image=user_feed.profile_image,
                                  nickname=user_feed.nickname,
                                  reply_list=reply_list,
                                  is_liked=is_liked,
                                  is_marked=is_marked
                                  ))
        #context:전송할 데이터 지정 앞에 coment_list는 key값. 변경되어도 상관없음, 뒤에는 objects.all로 가져온 데이터
        return render(request, "palmTreeSns/main.html", context=dict(feeds=feed_list, user=user))


class UploadFeed(APIView):
    def post(self, request):

        #파일 불러오는 코드
        file = request.FILES['file']

        #랜덤으로 고유한 id값을 주기 위해서 uuid4사용(특수문자, 한글 섞여들어가면 오류가 날 수 있기 때문에)
        uuid_name = uuid4().hex 
        #/media/uuid랜덤이름 으로 저장되게 만든다
        save_path = os.path.join(MEDIA_ROOT, uuid_name)

         #실제로 저장하는 부분save_path에. 저장된 chunks에서 chuck를 하나하나 가져와서 사용한다.
        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        asdf = uuid_name
        content123 = request.data.get('content')
        email = request.session.get('email', None)

        Feed.objects.create(image=asdf, content=content123, email=email)
        #http 성공 응답코드 200
        return Response(status=200)

#프로필을 불러올 수 있게 email값에 맞는 유저 정보 가져오기
class Profile(APIView):
    def get(self, request):
        email = request.session.get('email', None)

        if email is None:
            return render(request, "user/login.html")

        user = User.objects.filter(email=email).first()

        if user is None:
            return render(request, "user/login.html")

        # 내가 쓴 글 불러오기
        feed_list = Feed.objects.filter(email=email)
        # 내가 좋아요 누른 사람들
        like_list = list(Like.objects.filter(email=email, is_like=True).values_list('feed_id', flat=True))
        # 내가 좋아요 누른 피드 리스트(id__in은 like_list에 있는 애들만 들어오게 됨)
        like_feed_list = Feed.objects.filter(id__in=like_list)
        # 내가 북마크 누른것들(flat을 넣어야지 리스트로나옴)
        bookmark_list = list(Bookmark.objects.filter(email=email, is_marked=True).values_list('feed_id', flat=True))
        # 북마크 누른 피드들
        bookmark_feed_list = Feed.objects.filter(id__in=bookmark_list)
        return render(request, 'content/profile.html', context=dict(feed_list=feed_list,
                                                                    like_feed_list=like_feed_list,
                                                                    bookmark_feed_list=bookmark_feed_list,
                                                                    user=user))


class UploadReply(APIView):
    def post(self, request):
        feed_id = request.data.get('feed_id', None)
        reply_content = request.data.get('reply_content', None)
        email = request.session.get('email', None)

        Reply.objects.create(feed_id=feed_id, reply_content=reply_content, email=email)

        return Response(status=200)


class ToggleLike(APIView):
    def post(self, request):
        feed_id = request.data.get('feed_id', None)
        favorite_text = request.data.get('favorite_text', True)
        # 좋아요를 새로 누른거
        if favorite_text == 'favorite_border':
            is_like = True
        else:
            is_like = False
        email = request.session.get('email', None)

        # 이미 좋아요 눌렀었는지 확인
        like = Like.objects.filter(feed_id=feed_id, email=email).first()

        if like:
            like.is_like = is_like
            like.save()
        else:
            Like.objects.create(feed_id=feed_id, is_like=is_like, email=email)

        return Response(status=200)


class ToggleBookmark(APIView):
    def post(self, request):
        feed_id = request.data.get('feed_id', None)
        bookmark_text = request.data.get('bookmark_text', True)
        print(bookmark_text)
        if bookmark_text == 'bookmark_border':
            is_marked = True
        else:
            is_marked = False
        email = request.session.get('email', None)

        bookmark = Bookmark.objects.filter(feed_id=feed_id, email=email).first()

        if bookmark:
            bookmark.is_marked = is_marked
            bookmark.save()
        else:
            Bookmark.objects.create(feed_id=feed_id, is_marked=is_marked, email=email)

        return Response(status=200)