from sqlalchemy.dialects.postgresql import insert

from app.config.database import SessionLocal
from app.models import User


def get_user(claims: dict) -> dict:
    with SessionLocal.begin() as db:
        statement = (
            insert(User)
            .values(
                firebase_uid=claims["uid"],
                name=claims.get("name"),
                email=claims.get("email"),
                avatar=claims.get("picture"),
            )
            .on_conflict_do_nothing(
                index_elements=[User.firebase_uid]
            )
        )

        db.execute(statement)
        user = db.get(User, claims["uid"])

        return {
            "firebaseUid": user.firebase_uid,
            "name": user.name,
            "email": user.email,
            "avatar": user.avatar,
        }

