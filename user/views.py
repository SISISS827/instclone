import os
from uuid import uuid4
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
#패스워드 암호화하는 기능 추가
from django.contrib.auth.hashers import make_password
from palmTreeSns.settings import MEDIA_ROOT
from django.http.response import JsonResponse
from django.contrib import auth


class Join(APIView):
    def get(self, request):
        return render(request, "user/join.html")

    def post(self, request):
        #회원가입
        #데이터 불러오기
        email = request.data.get('email', None)
        nickname = request.data.get('nickname', None)
        name = request.data.get('name', None)
        password = request.data.get('password', None)
        #패스워드는 암호화를 해줘야함(암호화 = 단방향 : 암호화된 비밀번호 복구 x, 양방향 : 암호화된 비밀번호 복구 o)
        #패스워드가 자동으로 암호화되어서 들어간다.
        
        User.objects.create(email=email,
                            nickname=nickname,
                            name=name,
                            password=make_password(password),
                            profile_image="default_profile.png")
        #성공
        return Response(status=200)


class Login(APIView):
    def get(self, request):
        return render(request, "user/login.html")

    def post(self, request):
        #로그인 (이메일과 패스워드로 사용자의 정보를 찾는다)
        email = request.data.get('email', None)
        password = request.data.get('password', None)
        #값을 하나만 리턴
        user = User.objects.filter(email=email).first()
        #유저가 없으면 찾을 수 없음 코드 + 메시지, 보안을 위해 오류는 동일 멘트
        if user is None:
            return Response(status=400, data=dict(message="회원정보가 잘못되었습니다."))
        #비밀번호 검사 후 동일하면
        if user.check_password(password):
            #로그인을 했다. 세션 or 쿠키
            #세션에 나의 email정보를 저장해놓는다. user.objects.filter(email)을 통해 정보를 다시 가져올 수 있음
            request.session['email'] = email
            return Response(status=200)
        else:
            return Response(status=400, data=dict(message="회원정보가 잘못되었습니다."))


class LogOut(APIView):
    def get(self, request):
        #로그아웃 때 세션 기록을 지워줘야함 flush사용
        auth.logout(request)
        return redirect("/user/login")


class UploadProfile(APIView):
    def post(self, request):

        #파일 불러오는 코드
        file = request.FILES['file']
        email = request.data.get('email')

        uuid_name = uuid4().hex
        save_path = os.path.join(MEDIA_ROOT, uuid_name)

        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        profile_image = uuid_name

        user = User.objects.filter(email=email).first()

        user.profile_image = profile_image
        user.save()

        #http 성공 응답코드 200
        return Response(status=200)

class Follow(APIView):
    def post(self, request):
        email = request.data.get('email', None)
        target_user = User.objects.get(email=email)
        user = User.objects.filter(email=email).first()
        user.follow.add(target_user)
        user.save()
        return JsonResponse({'status':"follow"})

class ViewFollow(APIView):
    def get(self, request):
        email = request.data.get('email', None)
        user = User.objects.get(email=email)
        following = list(user.follow.all().values('email'))
        return JsonResponse({'following':following})
