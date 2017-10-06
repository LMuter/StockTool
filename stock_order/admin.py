from django.contrib import admin
from models import StockOrder, Transaction, stock_order_readonly


class TransactionBuyInline(admin.TabularInline):
    model = Transaction
    extra = 0
    fk_name = 'buy'
    verbose_name_plural = "Buy transactions"
    readonly_fields = ['buy', 'sell', 'share_amount', 'share_price', 'transaction_status', 'transaction_date']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class TransactionSellInline(admin.TabularInline):
    model = Transaction
    extra = 0
    fk_name = 'sell'
    verbose_name_plural = "Sell transactions"
    fields = ['buy', 'share_amount', 'share_price', 'transaction_status', 'transaction_date']
    readonly_fields = ['buy', 'sell', 'share_amount', 'share_price', 'transaction_status', 'transaction_date']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class StockOrderAdmin(admin.ModelAdmin):
    model = StockOrder

    readonly_fields = stock_order_readonly
    inlines = [TransactionBuyInline, TransactionSellInline]
    actions = []

    fieldsets = [
        ('Meta info', {'fields': ['order_id', 'order_date', 'owner']}),
        ('Order', {'fields': ['order_type', 'order_amount_of_shares', 'order_price_per_share',
                              'order_definite_number_of_shares', 'order_definite_price', 'order_result']}),
        ('Status', {'fields': ['order_status', 'is_archived']}),
        ('bidding round', {'fields': ['bidding_round']}),
    ]

    search_fields = ['order_id', 'owner']
    list_display = ('order_id', 'get_owner_name', 'order_type', 'order_status', 'order_amount_of_shares',
                    'order_price_per_share', 'is_archived')
    list_display_links = ('order_id', 'get_owner_name', 'order_type', 'order_status', 'order_amount_of_shares',
                          'order_price_per_share', 'is_archived')

    ordering = ['order_id']

    def get_owner_name(self, obj):
        return obj.owner.get_full_name()

    def has_delete_permission(self, request, obj=None):
        return False

    get_owner_name.short_description = 'Owner of share order'
    #get_owner_name.admin_order_field = 'owner__user_name'


admin.site.register(StockOrder, StockOrderAdmin)

