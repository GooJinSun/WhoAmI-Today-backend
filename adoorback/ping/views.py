from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import generics, exceptions
from rest_framework.permissions import IsAuthenticated

from .models import Ping, get_or_create_ping_room
from .serializers import PingSerializer

User = get_user_model()


class PingList(generics.ListCreateAPIView):
    serializer_class = PingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            connected_user = User.objects.get(id=self.kwargs.get('pk'))
            if not user.is_connected(connected_user):
                raise exceptions.PermissionDenied("You are not connected to this user")
        except User.DoesNotExist:
            raise exceptions.NotFound("Connected user not found")

        ping_room = get_or_create_ping_room(connected_user, user)

        pings = list(ping_room.pings)  # to freeze the unread status

        oldest_unread = ping_room.pings.filter(receiver=user, is_read=False).order_by('id').first()
        
        if oldest_unread:
            oldest_position = Ping.objects.filter(ping_room=ping_room, id__gte=oldest_unread.id).count()
            pagination_size = getattr(settings, 'REST_FRAMEWORK', {}).get('PAGE_SIZE', 10)
            page_number = (oldest_position - 1) // pagination_size + 1
        else:
            page_number = 1
        self.oldest_unread_page = page_number

        # mark all pings as read
        unread_pings = ping_room.pings.filter(receiver=user, is_read=False)
        unread_pings.update(is_read=True)

        return pings
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data['oldest_unread_page'] = self.oldest_unread_page
        return response

    def perform_create(self, serializer):
        user = self.request.user
        try:
            connected_user = User.objects.get(id=self.kwargs.get('pk'))

            if not user.is_connected(connected_user):
                raise exceptions.PermissionDenied("You are not connected to this user")
        except User.DoesNotExist:
            raise exceptions.NotFound("Connected user not found")

        ping_room = get_or_create_ping_room(user, connected_user)

        serializer.save(sender=user, receiver=connected_user, ping_room=ping_room)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        user = request.user
        try:
            connected_user = User.objects.get(id=self.kwargs.get('pk'))
            ping_room = get_or_create_ping_room(user, connected_user)

            unread_count = ping_room.pings.filter(receiver=user, is_read=False).count()
        except User.DoesNotExist:
            raise exceptions.NotFound("Connected user not found")

        response.data['unread_count'] = unread_count
        return response

# class MarkPingAsRead(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, pk):
#         user = request.user
#         ping = get_object_or_404(Ping, id=pk, receiver=user)

#         if ping.is_read:
#             return Response({"detail": "Ping is already marked as read."}, status=status.HTTP_400_BAD_REQUEST)
        
#         ping.is_read = True
#         ping.save()
#         return Response({"detail": "Ping marked as read."}, status=status.HTTP_200_OK)
