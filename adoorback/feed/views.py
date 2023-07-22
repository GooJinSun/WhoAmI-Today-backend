import os
import pandas as pd
from datetime import date, datetime, timedelta
import json

from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.core.cache import cache
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.response import Response as DjangoResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from adoorback.utils.permissions import IsAuthorOrReadOnly, IsShared, IsNotBlocked
from adoorback.utils.validators import adoor_exception_handler
import comment.serializers as cs
import feed.serializers as fs
from feed.algorithms.data_crawler import select_daily_questions
from feed.models import Article, Response, Question, Post, ResponseRequest

User = get_user_model()


class FriendFeedPostList(generics.ListAPIView):
    """
    List friend feed posts
    """
    serializer_class = fs.PostFriendSerializer
    permission_classes = [IsAuthenticated]

    def get_exception_handler(self):
        return adoor_exception_handler

    def get_queryset(self):
        current_user = self.request.user
        # queryset = cache.get('friend-{}'.format(current_user.id))
        # if queryset:
        #     return queryset
        # else:
        queryset = Post.objects.friend_posts_only().filter(Q(author_id__in=current_user.friend_ids) | Q(author_id=current_user.id)).exclude(Q(author_id__in=current_user.user_report_blocked_ids) | Q(id__in=current_user.content_report_blocked_ids))
            # cache.set('friend-{}'.format(current_user.id), queryset)
        return queryset


class AnonymousFeedPostList(generics.ListAPIView):
    """
    List anonymous feed posts
    """
    serializer_class = fs.PostAnonymousSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        current_user = self.request.user
        # queryset = cache.get('anonymous')
        # if not queryset:
        queryset = Post.objects.anonymous_posts_only().exclude(Q(author_id__in=current_user.user_report_blocked_ids) | Q(id__in=current_user.content_report_blocked_ids))
            # cache.set('anonymous', queryset)
        return queryset

    def get_exception_handler(self):
        return adoor_exception_handler


class UserFeedPostList(generics.ListAPIView):
    """
    List feed posts for user page
    """
    serializer_class = fs.PostFriendSerializer
    permission_classes = [IsAuthenticated]

    def get_exception_handler(self):
        return adoor_exception_handler

    def get_queryset(self):
        selected_user_id = self.kwargs.get('pk')
        current_user = self.request.user
        if selected_user_id in current_user.user_report_blocked_ids:
            raise PermissionDenied("current user blocked this user")
        elif selected_user_id in current_user.friend_ids:
            return Post.objects.friend_posts_only().filter(author_id=self.kwargs.get('pk'))
        elif selected_user_id == current_user.id:
            return Post.objects.filter(author_id=current_user.id)
        raise PermissionDenied("you're not his/her friend...")


class ArticleList(generics.CreateAPIView):
    """
    List all articles, or create a new article.
    """
    queryset = Article.objects.all()
    serializer_class = fs.ArticleFriendSerializer
    permission_classes = [IsAuthenticated]

    def get_exception_handler(self):
        return adoor_exception_handler

    @transaction.atomic
    def perform_create(self, serializer):
        # cache.delete('friend-{}'.format(self.request.user.id))
        # cache.delete('anonymous')
        serializer.save(author=self.request.user)


class ArticleDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or destroy an article.
    """
    queryset = Article.objects.all()
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly, IsShared, IsNotBlocked]

    def get_exception_handler(self):
        return adoor_exception_handler

    def get_serializer_class(self):
        article = Article.objects.get(id=self.kwargs.get('pk'))
        if User.are_friends(self.request.user, article.author) and article.share_with_friends:
            return fs.ArticleFriendSerializer
        return fs.ArticleAnonymousSerializer


class ResponseList(generics.ListCreateAPIView):
    """
    List all responses, or create a new response.
    """
    queryset = Response.objects.all()
    serializer_class = fs.ResponseFriendSerializer
    permission_classes = [IsAuthenticated, IsNotBlocked]

    def get_exception_handler(self):
        return adoor_exception_handler

    @transaction.atomic
    def perform_create(self, serializer):
        # cache.delete('questions')
        # cache.delete('friend-{}'.format(self.request.user.id))
        # cache.delete('anonymous')
        serializer.save(author=self.request.user)
        
class ResponseDaily(generics.ListCreateAPIView):
    serializer_class = fs.ResponseBaseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_date(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        created_date = date(year, month, day)

        return created_date
    
    @transaction.atomic
    def perform_create(self, serializer):
        created_date = self.get_date()
        next_day = created_date + timedelta(days=1)
        available_limit = timezone.make_aware(datetime(next_day.year, next_day.month, next_day.day, 23, 59, 59),
                                              timezone.get_current_timezone())
        serializer.save(author=self.request.user, date=self.get_date(), available_limit=available_limit)
        
    def get_queryset(self):
        current_user = self.request.user
        current_date = self.get_date()
        return Response.objects.filter(author=current_user, date=current_date).order_by('question')
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        combined_responses = []
        last_question_id = 0

        for response in serializer.data:
            question = response["question"]
            copied_response = response.copy()
            del copied_response["question"]

            if question["id"] != last_question_id:
                copied_question = question.copy()
                copied_question["responses"] = [copied_response]
                combined_responses.append(copied_question)
                last_question_id = question["id"]
            else:
                combined_responses[-1]["responses"].append(copied_response)

        return DjangoResponse(combined_responses)
    
    def get_exception_handler(self):
        return adoor_exception_handler


class QuestionResponseList(generics.ListAPIView):
    """
    List responses for a question
    """
    serializer_class = fs.ResponseBaseSerializer
    permission_classes = [IsAuthenticated]

    def get_exception_handler(self):
        return adoor_exception_handler

    def get_queryset(self):
        current_user = self.request.user
        return Response.objects.filter(question__id=self.kwargs.get('pk'), author=current_user).order_by('-created_at')


class ResponseDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or destroy a response.
    """
    queryset = Response.objects.all()
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly, IsShared, IsNotBlocked]

    def get_exception_handler(self):
        return adoor_exception_handler

    def get_serializer_class(self):
        response = Response.objects.get(id=self.kwargs.get('pk'))
        if User.are_friends(self.request.user, response.author) and response.share_with_friends:
            return fs.ResponseFriendSerializer
        return fs.ResponseAnonymousSerializer
    

class ResponseComments(generics.ListAPIView):
    serializer_class = cs.PostCommentsSerializer
    permission_classes = [IsAuthenticated, IsNotBlocked]

    def get_exception_handler(self):
        return adoor_exception_handler

    def get_queryset(self):
        return Response.objects.filter(id=self.kwargs.get('pk'))


class QuestionList(generics.ListCreateAPIView):
    """
    List all questions, or create a new question.
    """
    
    serializer_class = fs.QuestionResponsiveSerializer
    permission_classes = [IsAuthenticated]

    def get_exception_handler(self):
        return adoor_exception_handler

    def get_queryset(self):
        queryset = Question.objects.raw("""
                SELECT * FROM feed_question
                WHERE array_length(selected_dates, 1) IS NOT NULL
                ORDER BY selected_dates[array_upper(selected_dates, 1)] DESC
                LIMIT 30;
            """)
        return queryset
    
    @transaction.atomic
    def perform_create(self, serializer):
        # cache.delete('friend-{}'.format(self.request.user.id))
        # cache.delete('anonymous')
        # cache.delete('questions')
        serializer.save(author=self.request.user)


class QuestionDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or destroy a question.
    """
    queryset = Question.objects.all()
    serializer_class = fs.QuestionResponsiveSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly, IsShared, IsNotBlocked]

    def get_exception_handler(self):
        return adoor_exception_handler


class QuestionFriendResponsesDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or destroy a question.
    """
    serializer_class = fs.QuestionDetailFriendResponsesSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly, IsShared, IsNotBlocked]

    def get_queryset(self):
        # queryset = cache.get('questions')
        # if not queryset:
        queryset = Question.objects.all()
        cache.set('questions', queryset)
        return queryset

    def get_exception_handler(self):
        return adoor_exception_handler


class QuestionAnonymousResponsesDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or destroy a question.
    """
    serializer_class = fs.QuestionDetailAnonymousResponsesSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly, IsShared, IsNotBlocked]

    def get_queryset(self):
        # queryset = cache.get('questions')
        # if not queryset:
        queryset = Question.objects.all()
        cache.set('questions', queryset)
        return queryset

    def get_exception_handler(self):
        return adoor_exception_handler


class ResponseRequestList(generics.ListAPIView):
    """
    Get response requests sent to other users on the selected question.
    (for frontend 'send' button implementation purposes)
    """
    serializer_class = fs.ResponseRequestSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_exception_handler(self):
        return adoor_exception_handler

    @transaction.atomic
    def get_queryset(self):
        try:
            question = Question.objects.get(id=self.kwargs['qid'])
        except Question.DoesNotExist:
            return HttpResponseBadRequest
        sent_response_request_set = self.request.user.sent_response_request_set.all()
        response_requests = sent_response_request_set.filter(question=question).order_by('-id')
        return response_requests


class ResponseRequestCreate(generics.CreateAPIView):
    """
    Get response requests of the selected question.
    """
    queryset = ResponseRequest.objects.all()
    serializer_class = fs.ResponseRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_exception_handler(self):
        return adoor_exception_handler

    @transaction.atomic
    def perform_create(self, serializer):
        current_user = self.request.user
        requester = User.objects.get(id=self.request.data.get('requester_id'))
        requestee = User.objects.get(id=self.request.data.get('requestee_id'))
        if requester != current_user:
            raise PermissionDenied("requester가 본인이 아닙니다...")
        if not User.are_friends(requestee, current_user):
            raise PermissionDenied("친구에게만 response request를 보낼 수 있습니다...")
        try:
            serializer.save()
        except IntegrityError as e:
            if 'unique constraint' in e.args[0]:
                return
            else:
                raise e


class ResponseRequestDestroy(generics.DestroyAPIView):
    serializer_class = fs.ResponseRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_exception_handler(self):
        return adoor_exception_handler

    def get_object(self):
        # since the requester is the authenticated user, no further permission checking unnecessary
        return ResponseRequest.objects.get(requester_id=self.request.user.id,
                                           requestee_id=self.kwargs.get('rid'),
                                           question_id=self.kwargs.get('qid'))


class DailyQuestionList(generics.ListAPIView):
    serializer_class = fs.DailyQuestionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_exception_handler(self):
        return adoor_exception_handler

    def get_queryset(self):
        return Question.objects.daily_questions()


class DateQuestionList(generics.ListAPIView):
    serializer_class = fs.DailyQuestionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_exception_handler(self):
        return adoor_exception_handler

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        return Question.objects.date_questions(date=date(year=year, month=month, day=day))


class RecommendedQuestionList(generics.ListAPIView):
    serializer_class = fs.QuestionBaseSerializer
    permission_classes = [IsAuthenticated]

    def get_exception_handler(self):
        return adoor_exception_handler

    @transaction.atomic
    def get_queryset(self):
        try:
            dir_name = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(dir_name, 'algorithms', 'recommendations.csv')
            df = pd.read_csv(path)
        except FileNotFoundError:
            return Question.objects.daily_questions().order_by('?')[:5]

        df = df[df.userId == self.request.user.id]
        rank_ids = df['questionId'].tolist()
        daily_question_ids = set(list(Question.objects.daily_questions().values_list('id', flat=True)))
        recommended_ids = [x for x in rank_ids if x in daily_question_ids][:5]
        recommended_ids = recommended_ids if len(recommended_ids) == 5 else \
            Question.objects.daily_questions().values_list('id', flat=True)[:5]

        return Question.objects.filter(pk__in=recommended_ids).order_by('?')
