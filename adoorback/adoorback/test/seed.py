from datetime import datetime
import logging
import random
import sys

from django.contrib.auth import get_user_model
from faker import Faker

from account.models import FriendRequest
from adoorback.utils.content_types import get_comment_type, get_response_type
from chat.models import ChatRoom, Message
from check_in.models import CheckIn
from comment.models import Comment
from like.models import Like
from note.models import Note
from qna.algorithms.data_crawler import select_daily_questions
from qna.models import Response, Question, ResponseRequest

DEBUG = False


def set_seed(n):
    if DEBUG:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    User = get_user_model()
    faker = Faker()

    try:
        User.objects.create_superuser(
            username='adoor', email='adoor.team@gmail.com', password='adoor2020:)',
            question_history=",".join(map(str, faker.random_elements(
                elements=range(1, 1501),
                length=random.randint(3, 10),
                unique=True))))
    except:
        pass

    # Seed User
    for _ in range(10):
        username = "adoor_" + str(_ + 1)
        if User.objects.filter(username=username).count() == 0:
            User.objects.create_user(username=username,
                                     email=faker.email(),
                                     password="Adoor2020:)")
    if not User.objects.filter(username="tester2"):
        User.objects.create_user(username="tester2", email=faker.email(), password="Test1234!")
    logging.info(
        f"{User.objects.count()} User(s) created!") if DEBUG else None

    # Seed Superuser
    admin = User.objects.filter(is_superuser=True).first()
    user = User.objects.get(username="adoor_2")
    logging.info("Superuser created!") if DEBUG else None

    # Seed Article/AdminQuestion/CustomQuestionPost
    users = User.objects.all()
    for _ in range(n):
        user = random.choice(users)
        Question.objects.create(
            author=admin, is_admin_question=True, content=faker.word())
    logging.info(f"{Question.objects.count()} Question(s) created!") \
        if DEBUG else None

    # Select Daily Questions
    select_daily_questions()

    # Seed Response
    questions = Question.objects.all()
    for _ in range(n):
        user = random.choice(users)
        question = random.choice(questions)
        response = Response.objects.create(author=user,
                                           content=faker.text(max_nb_chars=50),
                                           question=question)
    logging.info(
        f"{Response.objects.count()} Response(s) created!") if DEBUG else None

    # Seed Check-in
    for _ in range(n):
        user = random.choice(users)
        checkin = CheckIn.objects.create(user=user,
                                         availability=faker.text(max_nb_chars=10),
                                         mood=faker.text(max_nb_chars=5),
                                         description=faker.text(max_nb_chars=20),
                                         track_id=faker.text(max_nb_chars=10))
    logging.info(
        f"{CheckIn.objects.count()} Check-in(s) created!") if DEBUG else None

    # Seed Note
    for _ in range(n):
        user = random.choice(users)
        note = Note.objects.create(author=user,
                                   content=faker.text(max_nb_chars=50))
    logging.info(
        f"{Note.objects.count()} Note(s) created!") if DEBUG else None

    # Seed Friend Request
    user_1 = User.objects.get(username="adoor_1")
    user_2 = User.objects.get(username="adoor_2")
    user_3 = User.objects.get(username="adoor_3")
    user_4 = User.objects.get(username="adoor_4")
    user_5 = User.objects.get(username="adoor_5")
    user_6 = User.objects.get(username="adoor_6")
    user_7 = User.objects.get(username="adoor_7")
    user_8 = User.objects.get(username="adoor_8")
    user_9 = User.objects.get(username="adoor_9")
    user_10 = User.objects.get(username="adoor_10")

    FriendRequest.objects.all().delete()
    FriendRequest.objects.get_or_create(requester=user_8, requestee=user_9)
    FriendRequest.objects.get_or_create(requester=user_8, requestee=user_10)

    # Seed Friendship
    user_2.friends.add(user_1, user_3, user_4, user_5, user_6)

    # Test Notifications
    response = Response.objects.first()
    note = Note.objects.first()

    Like.objects.all().delete()
    Like.objects.create(user=user_1, target=response)
    Like.objects.create(user=user_3, target=response)
    Like.objects.create(user=user_4, target=response)
    Like.objects.create(user=user_5, target=response)
    Like.objects.create(user=user_6, target=response)
    Like.objects.create(user=user_7, target=response)
    Like.objects.create(user=user_1, target=note)
    Like.objects.create(user=user_3, target=note)
    Like.objects.create(user=user_4, target=note)
    Like.objects.create(user=user_5, target=note)
    Like.objects.create(user=user_6, target=note)
    Like.objects.create(user=user_7, target=note)
    Like.objects.all().delete()
    Comment.objects.all().delete()
    Comment.objects.create(author=user_1, target=response, content="test comment noti")
    Comment.objects.create(author=user_3, target=response, content="test comment noti")
    Comment.objects.create(author=user_4, target=response, content="test comment noti")
    Comment.objects.create(author=user_5, target=response, content="test comment noti")
    Comment.objects.create(author=user_6, target=response, content="test comment noti")
    Comment.objects.create(author=user_7, target=response, content="test comment noti")
    Comment.objects.create(author=user_1, target=note, content="test note noti")
    Comment.objects.create(author=user_3, target=note, content="test note noti")
    Comment.objects.create(author=user_4, target=note, content="test note noti")
    Comment.objects.create(author=user_5, target=note, content="test note noti")
    Comment.objects.create(author=user_6, target=note, content="test note noti")
    Comment.objects.create(author=user_7, target=note, content="test note noti")
    Comment.objects.all().delete()
    ResponseRequest.objects.all().delete()
    ResponseRequest.objects.create(requester=user_1, requestee=user_3, question=response.question, message="test")
    ResponseRequest.objects.create(requester=user_4, requestee=user_3, question=response.question, message="test")
    ResponseRequest.objects.create(requester=user_5, requestee=user_3, question=response.question, message="test")
    ResponseRequest.objects.create(requester=user_6, requestee=user_3, question=response.question, message="test")
    ResponseRequest.objects.create(requester=user_7, requestee=user_3, question=response.question, message="test")
    ResponseRequest.objects.all().delete()

    # Seed Response Request
    for _ in range(n):
        question = random.choice(questions)
        requester = random.choice(users)
        requestee = random.choice(users.exclude(id=requester.id))
        ResponseRequest.objects.create(requester=requester, requestee=requestee, question=question,
                                       message=faker.catch_phrase())
    logging.info(
        f"{ResponseRequest.objects.count()} ResponseRequest(s) created!") if DEBUG else None

    # Seed Comment (target=Feed)
    responses = Response.objects.all(author=user_2)
    for _ in range(n):
        user = random.choice(users)
        response = random.choice(responses)
        Comment.objects.create(author=user, target=response,
                               content=faker.catch_phrase(), is_private=_ % 2)
    logging.info(
        f"{Comment.objects.count()} Comment(s) created!") if DEBUG else None

    # Seed Reply Comment (target=Comment)
    comment_model = get_comment_type()
    comments = Comment.objects.filter(author=user_2)
    for _ in range(n):
        user = random.choice(users)
        comment = random.choice(comments)
        reply = Comment.objects.create(author=user, target=comment,
                                       content=faker.catch_phrase(), is_private=comment.is_private)
        if reply.target.is_private:
            reply.is_private = True
            reply.save()
    logging.info(f"{Comment.objects.filter(content_type=comment_model).count()} Repl(ies) created!") \
        if DEBUG else None

    # Test Notification
    comment = Comment.objects.filter(content_type=comment_model).last()
    reply = Comment.objects.filter(content_type=get_response_type()).last()
    Like.objects.all().delete()
    Like.objects.create(user=user_1, target=comment)
    Like.objects.create(user=user_3, target=comment)
    Like.objects.create(user=user_4, target=comment)
    Like.objects.create(user=user_5, target=comment)
    Like.objects.create(user=user_6, target=comment)
    Like.objects.create(user=user_7, target=comment)
    Like.objects.create(user=user_1, target=reply)
    Like.objects.create(user=user_3, target=reply)
    Like.objects.create(user=user_4, target=reply)
    Like.objects.create(user=user_5, target=reply)
    Like.objects.create(user=user_6, target=reply)
    Like.objects.create(user=user_7, target=reply)
    Like.objects.all().delete()

    # Seed Like
    for i in range(n):
        user = random.choice(users)
        question = Question.objects.all()[i:i + 1].first()
        response = Response.objects.all()[i:i + 1].first()
        comment = Comment.objects.comments_only()[i]
        reply = Comment.objects.replies_only()[i]
        Like.objects.create(user=user, target=question)
        Like.objects.create(user=user, target=response)
        Like.objects.create(user=user, target=comment)
        Like.objects.create(user=user, target=reply)
    logging.info(
        f"{Like.objects.count()} Like(s) created!") if DEBUG else None

    # Seed Chat Messages
    for chat_room in ChatRoom.objects.all():
        participants = chat_room.users.all()
        for p in participants:
            timestamp = datetime.utcnow()
            for _ in range(random.randint(3, 5)):
                Message.objects.create(sender=p, content=faker.text(max_nb_chars=50), timestamp=timestamp, chat_room=chat_room)
