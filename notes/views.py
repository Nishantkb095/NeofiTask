from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Note, NoteHistory
from .serializers import UserSerializer, NoteSerializer, NoteHistorySerializer
from rest_framework.authtoken.models import Token
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserCreate(generics.CreateAPIView):
    """
    POST auth/signup/
    """

    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="Create a new user.",
        request_body=UserSerializer,
        responses={
            201: "User registered successfully",
            400: "User registration failed",
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    "status": "success",
                    "message": "User registered successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "status": "error",
                    "message": "User registration failed",
                    "data": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginView(APIView):
    """
    POST auth/login/
    """

    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="Authenticate a user and return a token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Username of the user."
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Password of the user."
                ),
            },
        ),
        responses={
            200: "User logged in successfully",
            400: "Invalid login credentials",
        },
    )
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "status": "success",
                    "message": "User logged in successfully",
                    "data": {"token": token.key},
                }
            )
        else:
            return Response(
                {"status": "error", "message": "Invalid login credentials", "data": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )


class NoteCreate(generics.CreateAPIView):
    """
    POST notes/create/
    """

    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new note.",
        request_body=NoteSerializer,
        responses={201: "Note created successfully", 401: "Authentication required"},
    )
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            return Response(
                {"status": "error", "message": "Authentication required", "data": {}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer.save(user=self.request.user)
        return Response(
            {
                "status": "success",
                "message": "Note created successfully",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class NoteRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    GET notes/:id/
    PUT notes/:id/
    DELETE notes/:id/
    """

    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve, update, or delete a note.",
        responses={
            200: "Operation successful",
            403: "You do not have permission to access this note",
        },
    )
    def get_object(self):
        note = super().get_object()
        print(self.request.user)
        print(note.shared_with.all())
        print(note)
        if (
            self.request.user != note.user
            and self.request.user not in note.shared_with.all()
        ):
            raise PermissionDenied(
                {
                    "status": "error",
                    "message": "You do not have permission to access this note",
                    "data": {},
                }
            )
        return note


class NoteShare(generics.UpdateAPIView):
    """
    POST notes/:id/share/
    """

    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Share a note with specified users.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "shared_with": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description="List of usernames to share the note with.",
                )
            },
        ),
        responses={
            200: "Note shared successfully",
            403: "You do not have permission to share this note",
        },
    )
    def update(self, request, *args, **kwargs):
        note = self.get_object()
        if note.user != request.user:
            return Response(
                {
                    "status": "error",
                    "message": "You do not have permission to share this note",
                    "data": {},
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        shared_with = request.data.get("shared_with")
        for username in shared_with:
            user = User.objects.get(username=username)
            note.shared_with.add(user)
        note.save()
        return Response(
            {
                "status": "success",
                "message": "Note shared successfully",
                "data": NoteSerializer(note).data,
            }
        )


class NoteUpdateWithHistory(generics.UpdateAPIView):
    """
    PUT notes/:id/update/
    """

    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update a note and create a history record.",
        request_body=NoteSerializer,
        responses={
            200: "Note updated successfully",
            403: "You do not have permission to edit this note",
        },
    )
    def update(self, request, *args, **kwargs):
        note = self.get_object()
        if request.user not in note.shared_with.all() and note.user != request.user:
            return Response(
                {
                    "status": "error",
                    "message": "You do not have permission to edit this note",
                    "data": {},
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        NoteHistory.objects.create(
            note=note, content=note.content, updated_by=request.user
        )
        response = super().update(request, *args, **kwargs)
        return Response(
            {
                "status": "success",
                "message": "Note updated successfully",
                "data": response.data,
            }
        )


class NoteHistoryList(generics.ListAPIView):
    """
    GET notes/version-history/:id/
    """

    serializer_class = NoteHistorySerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get the version history of a note.",
        responses={
            200: "Operation successful",
            403: "You do not have permission to access this note's history",
        },
    )
    def get_queryset(self):
        note = generics.get_object_or_404(Note, id=self.kwargs["pk"])
        if (
            self.request.user != note.user
            and self.request.user not in note.shared_with.all()
        ):
            return Response(
                {
                    "status": "error",
                    "message": "You do not have permission to access this note's history",
                    "data": {},
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return NoteHistory.objects.filter(note=note)
