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
    help = "Refresh sample catalog with 50 Uzbek products and real product photos."

    API_URL = (
        "https://dummyjson.com/products"
        "?limit=50"
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
        "mens-shoes": "Erkak oyoq",
        "mens-watches": "Erkak soat",
        "mobile-accessories": "Mobil akses",
        "motorcycle": "Mototsikl",
        "skin-care": "Teri parvar",
        "smartphones": "Smartfonlar",
        "sports-accessories": "Sport anjom",
        "sunglasses": "Ko'zoynak",
        "tablets": "Planshetlar",
        "tops": "Ustki kiyim",
        "vehicle": "Avto",
        "womens-bags": "Ayol sumka",
        "womens-dresses": "Ayol libos",
        "womens-jewellery": "Taqinchoq",
        "womens-shoes": "Ayol oyoq",
        "womens-watches": "Ayol soat",
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

    TITLE_TRANSLATIONS = {
        "Essence Mascara Lash Princess": "Essence Lash Princess maskarasi",
        "Eyeshadow Palette with Mirror": "Oynali ten palitrasi",
        "Powder Canister": "Upa qutichasi",
        "Red Lipstick": "Qizil lab bo'yog'i",
        "Red Nail Polish": "Qizil tirnoq bo'yog'i",
        "Calvin Klein CK One": "Calvin Klein CK One atiri",
        "Chanel Coco Noir Eau De": "Chanel Coco Noir atiri",
        "Dior J'adore": "Dior J'adore atiri",
        "Dolce Shine Eau de": "Dolce Shine atiri",
        "Gucci Bloom Eau de": "Gucci Bloom atiri",
        "Annibale Colombo Bed": "Annibale Colombo karovati",
        "Annibale Colombo Sofa": "Annibale Colombo divani",
        "Bedside Table African Cherry": "Afrika olchasi rangidagi yotoq stolchasi",
        "Knoll Saarinen Executive Conference Chair": "Knoll Saarinen konferensiya o'rindig'i",
        "Wooden Bathroom Sink With Mirror": "Oynali yog'och lavabo to'plami",
        "Apple": "Olma",
        "Beef Steak": "Mol go'shti steyki",
        "Cat Food": "Mushuklar uchun yem",
        "Chicken Meat": "Tovuq go'shti",
        "Cooking Oil": "Osh yog'i",
        "Cucumber": "Bodring",
        "Dog Food": "Itlar uchun yem",
        "Eggs": "Tuxum",
        "Fish Steak": "Baliq steyki",
        "Green Bell Pepper": "Yashil bulg'or qalampiri",
        "Green Chili Pepper": "Yashil achchiq qalampir",
        "Honey Jar": "Asal bankasi",
        "Ice Cream": "Muzqaymoq",
        "Juice": "Sharbat",
        "Kiwi": "Kivi",
        "Lemon": "Limon",
        "Milk": "Sut",
        "Mulberry": "Tut mevasi",
        "Nescafe Coffee": "Nescafe qahvasi",
        "Potatoes": "Kartoshka",
        "Protein Powder": "Protein kukuni",
        "Red Onions": "Qizil piyoz",
        "Rice": "Guruch",
        "Soft Drinks": "Gazli ichimliklar",
        "Strawberry": "Qulupnay",
        "Tissue Paper Box": "Salfetka qutisi",
        "Water": "Suv",
        "Decoration Swing": "Dekorativ belanchak",
        "Family Tree Photo Frame": "Oila daraxti foto ramkasi",
        "House Showpiece Plant": "Uy uchun dekor o'simlik",
        "Plant Pot": "Gul tuvagi",
        "Table Lamp": "Stol chirog'i",
        "Bamboo Spatula": "Bambuk spatula",
        "Black Aluminium Cup": "Qora alyuminiy stakan",
        "Black Whisk": "Qora ko'pirtirgich",
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
    ]

    SAMPLE_PHONES = [
        "+998 90 111 22 33",
        "+998 90 222 33 44",
        "+998 90 333 44 55",
        "+998 90 444 55 66",
        "+998 90 555 66 77",
    ]

    def handle(self, *args, **options):
        sellers = self._get_or_create_sellers()
        product_payloads = self._fetch_products()
        self._clear_existing_sample_data()
        categories = {}

        for index, payload in enumerate(product_payloads):
            seller = sellers[index % len(sellers)]
            category = self._get_or_create_category(categories, payload["category"])
            product = Product.objects.create(
                author=seller,
                category=category,
                title=self._build_uzbek_title(payload),
                description=self._build_uzbek_description(payload),
                price=Decimal(str(payload["price"])),
                address=self.SAMPLE_ADDRESSES[index % len(self.SAMPLE_ADDRESSES)],
                phone_number=self.SAMPLE_PHONES[index % len(self.SAMPLE_PHONES)],
                discount_percent=Decimal(str(payload.get("discountPercentage", 0))).quantize(Decimal("0.01")),
            )
            self._attach_real_images(product, payload)

        total_products = Product.objects.count()
        total_images = ProductImage.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Yangi katalog tayyorlandi. Mahsulotlar: {total_products}. Rasmlar: {total_images}."
            )
        )

    def _fetch_products(self):
        request = Request(self.API_URL, headers={"User-Agent": "mini-online-shop-seeder/1.0"})
        with urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload.get("products", [])

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

    def _clear_existing_sample_data(self):
        sample_images_root = Path(settings.MEDIA_ROOT) / "products"
        if sample_images_root.exists():
            shutil.rmtree(sample_images_root)
        Product.objects.filter(author__username__in=self.SAMPLE_SELLERS).delete()
        Category.objects.filter(product__isnull=True).delete()

    def _get_or_create_category(self, category_cache, category_slug):
        if category_slug in category_cache:
            return category_cache[category_slug]
        category_name = self.CATEGORY_NAMES.get(category_slug, "Mahsulotlar")
        category, _ = Category.objects.get_or_create(name=category_name[:20])
        category_cache[category_slug] = category
        return category

    def _build_uzbek_title(self, payload):
        category_slug = payload["category"]
        source_title = payload["title"]
        translated_title = self.TITLE_TRANSLATIONS.get(source_title)
        if translated_title:
            return translated_title[:150]
        prefix = self.CATEGORY_TITLE_PREFIX.get(category_slug, "Mahsulot")
        brand = payload.get("brand") or ""
        if brand and brand.lower() not in source_title.lower():
            return f"{prefix}: {brand} {source_title}"[:150]
        return f"{prefix}: {source_title}"[:150]

    def _build_uzbek_description(self, payload):
        category_slug = payload["category"]
        template = self.DESCRIPTION_TEMPLATES.get(
            category_slug,
            "{source_title} kundalik foydalanish uchun mo'ljallangan sifatli mahsulot bo'lib, zamonaviy dizayn va qulaylikni taklif etadi.",
        )
        brand = payload.get("brand") or "Ushbu"
        source_title = payload["title"]
        description = template.format(brand=brand, source_title=source_title)
        return (
            f"{description} Ushbu katalog yozuvi o'zbek tilida moslashtirildi va mahsulot suratlari haqiqiy mahsulot fotosuratlaridan olindi."
        )

    def _attach_real_images(self, product, payload):
        image_urls = self._pick_three_image_urls(payload)
        product_dir = Path(settings.MEDIA_ROOT) / "products" / f"product_{product.pk}"
        product_dir.mkdir(parents=True, exist_ok=True)

        for index, image_url in enumerate(image_urls, start=1):
            extension = Path(urlparse(image_url).path).suffix or ".jpg"
            if len(extension) > 5:
                extension = ".jpg"
            relative_path = f"products/product_{product.pk}/image_{index}{extension}"
            full_path = Path(settings.MEDIA_ROOT) / relative_path
            self._download_image(image_url, full_path)
            ProductImage.objects.create(product=product, image=relative_path)

    def _pick_three_image_urls(self, payload):
        raw_urls = list(payload.get("images") or [])
        thumbnail = payload.get("thumbnail")
        if thumbnail:
            raw_urls.append(thumbnail)

        unique_urls = []
        for url in raw_urls:
            if url and url not in unique_urls:
                unique_urls.append(url)

        if not unique_urls:
            raise ValueError(f"Mahsulot uchun rasm topilmadi: {payload['title']}")

        while len(unique_urls) < 3:
            unique_urls.append(unique_urls[-1])

        return unique_urls[:3]

    def _download_image(self, image_url, destination):
        request = Request(image_url, headers={"User-Agent": "mini-online-shop-seeder/1.0"})
        with urlopen(request, timeout=60) as response:
            destination.write_bytes(response.read())
