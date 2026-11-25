import firebase_admin


def initialize_firebase() -> firebase_admin.App:
    return firebase_admin.initialize_app(
        options={"projectId": "aliceai-ae27f"}
    )
