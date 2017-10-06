from django.contrib import admin
from models import Email, email_readonly_fields


# todo implement
# from models import EmailTemplate
# from django import forms


class EmailAdmin(admin.ModelAdmin):
    model = Email

    readonly_fields = email_readonly_fields

    fieldsets = [
        ('Meta info', {'fields': ['email_id', 'send_date', 'email_from', 'email_to', 'email_subject']}),
        ('Content', {'fields': ['email_content']}),
        ('Participant', {'fields': ['participant']}),

    ]

    search_fields = ['email_subject', 'send_date', 'email_to', 'email_from']
    list_display = ('email_id', 'email_to', 'email_subject', 'send_date')
    list_display_links = ('email_id', 'email_to', 'email_subject', 'send_date')
    ordering = ['email_id']

    def has_add_permission(self, request):
        return False


# todo implement
# class EmailTemplateAdmin(admin.ModelAdmin):
#     model = EmailTemplate
#
#     fieldsets = [
#         ('Information', {'fields': ['template_type', 'template_name']}),
#         ('Content', {'fields': ['template_text', 'template_html']}),
#     ]
#
#     search_fields = ['template_type', 'template_name']
#     list_display = ('template_type', 'template_name')
#     list_display_links = ('template_type', 'template_name')
#     ordering = ['template_name']


admin.site.register(Email, EmailAdmin)
# todo implement
# admin.site.register(EmailTemplate, EmailTemplateAdmin)
