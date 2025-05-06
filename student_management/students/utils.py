from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

def log_student_action(user, obj, action_flag, message):
    if not user.is_authenticated:
        # Use a dummy user named "user"
        try:
            user = User.objects.get(username='user')
        except User.DoesNotExist:
            user = User.objects.create_user(username='user', password='user')
            user.is_staff = False
            user.save()

    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj),
        action_flag=action_flag,
        change_message=message,
    )