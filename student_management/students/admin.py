from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from .models import StudentInfo

class StudentAdmin(admin.ModelAdmin):
    search_fields = ['name', 'email', 'course', 'interest']
    list_display = ('name', 'email', 'address', 'gender', 'age', 'interest', 'course')
    list_filter = ('age', 'gender', 'course')

    def log_addition(self, request, obj, message):
        pass

    def log_deletion(self, request, obj, message):
        pass
        
    def save_model(self, request, obj, form, change):
        content_type = ContentType.objects.get_for_model(obj)

        if change:
            # Prevent default CHANGE log
            # Don't call super().save_model before logging
            old_obj = StudentInfo.objects.get(pk=obj.pk)
            changes = []

            for field in form.changed_data:
                old_value = getattr(old_obj, field)
                new_value = getattr(obj, field)
                changes.append(f"Changed the {field} of {obj.name} from {old_value} to {new_value}")

            if changes:
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=content_type.pk,
                    object_id=obj.pk,
                    object_repr=str(obj),
                    action_flag=CHANGE,
                    change_message=", ".join(changes)
                )

        elif not change:
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=content_type.pk,
                object_id=obj.pk,
                object_repr=str(obj),
                action_flag=ADDITION,
                change_message=f"Added student: {obj.name}"
            )

        # Only save AFTER logging to avoid Django's default change log
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(obj).pk,
            object_id=obj.pk,
            object_repr=str(obj),
            action_flag=DELETION,
            change_message=f"Deleted student: {obj.name}"
        )
        super().delete_model(request, obj)

    def log_change(self, request, obj, message):
        # Disable Django's default change logging
        pass

    def changelist_view(self, request, extra_context=None):
        studentinfo_ct = ContentType.objects.get_for_model(StudentInfo)
        logs = LogEntry.objects.filter(content_type=studentinfo_ct).order_by('-action_time')
        admin_logs = logs.filter(user__is_staff=True)[:10]
        user_logs = logs.filter(user__is_staff=False)[:10]

        extra_context = extra_context or {}
        extra_context['admin_logs'] = admin_logs
        extra_context['user_logs'] = user_logs

        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(StudentInfo, StudentAdmin)
