from django.contrib import admin
from .models import Court, Document, Opinion, Block, Footnote


class OpinionInline(admin.TabularInline):
    model = Opinion
    extra = 0
    fields = ("order", "type", "author")


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ("court_id", "label", "claude_done", "suspect_count")
    list_filter = ("claude_done",)
    search_fields = ("court_id", "label", "notes")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("stem", "court", "doc_type", "n_pages", "suspect", "coverage")
    list_filter = ("court", "doc_type", "suspect")
    search_fields = ("stem", "docket_number")
    inlines = [OpinionInline]


@admin.register(Opinion)
class OpinionAdmin(admin.ModelAdmin):
    list_display = ("document", "order", "type", "author")
    list_filter = ("type",)
    search_fields = ("author",)


admin.site.register(Block)
admin.site.register(Footnote)
