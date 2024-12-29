import firebase_admin
from firebase_admin import credentials

# Initialize Firebase Admin SDK
cred = credentials.Certificate(
    r"storage-7a382-firebase-adminsdk-1rvsg-291e4a387d.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'storage-7a382.appspot.com',
    'databaseURL': 'https://storage-7a382-default-rtdb.firebaseio.com/'
})
