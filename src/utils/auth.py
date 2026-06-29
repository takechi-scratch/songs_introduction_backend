import time

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


firebase_users_cache = None
firebase_users_cache_timestamp = 0


# TODO: TTL付きのキャッシュを実装
def get_firebase_users() -> list[UserFromFirebase]:
    global firebase_users_cache, firebase_users_cache_timestamp

    if firebase_users_cache is None or time.time() - firebase_users_cache_timestamp > 300:  # 5分ごとに更新
        users = []
        for user in auth.list_users().iterate_all():
            users.append(
                UserFromFirebase(
                    firebaseUID=user.uid, IconURL=user.photo_url, isGuest=bool(len(user.provider_data) == 0)
                )
            )
        firebase_users_cache = users
        firebase_users_cache_timestamp = time.time()

    return firebase_users_cache


if __name__ == "__main__":
    auth_initialize()
