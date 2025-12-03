
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.text import slugify
from PIL import Image
import os

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, help_text="URL-friendly identifier (e.g., mumbai-vile-parle)")
    tagline = models.CharField(max_length=300)
    address = models.TextField()
    phone = models.CharField(max_length=100)
    email = models.EmailField()
    thumbnail = models.ImageField(upload_to='hotel_thumbnails/', blank=True, null=True, help_text="Image for dropdown preview")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_preview_image(self):
        """Get preview image - either thumbnail or first carousel image"""
        if self.thumbnail:
            return self.thumbnail.url
        # Try to get first carousel image
        first_slide = self.carousel_slides.filter(is_active=True).first()
        if first_slide:
            return first_slide.image.url
        return None
    
    def __str__(self):
        return self.name

class CarouselSlide(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='carousel_slides')
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='carousel/')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['hotel', 'order']
    
    def __str__(self):
        return f"{self.hotel.name} - Slide {self.order}: {self.title}"

class MainInfo(models.Model):
    hotel = models.OneToOneField(Hotel, on_delete=models.CASCADE, related_name='main_info')
    title = models.CharField(max_length=200)
    highlighted_text = models.CharField(max_length=100)
    description = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.hotel.name} - Main Info"

class Card(models.Model):
    CATEGORY_CHOICES = [
        ('gallery', 'Gallery'),
        ('rooms', 'Rooms'),
        ('general', 'General'),
        ('special_offers', 'Special Offers'),
        ('blog', 'Blog'),
    ]
    
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='cards')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='cards/')
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    button_text = models.CharField(max_length=50, blank=True)
    button_link = models.CharField(max_length=200, blank=True)
    
    def get_image_dimensions(self):
        """Get image width and height for proper lazy loading"""
        if self.image:
            try:
                with Image.open(self.image.path) as img:
                    return img.size  # returns (width, height)
            except:
                return (400, 300)  # default dimensions
        return (400, 300)

    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.hotel.name} - {self.category}: {self.title}"

class RoomType(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_types')
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='rooms/')
    description = models.TextField(blank=True)
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.hotel.name} - {self.name}"

class SectionContent(models.Model):
    SECTION_CHOICES = [
        ('wedding', 'Wedding Venues'),
        ('banquet', 'Banquet Halls'),
        ('restaurant', 'Restaurant'),
        ('faq', 'FAQ Section'),
    ]
    
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='sections')
    section_type = models.CharField(max_length=20, choices=SECTION_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image1 = models.ImageField(upload_to='sections/', blank=True)
    image2 = models.ImageField(upload_to='sections/', blank=True)
    image3 = models.ImageField(upload_to='sections/', blank=True)
    button1_text = models.CharField(max_length=50, default="Know More")
    button1_link = models.CharField(max_length=200, blank=True)
    button2_text = models.CharField(max_length=50, default="Enquire Now")
    button2_link = models.CharField(max_length=200, blank=True)
    overlay_title = models.CharField(max_length=200, blank=True, default="Need More Help?")
    overlay_text = models.TextField(blank=True, default="Our team is available 24/7 to assist you with any queries.")
    overlay_button_text = models.CharField(max_length=50, blank=True, default="Contact Support")
    overlay_button_link = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['hotel', 'section_type']
    
    def __str__(self):
        return f"{self.hotel.name} - {self.get_section_type_display()}"

class FAQ(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
    
    def __str__(self):
        return f"{self.hotel.name} - {self.question[:50]}"

class BlogPost(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='blog_posts')
    title = models.CharField(max_length=200)
    excerpt = models.TextField()
    content = models.TextField()
    image = models.ImageField(upload_to='blogs/')
    category = models.CharField(max_length=100, default="General")
    published_date = models.DateField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-published_date']
    
    def __str__(self):
        return f"{self.hotel.name} - {self.title}"