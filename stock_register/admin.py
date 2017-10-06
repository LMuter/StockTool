from django.contrib import admin
from models import Stock, stock_readonly


class TransactionInline(admin.TabularInline):
    model = Stock.transactions.through
    extra = 0
    exclude = ()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class StockRegisterAdmin(admin.ModelAdmin):
    model = Stock
    readonly_fields = stock_readonly
    actions = []
    inlines = [TransactionInline]
    exclude = ('transactions',)

    fieldsets = [
        ('Meta info', {'fields': ['stock_id', 'stock_ref', 'owner', 'last_change', 'created']}),
    ]

    search_fields = ['stock_id', 'stock_ref', 'owner__user_last_name', 'owner__user_first_name']
    list_display = ('stock_id', 'stock_ref', 'owner', 'last_change', 'created')
    list_display_links = ('stock_id', 'stock_ref', 'owner', 'last_change', 'created')

    ordering = ['stock_id']

    def get_owner_name(self, obj):
        return obj.owner.user.get_full_name()

    get_owner_name.short_description = 'Owner of share'

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Stock, StockRegisterAdmin)