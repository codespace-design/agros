from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

def log_action(user, obj, action_flag, change_message=""):
    """
    Creates a LogEntry record for an action performed on an object.
    
    :param user: The User object performing the action.
    :param obj: The model instance being modified.
    :param action_flag: ADDITION, CHANGE, or DELETION.
    :param change_message: Optional description of the changes.
    """
    if not user or not user.is_authenticated:
        return
        
    LogEntry.objects.create(
        user_id=user.pk,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=str(obj.pk),
        object_repr=str(obj)[:200],
        action_flag=action_flag,
        change_message=change_message
    )
