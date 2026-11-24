from firebase_admin import App, auth


def verify_firebase_token(token: str, firebase_app: App) -> dict:
    return auth.verify_id_token(token, app=firebase_app)

