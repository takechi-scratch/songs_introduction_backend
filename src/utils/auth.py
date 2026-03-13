from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import firebase_admin
from firebase_admin import auth, credentials

from src.utils.user_models import UserFromFirebase


def get_current_user(cred: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    if not cred:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        cred = auth.verify_id_token(cred.credentials)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return cred


def auth_initialize():
    cred = credentials.Certificate("./serviceAccountKey.json")
    firebase_admin.initialize_app(cred)


def add_admin_user(uid: str):
    auth.set_custom_user_claims(uid, {"admin": True})


def get_firebase_user(uid: str):
    try:
        user = auth.get_user(uid)
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")

    return UserFromFirebase(firebaseUID=user.uid, IconURL=user.photo_url, isGuest=bool(len(user.provider_data) == 0))


# TODO: TTL付きのキャッシュを実装
def get_firebase_users() -> list[UserFromFirebase]:
    users = []
    for user in auth.list_users().iterate_all():
        users.append(
            UserFromFirebase(firebaseUID=user.uid, IconURL=user.photo_url, isGuest=bool(len(user.provider_data) == 0))
        )
    return users


if __name__ == "__main__":
    auth_initialize()
