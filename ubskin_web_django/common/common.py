from django.conf import settings


def build_photo_url(photo_id, pic_version="thumb", pic_type="photos", cdn=False):
    # identifier = "!"
    if not cdn:
        if photo_id:
            return "".join([
                settings.MEDIA_URL, pic_type, "/", pic_version,
                "/", photo_id[:2], "/", photo_id, ".jpg"
            ])
        else:
            return "".join(["/static/", "images/", "user-default.jpg"])
    else:
        if photo_id:
            return "".join([
                settings.SERVERHOST, "/media/", pic_type, "/", pic_version, 
                "/", photo_id[:2], "/", photo_id , ".jpg"
            ])
        else:
            return "".join([settings.SERVERHOST, "/static/", "images/", "user-default", ".png"])

