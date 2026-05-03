from django.core.management.base import BaseCommand
from orders.models import PromoCode


class Command(BaseCommand):
    help = 'Create sample promo codes for testing'

    def handle(self, *args, **options):
        promo_codes = [
            {'code': 'WELCOME10', 'discount_percent': 10, 'active': True},
            {'code': 'SUMMER20', 'discount_percent': 20, 'active': True},
            {'code': 'SAVE15', 'discount_percent': 15, 'active': True},
            {'code': 'NEWYEAR25', 'discount_percent': 25, 'active': True},
            {'code': 'SPECIAL30', 'discount_percent': 30, 'active': True},
            {'code': 'EXPIRED5', 'discount_percent': 5, 'active': False},
        ]

        created_count = 0
        for promo_data in promo_codes:
            promo, created = PromoCode.objects.get_or_create(
                code=promo_data['code'],
                defaults={
                    'discount_percent': promo_data['discount_percent'],
                    'active': promo_data['active']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created promo code: {promo.code} ({promo.discount_percent}%)'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Promo code already exists: {promo.code}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Total created: {created_count} promo codes')
        )
