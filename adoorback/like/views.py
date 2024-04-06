from django.db import transaction, IntegrityError
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from account.serializers import UserMinimalSerializer
from like.models import Like
from like.serializers import LikeSerializer

from adoorback.utils.permissions import IsOwnerOrReadOnly
from adoorback.utils.content_types import get_generic_relation_type
from adoorback.utils.validators import adoor_exception_handler


class LikeCreate(generics.CreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_exception_handler(self):
        return adoor_exception_handler

    @transaction.atomic
    def perform_create(self, serializer):
        content_type_id = get_generic_relation_type(self.request.data['target_type']).id
        try:
            serializer.save(user=self.request.user,
                            content_type_id=content_type_id,
                            object_id=self.request.data['target_id'])
        except IntegrityError:
            pass


class LikeDestroy(generics.DestroyAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_exception_handler(self):
        return adoor_exception_handler
