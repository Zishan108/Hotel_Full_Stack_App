# hotel/management/commands/seed_hotels.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from hotel.models import Hotel, MainInfo

class Command(BaseCommand):
    help = 'Seeds the database with initial hotel data'

    def handle(self, *args, **kwargs):
        # Create Mumbai Vile Parle hotel
        mumbai_hotel, created = Hotel.objects.get_or_create(
            name="Orchid Hotel Mumbai Vile Parle",
            defaults={
                'slug': 'mumbai-vile-parle',
                'tagline': "Asia's First Certified Eco-Friendly 5 Star Hotel",
                'address': "70-C, Nehru Road,\nVile Parle (East),\nMumbai - 400099",
                'phone': "+91 22 2616 4000\n+91 98200 12345 (24x7)",
                'email': "reservations.mumbai@orchidshotel.com",
                'is_active': True
            }
        )
        
        if created:
            # Create main info for Mumbai
            MainInfo.objects.create(
                hotel=mumbai_hotel,
                title="Asia's First Certified Eco-Friendly 5 STAR",
                highlighted_text="Hotel Near Mumbai Airport",
                description="""Experience The Orchid Hotel Mumbai Vile Parle, a top 5-star hotel near Mumbai Airport T1 & T2. Perfect for transit, business trips, and family stays, we offer luxury rooms, rooftop dining, banquet halls, and elegant wedding venues. Located minutes from Juhu Beach, BKC, and Bandra-Worli Sea Link, our eco-friendly hotel combines sustainable luxury with airport convenience. Book your stay near Mumbai Domestic Airport now!"""
            )
            self.stdout.write(self.style.SUCCESS(f'Created hotel: {mumbai_hotel.name}'))
        
        # Create Delhi hotel (example)
        delhi_hotel, created = Hotel.objects.get_or_create(
            name="Orchid Hotel Delhi Connaught Place",
            defaults={
                'slug': 'delhi-connaught-place',
                'tagline': "Luxury Hospitality in the Heart of Delhi",
                'address': "15, Parliament Street,\nConnaught Place,\nNew Delhi - 110001",
                'phone': "+91 11 2345 6789\n+91 98765 43210 (24x7)",
                'email': "reservations.delhi@orchidshotel.com",
                'is_active': True
            }
        )
        
        if created:
            MainInfo.objects.create(
                hotel=delhi_hotel,
                title="Premium 5-Star Luxury",
                highlighted_text="In the Heart of Delhi",
                description="""Experience unparalleled luxury at Orchid Hotel Delhi, located in the prestigious Connaught Place. Our hotel offers exquisite rooms, world-class dining, state-of-the-art banquet facilities, and impeccable service. Perfect for business travelers and tourists alike, we provide easy access to Delhi's major attractions, business centers, and shopping districts."""
            )
            self.stdout.write(self.style.SUCCESS(f'Created hotel: {delhi_hotel.name}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded hotel data!'))