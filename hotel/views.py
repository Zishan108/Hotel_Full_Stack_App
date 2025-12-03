# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import *
import json
from datetime import datetime, timedelta
from django.utils import timezone

def home(request, hotel_slug=None):
    # Check for preferred hotel in cookies if no slug provided
    preferred_hotel_slug = request.COOKIES.get('preferred_hotel_slug')
    
    # Check for recent hotels in cookies
    recent_hotels_json = request.COOKIES.get('recent_hotels', '[]')
    try:
        recent_hotels = json.loads(recent_hotels_json)
        if not isinstance(recent_hotels, list):
            recent_hotels = []
    except (json.JSONDecodeError, TypeError):
        recent_hotels = []
    
    # Track this visit
    first_visit = request.COOKIES.get('first_visit')
    if not first_visit:
        first_visit = timezone.now().isoformat()
    
    # Determine which hotel to show
    if hotel_slug:
        hotel = get_object_or_404(Hotel, slug=hotel_slug, is_active=True)
        
        # Update recent hotels
        if hotel_slug not in recent_hotels:
            recent_hotels.insert(0, hotel_slug)
            # Keep only last 5 hotels
            recent_hotels = recent_hotels[:5]
    elif preferred_hotel_slug:
        # Try to use preferred hotel from cookie
        try:
            hotel = Hotel.objects.get(slug=preferred_hotel_slug, is_active=True)
        except Hotel.DoesNotExist:
            # Fallback to first active hotel
            hotel = Hotel.objects.filter(is_active=True).first()
            if not hotel:
                # Handle case with no hotels
                return render(request, 'hotel/no_hotels.html')
    else:
        # Fallback to first active hotel
        hotel = Hotel.objects.filter(is_active=True).first()
        if not hotel:
            # Handle case with no hotels
            return render(request, 'hotel/no_hotels.html')
    
    # Prepare context
    context = {
        'hotel': hotel,
        'carousel_slides': CarouselSlide.objects.filter(hotel=hotel, is_active=True),
        'main_info': MainInfo.objects.filter(hotel=hotel).first(),
        'gallery_cards': Card.objects.filter(hotel=hotel, category='gallery', is_active=True),
        'general_cards': Card.objects.filter(hotel=hotel, category='general', is_active=True),
        'special_offers': Card.objects.filter(hotel=hotel, category='special_offers', is_active=True),
        'room_types': RoomType.objects.filter(hotel=hotel, is_available=True),
        'wedding_section': SectionContent.objects.filter(hotel=hotel, section_type='wedding', is_active=True).first(),
        'banquet_section': SectionContent.objects.filter(hotel=hotel, section_type='banquet', is_active=True).first(),
        'restaurant_section': SectionContent.objects.filter(hotel=hotel, section_type='restaurant', is_active=True).first(),
        'faq_section': SectionContent.objects.filter(hotel=hotel, section_type='faq', is_active=True).first(),
        'faqs': FAQ.objects.filter(hotel=hotel, is_active=True),
        'blog_posts': BlogPost.objects.filter(hotel=hotel, is_published=True)[:3],
        'all_hotels': Hotel.objects.filter(is_active=True),
        'recent_hotels': recent_hotels,
        'is_first_visit': not bool(request.COOKIES.get('first_visit')),
    }
    
    # Create response
    response = render(request, 'hotel/index.html', context)
    
    # Set cookies
    # Set current hotel as preferred (30 days expiry)
    response.set_cookie(
        'preferred_hotel_slug',
        hotel.slug,
        max_age=30*24*60*60,  # 30 days
        httponly=True,
        samesite='Lax',
        secure=False  # Set to True in production with HTTPS
    )
    
    # Set current hotel slug cookie for immediate use
    response.set_cookie(
        'current_hotel_slug',
        hotel.slug,
        max_age=24*60*60,  # 1 day
        httponly=False,  # Allow JS access
        samesite='Lax'
    )
    
    # Update recent hotels cookie
    response.set_cookie(
        'recent_hotels',
        json.dumps(recent_hotels),
        max_age=30*24*60*60,  # 30 days
        httponly=True,
        samesite='Lax'
    )
    
    # Set first visit cookie if not set
    if not request.COOKIES.get('first_visit'):
        response.set_cookie(
            'first_visit',
            first_visit,
            max_age=365*24*60*60,  # 1 year
            httponly=True,
            samesite='Lax'
        )
    
    # Set last visit cookie
    response.set_cookie(
        'last_visit',
        timezone.now().isoformat(),
        max_age=30*24*60*60,  # 30 days
        httponly=True,
        samesite='Lax'
    )
    
    # Set visit count
    visit_count = int(request.COOKIES.get('visit_count', 0)) + 1
    response.set_cookie(
        'visit_count',
        str(visit_count),
        max_age=365*24*60*60,  # 1 year
        httponly=True,
        samesite='Lax'
    )
    
    # Set user preferences cookies if they exist in request
    if 'theme_preference' in request.GET:
        response.set_cookie(
            'theme_preference',
            request.GET.get('theme_preference'),
            max_age=365*24*60*60,
            httponly=False,
            samesite='Lax'
        )
    
    if 'language_preference' in request.GET:
        response.set_cookie(
            'language_preference',
            request.GET.get('language_preference'),
            max_age=365*24*60*60,
            httponly=False,
            samesite='Lax'
        )
    
    return response

