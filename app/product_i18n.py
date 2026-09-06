"""Translations for the seeded Uzbek national dishes, keyed by their canonical
(Uzbek) product name as stored in the database.

Admin-added products that aren't in this table simply show their original
(Uzbek) name/description in every language — there's no automatic translation
for free-text admin input.
"""

PRODUCT_EMOJI = {
    "O'zbek Palovi": "🍚",
    "Manti": "🥟",
    "Lag'mon": "🍜",
    "Somsa": "🥧",
    "Shashlik": "🍢",
    "Chuchvara": "🍲",
}

PRODUCT_TRANSLATIONS = {
    "O'zbek Palovi": {
        "uz": ("O'zbek Palovi", "Guruch, mol go'shti, sabzi va piyoz bilan tayyorlangan O'zbekistonning milliy taomi"),
        "ko": ("우즈벡 팔로프 (오쉬)", "쌀, 소고기, 당근과 양파로 만든 우즈베키스탄의 국민 요리"),
        "en": ("Uzbek Plov (Osh)", "Uzbekistan's national dish — rice cooked with beef, carrots, and onions"),
        "ru": ("Узбекский плов (Ош)", "Национальное блюдо Узбекистана — рис с говядиной, морковью и луком"),
    },
    "Manti": {
        "uz": ("Manti", "Bug'da pishirilgan, qiymali xamir cho'ntaklari"),
        "ko": ("만티 (우즈벡 만두)", "다진 고기를 넣어 찐 우즈베키스탄식 만두"),
        "en": ("Manti (Steamed Dumplings)", "Steamed dumplings filled with seasoned minced meat"),
        "ru": ("Манты", "Паровые пельмени с начинкой из рубленого мяса"),
    },
    "Lag'mon": {
        "uz": ("Lag'mon", "Qo'lda cho'zilgan lag'mon, mol go'shti va sabzavotlar bilan"),
        "ko": ("라그몬 (수타면 볶음)", "손으로 뽑은 면과 소고기, 채소를 볶은 요리"),
        "en": ("Lagman (Hand-Pulled Noodles)", "Hand-pulled noodles stir-fried with beef and vegetables"),
        "ru": ("Лагман", "Домашняя лапша с говядиной и овощами"),
    },
    "Somsa": {
        "uz": ("Somsa", "Tandirda pishirilgan, qiymali xamir pirogi"),
        "ko": ("솜사 (화덕 만두빵)", "화덕에서 구운 다진 고기가 들어간 페이스트리"),
        "en": ("Somsa (Baked Pastry)", "Tandoor-baked pastry filled with spiced minced meat"),
        "ru": ("Самса", "Слоёное тесто с мясной начинкой, запечённое в тандыре"),
    },
    "Shashlik": {
        "uz": ("Shashlik", "Cho'g'da pishirilgan mol go'shti shashligi"),
        "ko": ("샤슬릭 (숯불 꼬치구이)", "숯불에 구운 소고기 꼬치"),
        "en": ("Shashlik (Grilled Skewers)", "Charcoal-grilled beef skewers"),
        "ru": ("Шашлык", "Шашлык из говядины, приготовленный на углях"),
    },
    "Chuchvara": {
        "uz": ("Chuchvara", "Mayda go'shtli chuchvara, issiq sho'rvada"),
        "ko": ("추치바라 (우즈벡 물만두)", "따뜻한 육수에 담긴 작은 고기 만두"),
        "en": ("Chuchvara (Dumpling Soup)", "Small meat dumplings served in a warm broth"),
        "ru": ("Чучвара", "Маленькие мясные пельмени в горячем бульоне"),
    },
}


def localized_product(name: str, description: str, lang: str) -> tuple[str, str]:
    entry = PRODUCT_TRANSLATIONS.get(name)
    if entry is None:
        return name, description
    return entry.get(lang, entry["uz"])


def product_emoji(name: str) -> str:
    return PRODUCT_EMOJI.get(name, "🍽️")
