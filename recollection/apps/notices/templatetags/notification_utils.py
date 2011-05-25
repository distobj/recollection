from django import template
from notification.models import Notice
register = template.Library()

@register.inclusion_tag("notification/notification_summary_list.html", takes_context=True)
def notification_summary_list(context, user, max_count=5):
   queryset =Notice.objects.filter(user=user)
   return {"queryset": queryset, "request": context["request"], "max_count": max_count,
           "user": user}