def hotel_list(request):
    """View to list all active hotels"""
    hotels = Hotel.objects.filter(is_active=True)
    
    # Get recent hotels from cookies
    recent_hotels_json = request.COOKIES.get('recent_hotels', '[]')
    try:
        recent_hotels = json.loads(recent_hotels_json)
        if not isinstance(recent_hotels, list):
            recent_hotels = []
    except (json.JSONDecodeError, TypeError):
        recent_hotels = []
    
    # Create a dictionary of recent hotels for quick lookup
    recent_hotel_slugs = set(recent_hotels)
    
    # Get visit count
    visit_count = int(request.COOKIES.get('visit_count', 0))
    
    context = {
        'hotels': hotels,
        'recent_hotel_slugs': recent_hotel_slugs,
        'visit_count': visit_count,
        'first_visit': request.COOKIES.get('first_visit'),
        'last_visit': request.COOKIES.get('last_visit'),
    }
    
    # Create response with cookie updates
    response = render(request, 'hotel/hotel_list.html', context)
    
    # Update last activity timestamp
    response.set_cookie(
        'last_activity',
        timezone.now().isoformat(),
        max_age=30*24*60*60,
        httponly=True,
        samesite='Lax'
    )
    
    return response

def set_preference(request):
    """API endpoint to set user preferences via AJAX"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        preference_type = request.POST.get('type')
        preference_value = request.POST.get('value')
        
        response_data = {'status': 'success', 'type': preference_type, 'value': preference_value}
        http_response = HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
        
        # Set the cookie based on preference type
        if preference_type == 'theme':
            http_response.set_cookie(
                'theme_preference',
                preference_value,
                max_age=365*24*60*60,
                httponly=False,
                samesite='Lax'
            )
        elif preference_type == 'language':
            http_response.set_cookie(
                'language_preference',
                preference_value,
                max_age=365*24*60*60,
                httponly=False,
                samesite='Lax'
            )
        elif preference_type == 'newsletter':
            http_response.set_cookie(
                'newsletter_subscribed',
                'true' if preference_value == 'true' else 'false',
                max_age=365*24*60*60,
                httponly=True,
                samesite='Lax'
            )
        
        return http_response
    
    return HttpResponse(json.dumps({'status': 'error', 'message': 'Invalid request'}), 
                       content_type='application/json', status=400)

def clear_preferences(request):
    """Clear user preferences (for testing/development)"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        response = HttpResponse(json.dumps({'status': 'success'}), content_type='application/json')
        
        # Clear specific preference cookies
        cookies_to_clear = [
            'theme_preference',
            'language_preference',
            'recent_hotels',
            'preferred_hotel_slug',
            'newsletter_subscribed'
        ]
        
        for cookie_name in cookies_to_clear:
            response.delete_cookie(cookie_name)
        
        return response
    
    return redirect('home_default')

