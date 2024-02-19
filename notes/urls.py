from django.urls import path
from .views import (
    UserCreate,
    LoginView,
    NoteCreate,
    NoteRetrieveUpdateDestroy,
    NoteShare,
    NoteUpdateWithHistory,
    NoteHistoryList,
)

urlpatterns = [
    path("signup/", UserCreate.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("notes/create/", NoteCreate.as_view(), name="note-create"),
    path("notes/<int:pk>/", NoteRetrieveUpdateDestroy.as_view(), name="note-detail"),
    path("notes/<int:pk>/share/", NoteShare.as_view(), name="note-share"),
    path("notes/<int:pk>/update/", NoteUpdateWithHistory.as_view(), name="note-update"),
    path(
        "notes/version-history/<int:pk>/",
        NoteHistoryList.as_view(),
        name="note-history",
    ),
]
