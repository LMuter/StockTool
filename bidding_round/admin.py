from django.contrib import admin, messages
from django.core.cache import cache

from bidding_round import bidding_round_manager
from bidding_round.models import BiddingRound
from stock_order.models import StockOrder, stock_order_readonly
from stock_register.controller import get_compressed_stock_register_all

admin.site.disable_action('delete_selected')


class StockOrderInline(admin.TabularInline):
    model = StockOrder
    extra = 0

    readonly_fields = stock_order_readonly
    exclude = ('encrypted_order_id',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class BiddingRoundAdmin(admin.ModelAdmin):
    model = BiddingRound
    readonly_fields = ['round_id', ]
    inlines = [StockOrderInline]
    actions = ['handle_orders', 'achieve']

    fieldsets = [
        ('Meta info', {'fields': ['round_id', 'is_active', ]}),
        ('Third party',
         {'fields': ['start_date_third_party', 'end_date_third_party', 'publication_date_third_party', ]}),
        ('Staff', {'fields': ['start_date_staff', 'end_date_staff', 'publication_date_staff', ]}),
        ('Moderator', {'fields': ['start_date_moderator', 'end_date_moderator', 'publication_date_moderator', ]}),
        ('Handling', {'fields': ['handling_period_start', 'handling_period_end', ]}),
        ('Transaction', {'fields': ['transaction_publication_date', ]}),
        ('Active round', {'fields': ['round_type', ]}),
    ]

    search_fields = ['round_id', 'is_active']
    list_display = ('round_id', 'start_date_third_party', 'transaction_publication_date', 'round_type',)
    list_display_links = ('round_id', 'start_date_third_party', 'transaction_publication_date', 'round_type',)

    ordering = ['round_id']

    def handle_orders(self, request, queryset):
        try:
            exchange_manager = bidding_round_manager.ExchangeManager()
            exchange_manager.handle_transactions(bidding_rounds=queryset, save_transactions=True)
            self.message_user(request, 'handle_orders invoked successfully', level=messages.SUCCESS)
            cache.set('stock_register', get_compressed_stock_register_all(), 60 * 60 * 24 * 100)
        except Exception as e:
            self.message_user(request, e.message, level=messages.ERROR)

    handle_orders.short_description = "Handel all orders."

    def achieve(self, request, queryset):
        queryset.update(is_active=False)
        for bidding_round in queryset:
            stock_orders = StockOrder.objects.filter(bidding_round=bidding_round)
            for stock_order in stock_orders:
                stock_order.is_archived = True
                stock_order.owner.number_of_orders_archived += 1
                stock_order.owner.save()
                stock_order.save()
        queryset.update(is_active=False)
        self.message_user(request, 'All orders of the selected bidding rounds are archived.', level=messages.SUCCESS)

    achieve.short_description = "Archive all stock orders."

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(BiddingRound, BiddingRoundAdmin)