def get_user_data(request):
    """Get user data stored in cookies (for client-side use)"""
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user_data = {
            'preferred_hotel': request.COOKIES.get('preferred_hotel_slug'),
            'current_hotel': request.COOKIES.get('current_hotel_slug'),
            'theme': request.COOKIES.get('theme_preference', 'light'),
            'language': request.COOKIES.get('language_preference', 'en'),
            'first_visit': request.COOKIES.get('first_visit'),
            'last_visit': request.COOKIES.get('last_visit'),
            'visit_count': int(request.COOKIES.get('visit_count', 0)),
            'newsletter_subscribed': request.COOKIES.get('newsletter_subscribed') == 'true',
            'last_activity': request.COOKIES.get('last_activity'),
        }
        
        # Get recent hotels
        recent_hotels_json = request.COOKIES.get('recent_hotels', '[]')
        try:
            user_data['recent_hotels'] = json.loads(recent_hotels_json)
        except (json.JSONDecodeError, TypeError):
            user_data['recent_hotels'] = []
        
        return HttpResponse(
            json.dumps({'status': 'success', 'data': user_data}),
            content_type='application/json'
        )
    
    return HttpResponse(json.dumps({'status': 'error'}), 
                       content_type='application/json', status=400)

def set_hotel_comparison(request):
    """API to add/remove hotels from comparison list"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        action = request.POST.get('action')
        hotel_slug = request.POST.get('hotel_slug')
        hotel_name = request.POST.get('hotel_name')
        
        # Get current comparison list from cookies
        comparison_json = request.COOKIES.get('comparison_list', '[]')
        try:
            comparison_list = json.loads(comparison_json)
            if not isinstance(comparison_list, list):
                comparison_list = []
        except (json.JSONDecodeError, TypeError):
            comparison_list = []
        
        if action == 'add':
            # Add hotel to comparison if not already there
            if not any(h.get('slug') == hotel_slug for h in comparison_list):
                comparison_list.append({
                    'slug': hotel_slug,
                    'name': hotel_name,
                    'added_at': timezone.now().isoformat()
                })
                # Keep only last 3 hotels
                comparison_list = comparison_list[-3:]
                message = f'Added {hotel_name} to comparison list'
        elif action == 'remove':
            # Remove hotel from comparison
            comparison_list = [h for h in comparison_list if h.get('slug') != hotel_slug]
            message = f'Removed {hotel_name} from comparison list'
        elif action == 'clear':
            comparison_list = []
            message = 'Cleared comparison list'
        else:
            return HttpResponse(
                json.dumps({'status': 'error', 'message': 'Invalid action'}),
                content_type='application/json',
                status=400
            )
        
        response_data = {
            'status': 'success',
            'action': action,
            'comparison_list': comparison_list,
            'message': message
        }
        
        http_response = HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
        
        # Update comparison list cookie
        http_response.set_cookie(
            'comparison_list',
            json.dumps(comparison_list),
            max_age=30*24*60*60,
            httponly=False,  # Allow JS access
            samesite='Lax'
        )
        
        return http_response
    
    return HttpResponse(
        json.dumps({'status': 'error', 'message': 'Invalid request'}),
        content_type='application/json',
        status=400
    )

def save_booking_data(request):
    """Save partial booking form data"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            booking_data = json.loads(request.body)
            
            # Validate required fields
            if not all(k in booking_data for k in ['check_in', 'check_out', 'guests']):
                return HttpResponse(
                    json.dumps({'status': 'error', 'message': 'Missing required fields'}),
                    content_type='application/json',
                    status=400
                )
            
            # Add timestamp
            booking_data['saved_at'] = timezone.now().isoformat()
            booking_data['expires_at'] = (timezone.now() + timedelta(hours=24)).isoformat()
            
            response_data = {
                'status': 'success',
                'message': 'Booking data saved',
                'expires_in': '24 hours'
            }
            
            http_response = HttpResponse(
                json.dumps(response_data),
                content_type='application/json'
            )
            
            # Save to cookie (24 hour expiry)
            http_response.set_cookie(
                'booking_form_data',
                json.dumps(booking_data),
                max_age=24*60*60,
                httponly=False,  # Allow JS access
                samesite='Lax'
            )
            
            return http_response
            
        except json.JSONDecodeError:
            return HttpResponse(
                json.dumps({'status': 'error', 'message': 'Invalid JSON data'}),
                content_type='application/json',
                status=400
            )
    
    return HttpResponse(
        json.dumps({'status': 'error', 'message': 'Invalid request method'}),
        content_type='application/json',
        status=400
    )

