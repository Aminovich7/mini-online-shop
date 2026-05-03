import json
import shutil
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.management.base import BaseCommand

from accounts.models import CustomUser
from products.models import Category, Product, ProductImage


class Command(BaseCommand):
    help = "150 ta o'zbek mahsuloti bilan namuna katalog yaratadi."

    # Fetch 100 from page 1, 50 from page 2
    API_URL_1 = (
        "https://dummyjson.com/products"
        "?limit=100&skip=0"
        "&select=title,description,category,price,discountPercentage,brand,images,thumbnail"
    )
    API_URL_2 = (
        "https://dummyjson.com/products"
        "?limit=50&skip=100"
        "&select=title,description,category,price,discountPercentage,brand,images,thumbnail"
    )

    SAMPLE_SELLERS = ["seller1", "seller2", "seller3", "seller4", "seller5"]

    CATEGORY_NAMES = {
        "beauty": "Go'zallik",
        "fragrances": "Atirlar",
        "furniture": "Mebel",
        "groceries": "Oziq-ovqat",
        "home-decoration": "Dekor",
        "kitchen-accessories": "Oshxona",
        "laptops": "Noutbuklar",
        "mens-shirts": "Erkak kiyim",
        "mens-shoes": "Erkak oyoq kiyim",
        "mens-watches": "Erkak soat",
        "mobile-accessories": "Mobil aksessuarlar",
        "motorcycle": "Mototsikl",
        "skin-care": "Teri parvarishi",
        "smartphones": "Smartfonlar",
        "sports-accessories": "Sport anjomlar",
        "sunglasses": "Ko'zoynak",
        "tablets": "Planshetlar",
        "tops": "Ustki kiyim",
        "vehicle": "Avtomobil",
        "womens-bags": "Ayollar sumkasi",
        "womens-dresses": "Ayollar libosi",
        "womens-jewellery": "Taqinchoqlar",
        "womens-shoes": "Ayollar oyoq kiyimi",
        "womens-watches": "Ayollar soati",
    }

    CATEGORY_TITLE_PREFIX = {
        "beauty": "Go'zallik mahsuloti",
        "fragrances": "Atir",
        "furniture": "Mebel",
        "groceries": "Oziq-ovqat",
        "home-decoration": "Uy dekor",
        "kitchen-accessories": "Oshxona anjomi",
        "laptops": "Noutbuk",
        "mens-shirts": "Erkak ko'ylagi",
        "mens-shoes": "Erkak poyabzali",
        "mens-watches": "Erkak qo'l soati",
        "mobile-accessories": "Mobil aksessuar",
        "motorcycle": "Mototsikl",
        "skin-care": "Teri parvarishi",
        "smartphones": "Smartfon",
        "sports-accessories": "Sport aksessuari",
        "sunglasses": "Quyosh ko'zoynagi",
        "tablets": "Planshet",
        "tops": "Ustki kiyim",
        "vehicle": "Transport vositasi",
        "womens-bags": "Ayollar sumkasi",
        "womens-dresses": "Ayollar libosi",
        "womens-jewellery": "Ayollar taqinchog'i",
        "womens-shoes": "Ayollar poyabzali",
        "womens-watches": "Ayollar soati",
    }

    DESCRIPTION_TEMPLATES = {
        "beauty": "{brand} brendining {source_title} mahsuloti kundalik go'zallik parvarishi uchun qulay. Yumshoq tekstura, zamonaviy dizayn va ishonchli natija bilan ajralib turadi.",
        "fragrances": "{brand} tomonidan taqdim etilgan {source_title} nafis hid va kundalik foydalanish uchun mos yechimdir. Sovg'a uchun ham, shaxsiy foydalanish uchun ham yaxshi tanlov.",
        "furniture": "{source_title} {brand} uslubidagi qulay va mustahkam mebel yechimidir. Uy yoki ish joyiga zamonaviy ko'rinish berish uchun tavsiya etiladi.",
        "groceries": "{source_title} mazali va kundalik ehtiyojlar uchun mos oziq-ovqat mahsulotidir. Sifatli tarkib va qulay iste'mol formati bilan tanlanadi.",
        "home-decoration": "{source_title} uyingiz interyeriga chiroyli ko'rinish qo'shadigan dekor mahsulotidir. {brand} uslubidagi bu buyum zamonaviy makonlar uchun mos.",
        "kitchen-accessories": "{source_title} oshxona ishlarini osonlashtirish uchun yaratilgan foydali anjomdir. Mustahkam material va qulay foydalanish tajribasini beradi.",
        "laptops": "{brand} ning {source_title} modeli ish, o'qish va kundalik vazifalar uchun mos noutbukdir. Tezkor ishlash, zamonaviy ko'rinish va qulay foydalanish imkonini beradi.",
        "mens-shirts": "{source_title} erkaklar uchun qulay va chiroyli kiyim variantidir. Kundalik uslub va tartibli ko'rinishni birlashtiradi.",
        "mens-shoes": "{source_title} erkaklar uchun mustahkam va qulay poyabzal bo'lib, faol kun davomida ishonchli foydalanish beradi.",
        "mens-watches": "{source_title} erkaklar uchun zamonaviy qo'l soati bo'lib, uslub va qulaylikni uyg'unlashtiradi.",
        "mobile-accessories": "{source_title} smartfon va mobil qurilmalardan foydalanishni yanada qulay qiluvchi aksessuardir. Kundalik ishlatish uchun amaliy tanlov.",
        "motorcycle": "{source_title} kuchli ko'rinish va qulay boshqaruvni taklif etuvchi mototsikl namunasidir. Faol hayot tarzini yoqtiruvchilar uchun mos.",
        "skin-care": "{source_title} teri parvarishi uchun mo'ljallangan zamonaviy mahsulot bo'lib, kundalik rutinaga osongina moslashadi.",
        "smartphones": "{brand} ning {source_title} modeli aloqa, kontent ko'rish va kundalik vazifalar uchun qulay smartfondir. Zamonaviy dizayn va ishonchli ishlashni taqdim etadi.",
        "sports-accessories": "{source_title} mashg'ulot va faol dam olish uchun foydali sport anjomidir. Qulay foydalanish va yengil konstruksiya bilan ajralib turadi.",
        "sunglasses": "{source_title} quyoshdan himoya qiluvchi zamonaviy ko'zoynak bo'lib, kundalik uslubni to'ldiradi.",
        "tablets": "{brand} ning {source_title} modeli o'qish, video ko'rish va ish uchun mos planshetdir. Yengil korpus va qulay ekran tajribasini beradi.",
        "tops": "{source_title} kundalik kombinlar uchun mos bo'lgan zamonaviy ustki kiyimdir. Qulay bichim va chiroyli ko'rinishni taklif etadi.",
        "vehicle": "{source_title} zamonaviy transport vositasi namunasidir. Kundalik harakat va zamonaviy uslubni qadrlaydiganlar uchun mos.",
        "womens-bags": "{source_title} ayollar uchun nafis va qulay sumka bo'lib, kundalik obrazni mukammal to'ldiradi.",
        "womens-dresses": "{source_title} ayollar uchun didli va qulay libos bo'lib, turli holatlar uchun mos keladi.",
        "womens-jewellery": "{source_title} ayollar uchun nafis taqinchoq bo'lib, obrazga nozik jilo qo'shadi.",
        "womens-shoes": "{source_title} ayollar uchun qulay va didli poyabzal bo'lib, kundalik va bayramona uslubga mos tushadi.",
        "womens-watches": "{source_title} ayollar uchun nafis qo'l soati bo'lib, uslubni zamonaviy aksent bilan boyitadi.",
    }

    SAMPLE_ADDRESSES = [
        "Amir Temur ko'chasi 12, Toshkent",
        "Navoiy shoh ko'chasi 45, Samarqand",
        "Bunyodkor ko'chasi 27, Farg'ona",
        "Istiqlol ko'chasi 18, Andijon",
        "Shahrisabz ko'chasi 61, Buxoro",
        "Mustaqillik ko'chasi 33, Namangan",
        "Bog'ishamol ko'chasi 7, Toshkent",
        "Al-Xorazmiy ko'chasi 19, Urganch",
        "Tinchlik ko'chasi 55, Qarshi",
        "Shota Rustaveli ko'chasi 3, Nukus",
    ]

    SAMPLE_PHONES = [
        "+998 90 111 22 33",
        "+998 90 222 33 44",
        "+998 90 333 44 55",
        "+998 90 444 55 66",
        "+998 90 555 66 77",
        "+998 91 666 77 88",
        "+998 91 777 88 99",
        "+998 93 888 99 00",
        "+998 94 999 00 11",
        "+998 97 000 11 22",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Mavjud namuna ma'lumotlarini o'chirib, qayta yuklaydi.",
        )

    def handle(self, *args, **options):
        if options["force"]:
            self.stdout.write(self.style.WARNING("Eski namuna ma'lumotlar o'chirilmoqda..."))
            Product.objects.filter(author__username__in=self.SAMPLE_SELLERS).delete()
            Category.objects.filter(product__isnull=True).delete()
            self.stdout.write(self.style.WARNING("Eski namuna ma'lumotlar o'chirildi."))
        elif Product.objects.filter(author__username__in=self.SAMPLE_SELLERS).exists():
            self.stdout.write(self.style.WARNING(
                "Namuna ma'lumotlar allaqachon mavjud. Qayta yuklash uchun --force ishlating."
            ))
            return

        sellers = self._get_or_create_sellers()

        self.stdout.write("Mahsulotlar API dan yuklanmoqda...")
        product_payloads = self._fetch_products()
        self.stdout.write(self.style.SUCCESS(f"{len(product_payloads)} ta mahsulot ma'lumoti olindi."))

        categories = {}

        for index, payload in enumerate(product_payloads, start=1):
            seller = sellers[index % len(sellers)]
            category = self._get_or_create_category(categories, payload["category"])
            product = Product.objects.create(
                author=seller,
                category=category,
                title=self._build_title(payload),
                description=self._build_description(payload),
                price=Decimal(str(payload["price"])),
                address=self.SAMPLE_ADDRESSES[index % len(self.SAMPLE_ADDRESSES)],
                phone_number=self.SAMPLE_PHONES[index % len(self.SAMPLE_PHONES)],
                discount_percent=Decimal(
                    str(payload.get("discountPercentage", 0))
                ).quantize(Decimal("0.01")),
            )
            self._attach_real_images(product, payload)
            self.stdout.write(f"  [{index}/{len(product_payloads)}] ✓ {product.title}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nKatalog tayyor! "
                f"Jami mahsulotlar: {Product.objects.count()}. "
                f"Jami rasmlar: {ProductImage.objects.count()}."
            )
        )

    # ------------------------------------------------------------------ #
    #  API                                                                 #
    # ------------------------------------------------------------------ #

    def _fetch_products(self):
        payloads = []
        for url in [self.API_URL_1, self.API_URL_2]:
            request = Request(url, headers={"User-Agent": "mini-online-shop-seeder/1.0"})
            with urlopen(request, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
            payloads.extend(data.get("products", []))
        return payloads[:150]

    # ------------------------------------------------------------------ #
    #  Sellers                                                             #
    # ------------------------------------------------------------------ #

    def _get_or_create_sellers(self):
        sellers = []
        for number in range(1, 6):
            username = f"seller{number}"
            seller, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "type": "seller",
                    "first_name": f"Sotuvchi {number}",
                },
            )
            if created:
                seller.set_password("seller12345")
                seller.save(update_fields=["password"])
            elif seller.type != "seller":
                seller.type = "seller"
                seller.save(update_fields=["type"])
            sellers.append(seller)
        return sellers

    # ------------------------------------------------------------------ #
    #  Categories                                                          #
    # ------------------------------------------------------------------ #

    def _get_or_create_category(self, category_cache, category_slug):
        if category_slug in category_cache:
            return category_cache[category_slug]
        category_name = self.CATEGORY_NAMES.get(category_slug, "Mahsulotlar")
        category, _ = Category.objects.get_or_create(name=category_name)
        category_cache[category_slug] = category
        return category

    # ------------------------------------------------------------------ #
    #  Title & Description                                                 #
    # ------------------------------------------------------------------ #

    def _build_title(self, payload):
        category_slug = payload["category"]
        source_title = payload["title"]
        prefix = self.CATEGORY_TITLE_PREFIX.get(category_slug, "Mahsulot")
        brand = payload.get("brand") or ""
        if brand and brand.lower() not in source_title.lower():
            return f"{prefix}: {brand} {source_title}"[:150]
        return f"{prefix}: {source_title}"[:150]

    def _build_description(self, payload):
        category_slug = payload["category"]
        template = self.DESCRIPTION_TEMPLATES.get(
            category_slug,
            "{source_title} kundalik foydalanish uchun mo'ljallangan sifatli mahsulot bo'lib, zamonaviy dizayn va qulaylikni taklif etadi.",
        )
        brand = payload.get("brand") or "Ushbu"
        source_title = payload["title"]
        description = template.format(brand=brand, source_title=source_title)
        return (
            f"{description} Ushbu katalog yozuvi o'zbek tilida moslashtirildi "
            f"va mahsulot suratlari haqiqiy mahsulot fotosuratlaridan olindi."
        )

    # ------------------------------------------------------------------ #
    #  Images                                                              #
    # ------------------------------------------------------------------ #

    def _attach_real_images(self, product, payload):
        image_urls = self._pick_image_urls(payload)
        product_dir = Path(settings.MEDIA_ROOT) / "products" / f"product_{product.pk}"
        product_dir.mkdir(parents=True, exist_ok=True)

        for index, image_url in enumerate(image_urls, start=1):
            extension = Path(urlparse(image_url).path).suffix or ".jpg"
            if len(extension) > 5:
                extension = ".jpg"
            relative_path = f"products/product_{product.pk}/image_{index}{extension}"
            full_path = Path(settings.MEDIA_ROOT) / relative_path
            try:
                self._download_image(image_url, full_path)
                ProductImage.objects.create(product=product, image=relative_path)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"    Rasm yuklanmadi ({image_url}): {e}"))

    def _pick_image_urls(self, payload):
        raw_urls = list(payload.get("images") or [])
        thumbnail = payload.get("thumbnail")
        if thumbnail and thumbnail not in raw_urls:
            raw_urls.append(thumbnail)

        unique_urls = list(dict.fromkeys(url for url in raw_urls if url))

        if not unique_urls:
            raise ValueError(f"Mahsulot uchun rasm topilmadi: {payload['title']}")

        while len(unique_urls) < 3:
            unique_urls.append(unique_urls[-1])

        return unique_urls[:3]

    def _download_image(self, image_url, destination):
        request = Request(image_url, headers={"User-Agent": "mini-online-shop-seeder/1.0"})
        with urlopen(request, timeout=60) as response:
            destination.write_bytes(response.read())