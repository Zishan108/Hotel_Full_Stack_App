# admin.py
from django.contrib import admin
from .models import *

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'phone', 'email', 'is_active']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug', 'phone']
    fields = ['name', 'slug', 'tagline', 'thumbnail', 'address', 'phone', 'email', 'is_active']

@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'title', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['hotel', 'is_active']
    search_fields = ['hotel__name', 'title']

@admin.register(MainInfo)
class MainInfoAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'title', 'updated_at']
    list_filter = ['hotel']
    search_fields = ['hotel__name', 'title']

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'title', 'category', 'order', 'is_active']
    list_filter = ['hotel', 'category', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['hotel__name', 'title']

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'name', 'price_per_night', 'is_available', 'order']
    list_editable = ['price_per_night', 'is_available', 'order']
    list_filter = ['hotel', 'is_available']
    search_fields = ['hotel__name', 'name']

@admin.register(SectionContent)
class SectionContentAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'section_type', 'title', 'is_active']
    list_editable = ['is_active']
    list_filter = ['hotel', 'section_type', 'is_active']
    
    fieldsets = (
        ('Hotel & Section', {
            'fields': ('hotel', 'section_type', 'title', 'description', 'is_active')
        }),
        ('Images', {
            'fields': ('image1', 'image2', 'image3'),
            'classes': ('collapse',)
        }),
        ('Buttons', {
            'fields': ('button1_text', 'button1_link', 'button2_text', 'button2_link'),
            'classes': ('collapse',)
        }),
        ('FAQ Section Overlay', {
            'fields': ('overlay_title', 'overlay_text', 'overlay_button_text', 'overlay_button_link'),
            'classes': ('collapse',)
        }),
    )

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'question', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['hotel', 'is_active']
    search_fields = ['hotel__name', 'question']

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'title', 'category', 'published_date', 'is_published']
    list_filter = ['hotel', 'category', 'is_published']
    list_editable = ['is_published']
    search_fields = ['hotel__name', 'title', 'category']