def get_booking_data(request):
    """Get saved booking form data"""
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        booking_json = request.COOKIES.get('booking_form_data')
        
        if booking_json:
            try:
                booking_data = json.loads(booking_json)
                
                # Check if data has expired
                expires_at_str = booking_data.get('expires_at')
                if expires_at_str:
                    expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                    if timezone.now() > expires_at:
                        # Data expired, clear it
                        response_data = {'status': 'expired', 'data': None}
                        http_response = HttpResponse(
                            json.dumps(response_data),
                            content_type='application/json'
                        )
                        http_response.delete_cookie('booking_form_data')
                        return http_response
                
                return HttpResponse(
                    json.dumps({'status': 'success', 'data': booking_data}),
                    content_type='application/json'
                )
            except (json.JSONDecodeError, ValueError):
                pass
        
        return HttpResponse(
            json.dumps({'status': 'success', 'data': None}),
            content_type='application/json'
        )
    
    return HttpResponse(
        json.dumps({'status': 'error', 'message': 'Invalid request'}),
        content_type='application/json',
        status=400
    )

def cookie_consent(request):
    """Handle cookie consent preferences"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        consent_type = request.POST.get('type', 'all')
        granted = request.POST.get('granted', 'true') == 'true'
        
        response_data = {
            'status': 'success',
            'consent_type': consent_type,
            'granted': granted
        }
        
        http_response = HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
        
        # Set consent cookie based on type
        if consent_type == 'essential' or consent_type == 'all':
            http_response.set_cookie(
                'cookie_consent_essential',
                'true' if granted else 'false',
                max_age=365*24*60*60,
                httponly=True,
                samesite='Lax'
            )
        
        if consent_type == 'analytics' or consent_type == 'all':
            http_response.set_cookie(
                'cookie_consent_analytics',
                'true' if granted else 'false',
                max_age=365*24*60*60,
                httponly=True,
                samesite='Lax'
            )
        
        if consent_type == 'marketing' or consent_type == 'all':
            http_response.set_cookie(
                'cookie_consent_marketing',
                'true' if granted else 'false',
                max_age=365*24*60*60,
                httponly=True,
                samesite='Lax'
            )
        
        # Set overall consent timestamp
        if consent_type == 'all':
            http_response.set_cookie(
                'cookie_consent_given',
                timezone.now().isoformat(),
                max_age=365*24*60*60,
                httponly=True,
                samesite='Lax'
            )
        
        return http_response
    
    return HttpResponse(
        json.dumps({'status': 'error', 'message': 'Invalid request'}),
        content_type='application/json',
        status=400
    )

def check_consent(request):
    """Check user's cookie consent status"""
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        consent_data = {
            'essential': request.COOKIES.get('cookie_consent_essential', 'false') == 'true',
            'analytics': request.COOKIES.get('cookie_consent_analytics', 'false') == 'true',
            'marketing': request.COOKIES.get('cookie_consent_marketing', 'false') == 'true',
            'given_at': request.COOKIES.get('cookie_consent_given'),
        }
        
        return HttpResponse(
            json.dumps({'status': 'success', 'consent': consent_data}),
            content_type='application/json'
        )
    
    return HttpResponse(
        json.dumps({'status': 'error', 'message': 'Invalid request'}),
        content_type='application/json',
        status=400
    )