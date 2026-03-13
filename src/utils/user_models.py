import uuid

from pydantic import BaseModel, Field


class UserFromDB(BaseModel):
    id: str = Field(..., default_factory=lambda: str(uuid.uuid4()))
    firebaseUID: str
    displayName: str | None = None
    useProvidedIcon: bool = False


class UserFromFirebase(BaseModel):
    firebaseUID: str
    IconURL: str | None = None
    isGuest: bool = False


class User(BaseModel):
    id: str
    displayName: str | None = None
    IconURL: str | None = None
    useProvidedIcon: bool = False


class UpdateUser(BaseModel):
    displayName: str | None = Field(None, max_length=30, min_length=1)
    useProvidedIcon: bool = False
