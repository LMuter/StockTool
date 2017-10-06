from django.contrib import admin, messages
from models import Person
from stock_order.models import StockOrder, stock_order_readonly
from email_conversation.models import Email, email_readonly_fields
from user_login.models import UserLogin


class StockOrderInline(admin.TabularInline):
    model = StockOrder
    extra = 0

    readonly_fields = stock_order_readonly
    exclude = ('encrypted_order_id',)

    def has_add_permission(self, request):
        return False


class EmailInline(admin.TabularInline):
    model = Email
    extra = 0

    readonly_fields = email_readonly_fields

    def has_add_permission(self, request):
        return False


class UserLoginInline(admin.TabularInline):
    model = UserLogin
    extra = 0


class PersonAdmin(admin.ModelAdmin):
    model = Person
    actions = ['delete_selection']
    inlines = [StockOrderInline, EmailInline, UserLoginInline]

    readonly_fields = ('number_of_orders_total', 'number_of_orders_accepted', 'number_of_orders_pending',
                       'number_of_orders_final', 'number_of_orders_archived',)

    fieldsets = [
        # ('User info', {'fields': ['user_type', 'user_communication_type']}), todo implement when database update
        ('User info', {'fields': ['user_type']}),
        ('Order info', {'fields': ['number_of_orders_max', 'number_of_orders_total', 'number_of_orders_accepted',
                                   'number_of_orders_pending', 'number_of_orders_final', 'number_of_orders_archived']}),
        ('Stock info', {'fields': ['number_of_stocks']}),
        ('Personal details', {'fields': ['user_last_name', 'user_first_name', 'user_title', 'user_initials',
                                         'user_infix', 'user_sex', 'user_country', 'user_date_of_birth',
                                         'user_street_name', 'user_house_number', 'user_house_number_addition',
                                         'user_postal_code', 'user_residence', 'user_telephone', 'user_email_address',
                                         'user_mobile_telephone_number',
        ]}),
    ]
    search_fields = ['person_id', 'user_last_name', 'user_first_name', 'user_date_of_birth']
    list_display = ('person_id', 'get_full_name', 'user_email_address', 'user_type')
    list_display_links = ('person_id', 'get_full_name', 'user_email_address',
                          'user_type')

    ordering = ['person_id']

    def get_full_name(self, obj):
        return unicode(obj.user_title) + " " + unicode(obj.user_initials) + " (" + unicode(obj.user_first_name) + ") " + \
               unicode(obj.user_infix) + " " + unicode(obj.user_last_name)

    def has_delete_permission(self, request, obj=None):
        return False

    def delete_selection(self, request, queryset):
        try:
            queryset.delete()
            self.message_user(request, 'Selection deleted successfully', level=messages.SUCCESS)
        except Exception as e:
            self.message_user(request, e.message, level=messages.ERROR)

    delete_selection.short_description = "Delete selection"



admin.site.register(Person, PersonAdmin)
