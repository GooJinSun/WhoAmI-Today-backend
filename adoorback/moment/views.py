import os
from datetime import date, datetime, timedelta


from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from rest_framework import generics, exceptions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from safedelete.models import SOFT_DELETE_CASCADE

from adoorback.utils.permissions import IsNotBlocked
from adoorback.utils.validators import adoor_exception_handler

import comment.serializers as cs
import moment.serializers as ms
from moment.models import Moment


class MomentToday(generics.CreateAPIView, generics.RetrieveUpdateAPIView):
    """
    Get today's moment of request user, create a new moment for today, or update today's moment.
    """
    serializer_class = ms.MyMomentSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]
    
    def get_date(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        created_date = date(year, month, day)
        
        return created_date

    def get_exception_handler(self):
        return adoor_exception_handler
    
    def create(self, request, *args, **kwargs):
        try:
            current_user = self.request.user
            current_date = self.get_date()
            existing_moments = Moment.objects.get(Q(author=current_user) & Q(date=current_date))
        except:
            existing_moments = None

        if existing_moments is not None:
            return Response("A moment for today already exists.", status=status.HTTP_400_BAD_REQUEST)
        
        if not 'mood' in request.data and not 'description' in request.data and not 'photo' in request.data:
            return Response("No fields provided for create.", status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @transaction.atomic
    def perform_create(self, serializer):
        created_date = self.get_date()
        next_day = created_date + timedelta(days=1)
        available_limit = timezone.make_aware(datetime(next_day.year, next_day.month, next_day.day, 23, 59, 59), timezone.get_current_timezone())
        serializer.save(author=self.request.user, date=created_date, available_limit=available_limit)
    
    def get_object(self):
        current_user = self.request.user
        current_date = self.get_date()
        try:
            moment = Moment.objects.get(author=current_user, date=current_date)
        except:
            moment = None
        return moment
    
    def get(self, request, *args, **kwargs):
        object = self.get_object()
        if object is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(object)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        if not instance:
           return Response("There's no moment for today to update.", status=status.HTTP_400_BAD_REQUEST) 
        
        if instance.mood and 'mood' in request.data:
            return Response("Cannot update mood - already exists.", status=status.HTTP_400_BAD_REQUEST)
        
        if instance.description and 'description' in request.data:
            return Response("Cannot update description - already exists.", status=status.HTTP_400_BAD_REQUEST)
        
        if instance.photo and 'photo' in request.data:
            return Response("Cannot update photo - already exists.", status=status.HTTP_400_BAD_REQUEST)
            
        if not 'mood' in request.data and not 'description' in request.data and not 'photo' in request.data:
            return Response("No fields provided for update.", status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class MomentWeekly(generics.ListAPIView):
    serializer_class = ms.MyMomentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_next_seven_days(self, start_date):
        next_seven_days = []
        next_seven_days.append(start_date)

        for i in range(6):
            next_day = start_date + timedelta(days=i + 1)
            next_seven_days.append(next_day)

        return next_seven_days
    
    def get_queryset(self):
        current_user = self.request.user
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        start_date = date(year, month, day)
        
        next_seven_days = self.get_next_seven_days(start_date)
        
        queryset = Moment.objects.filter(Q(author=current_user) & Q(date__in=next_seven_days)).order_by('date')
        return queryset
    

class MomentMonthly(generics.ListAPIView):
    serializer_class = ms.MyMomentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        current_user = self.request.user
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        formatted_date = f"{year}-{month:02d}"
        
        queryset = Moment.objects.filter(Q(author=current_user) & Q(date__startswith=formatted_date)).order_by('date')
        return queryset


class MomentDetail(generics.RetrieveAPIView):
    queryset = Moment.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ms.MomentDetailSerializer

    def get_exception_handler(self):
        return adoor_exception_handler


class MomentDelete(generics.DestroyAPIView):
    serializer_class = ms.MyMomentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        try:
            moment = Moment.objects.get(id=self.kwargs.get('pk'))
        except Moment.DoesNotExist:
            raise exceptions.NotFound("Moment not found")
        
        if moment.author != self.request.user:
            raise exceptions.PermissionDenied("You do not have permission to delete this moment")
        return moment
    
    @transaction.atomic
    def perform_destroy(self, instance):
        instance.delete(force_policy=SOFT_DELETE_CASCADE)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        field_name = self.kwargs.get('field')

        if field_name == 'mood':
            instance.mood = None
        elif field_name == 'photo':
            if instance.photo:
                file_path = os.path.join(settings.MEDIA_ROOT, instance.photo.name)
                if os.path.exists(file_path):
                    os.remove(file_path)
            instance.photo = None
        elif field_name == 'description':
            instance.description = None
        else:
            return Response("Wrong field name to delete.", status=status.HTTP_400_BAD_REQUEST)

        instance.save()
        
        if not instance.mood and not instance.photo and not instance.description:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(self.get_serializer(instance).data)
    

class MomentComments(generics.ListAPIView):
    serializer_class = cs.PostCommentsSerializer
    permission_classes = [IsAuthenticated, IsNotBlocked]

    def get_exception_handler(self):
        return adoor_exception_handler

    def get_queryset(self):
        return Moment.objects.filter(id=self.kwargs.get('pk'))
    

class MomentRead(generics.UpdateAPIView):
    queryset = Moment.objects.all()
    serializer_class = ms.MomentBaseSerializer
    permission_classes = [IsAuthenticated]

    def get_exception_handler(self):
        return adoor_exception_handler

    def patch(self, request, *args, **kwargs):
        current_user = self.request.user
        ids = request.data.get('ids', [])
        queryset = Moment.objects.filter(id__in=ids)
        for response in queryset:
            response.readers.add(current_user)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)
    