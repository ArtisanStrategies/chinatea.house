"""
Extended Chinese tea database for chinatea.house.

Adds 40 additional famous Chinese tea varieties across all categories to
increase ranking surface area and comparison coverage.
"""

from .models import (
    Tea, BrewingParams, PriceRange,
    CaffeineLevel, BodyLevel, RoastLevel
)


def _tea(
    id: str,
    name_en: str,
    name_zh: str,
    category_id: str,
    region_id: str,
    description_brief: str,
    flavor_primary: list[str],
    body: BodyLevel,
    caffeine_level: CaffeineLevel,
    oxidation_level: float | None = None,
    subcategory_id: str | None = None,
    roast_level: RoastLevel | None = None,
    harvest_season: str = "spring",
    tier: int = 2,
) -> Tea:
    """Compact tea factory with sensible defaults."""

    temp_map = {
        "green": 80,
        "white": 80,
        "yellow": 82,
        "oolong": 95,
        "black": 95,
        "dark": 100,
        "puerh": 98,
        "scented": 85,
    }
    temp = temp_map.get(category_id, 90)
    ratio = 5 if category_id in ("oolong", "puerh", "dark") else 3
    first = 30 if category_id in ("oolong", "puerh", "dark") else 120
    steeps = 7 if category_id in ("oolong", "puerh", "dark") else 3
    rinse = category_id in ("oolong", "puerh", "dark")

    return Tea(
        id=id,
        name_en=name_en,
        name_zh=name_zh,
        category_id=category_id,
        subcategory_id=subcategory_id,
        region_id=region_id,
        oxidation_level=oxidation_level,
        roast_level=roast_level,
        harvest_season=harvest_season,
        caffeine_level=caffeine_level,
        flavor_primary=flavor_primary,
        body=body,
        brewing_gongfu=BrewingParams(
            water_temp_c=temp,
            leaf_ratio_g_per_100ml=ratio,
            first_steep_seconds=first,
            subsequent_steep_seconds=first,
            steep_increment_seconds=5,
            num_steeps=steeps,
            rinse_recommended=rinse,
        ),
        brewing_western=BrewingParams(
            water_temp_c=temp,
            leaf_ratio_g_per_100ml=2,
            first_steep_seconds=180,
            subsequent_steep_seconds=210,
            steep_increment_seconds=30,
            num_steeps=2,
            rinse_recommended=False,
        ),
        price_budget=PriceRange(min_usd_per_50g=8, max_usd_per_50g=18),
        price_mid=PriceRange(min_usd_per_50g=25, max_usd_per_50g=60),
        price_premium=PriceRange(min_usd_per_50g=90, max_usd_per_50g=350),
        description_brief=description_brief,
        tier=tier,
    )


ADDITIONAL_TEAS = [
    # GREEN TEAS
    _tea(
        "shi-feng-longjing", "Shi Feng Longjing", "狮峰龙井", "green", "west-lake",
        "Premium Longjing from Lion Peak, the most prized sub-region of West Lake Hangzhou. Prized for its jade color, flat leaves, and pronounced chestnut sweetness.",
        ["chestnut", "sweet", "orchid"], BodyLevel.LIGHT_MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.02, subcategory_id="longjing", tier=1,
    ),
    _tea(
        "kaihua-longding", "Kaihua Longding", "开化龙顶", "green", "zhejiang",
        "Award-winning green tea from Kaihua County in Zhejiang. Known for its sharp, pine-needle shape, bright green color, and fresh vegetal flavor.",
        ["vegetal", "nutty", "sweet"], BodyLevel.LIGHT_MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.02, tier=2,
    ),
    _tea(
        "jinggang-cuilu", "Jinggang Cuilü", "井冈翠绿", "green", "jiangxi",
        "High-mountain green tea from Jinggangshan. Tender buds yield a bright, grassy infusion with a clean sweet finish.",
        ["grassy", "sweet", "floral"], BodyLevel.LIGHT, CaffeineLevel.MODERATE,
        oxidation_level=0.02, tier=2,
    ),
    _tea(
        "dinggu-dafang", "Dinggu Dafang", "顶谷大方", "green", "anhui",
        "Flat-pressed green tea from Anhui with a roasted chestnut character similar to Longjing but with a fuller body and longer finish.",
        ["chestnut", "roasted", "sweet"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.03, tier=2,
    ),
    _tea(
        "songluo", "Songluo", "松萝茶", "green", "anhui",
        "One of China's oldest named green teas, from Xiuning in Anhui. Tightly rolled pellets with a brisk, slightly astringent, and refreshing profile.",
        ["brisk", "vegetal", "astringent"], BodyLevel.LIGHT_MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.03, tier=2,
    ),
    _tea(
        "yunnan-green", "Yunnan Green", "滇绿", "green", "yunnan",
        "Sun-dried green tea from Yunnan made from large-leaf cultivars. Fuller and sweeter than eastern greens with a noticeable malt backbone.",
        ["malty", "sweet", "grassy"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.03, tier=2,
    ),
    _tea(
        "fujian-baihao", "Fujian Baihao", "福建白毫", "green", "fujian",
        "Fujian silver-needle style green tea with fuzzy white buds. Delicate, sweet, and floral with very little astringency.",
        ["floral", "sweet", "creamy"], BodyLevel.LIGHT, CaffeineLevel.LOW,
        oxidation_level=0.02, tier=2,
    ),
    _tea(
        "tianmu-qingding", "Tianmu Qingding", "天目青顶", "green", "zhejiang",
        "Green tea from Mount Tianmu with plump jade buds. Fresh, nutty, and slightly sweet with a silky mouthfeel.",
        ["nutty", "fresh", "sweet"], BodyLevel.LIGHT_MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.02, tier=2,
    ),
    _tea(
        "wuzhen-green", "Wuzhen Green", "乌镇绿茶", "green", "zhejiang",
        "Local green tea from the water-town region of Wuzhen. Light, refreshing, and mildly floral.",
        ["floral", "light", "refreshing"], BodyLevel.LIGHT, CaffeineLevel.LOW,
        oxidation_level=0.02, tier=3,
    ),

    # OOLONG TEAS
    _tea(
        "tieguanyin-classic", "Tie Guan Yin Classic", "铁观音", "oolong", "anxi",
        "The iconic Anxi oolong named after the Iron Goddess of Mercy. Ranges from fresh floral to deeply roasted; classic versions balance orchid aroma with a creamy body.",
        ["orchid", "creamy", "nutty"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.35, subcategory_id="tieguanyin", tier=1,
    ),
    _tea(
        "huangjin-gui", "Huangjin Gui", "黄金桂", "oolong", "anxi",
        "Fragrant Anxi oolong known as Golden Osmanthus. Light oxidation gives it a bright floral aroma with a sweet, silky liquor.",
        ["osmanthus", "floral", "sweet"], BodyLevel.LIGHT_MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.25, subcategory_id="tieguanyin", tier=2,
    ),
    _tea(
        "benshan", "Ben Shan", "本山", "oolong", "anxi",
        "Traditional Anxi oolong cultivar often compared to Tie Guan Yin. Smooth, floral, and slightly less aromatic than its famous cousin.",
        ["floral", "smooth", "mild"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.30, subcategory_id="tieguanyin", tier=2,
    ),
    _tea(
        "milan-xiang", "Mi Lan Xiang Dancong", "蜜兰香单丛", "oolong", "phoenix-mountain",
        "Honey-orchid fragrance dancong from Phoenix Mountain. Intensely aromatic with honeyed fruit and orchid notes.",
        ["honey", "orchid", "fruit"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.50, subcategory_id="dancong", tier=1,
    ),
    _tea(
        "yashi-xiang", "Ya Shi Xiang Dancong", "鸭屎香单丛", "oolong", "phoenix-mountain",
        "Duck-Shit Fragrance dancong, now one of the most sought-after Phoenix oolongs. Creamy, floral, and intensely aromatic with a long finish.",
        ["creamy", "floral", "long"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.45, subcategory_id="dancong", tier=1,
    ),
    _tea(
        "huang-zhi-xiang", "Huang Zhi Xiang Dancong", "黄枝香单丛", "oolong", "phoenix-mountain",
        "Yellow Branch Fragrance dancong with bright floral and citrus notes. Elegant and complex with a clean finish.",
        ["citrus", "floral", "bright"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.50, subcategory_id="dancong", tier=2,
    ),
    _tea(
        "shan-lin-xi", "Shan Lin Xi", "杉林溪", "oolong", "taiwan",
        "High mountain oolong from Shan Lin Xi, Taiwan. Grown around 1,500m, it is floral, creamy, and remarkably smooth with little astringency.",
        ["floral", "creamy", "smooth"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.20, subcategory_id="taiwan-gaoshan", tier=1,
    ),
    _tea(
        "da-yu-ling", "Da Yu Ling", "大禹岭", "oolong", "taiwan",
        "One of Taiwan's highest elevation oolongs, grown above 2,000m. Exceptionally clean, floral, and sweet with a cooling finish.",
        ["floral", "sweet", "cooling"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.18, subcategory_id="taiwan-gaoshan", tier=1,
    ),
    _tea(
        "baozhong", "Wenshan Baozhong", "文山包种", "oolong", "taiwan",
        "Lightly oxidized twisted-leaf oolong from northern Taiwan. Fresh, floral, and silky with a lingering orchid aroma.",
        ["floral", "silky", "fresh"], BodyLevel.LIGHT_MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.15, subcategory_id="taiwan-gaoshan", tier=2,
    ),

    # BLACK TEAS
    _tea(
        "keemun-haoya", "Keemun Hao Ya", "祁门毫芽", "black", "qimen",
        "Premium grade Keemun made from tender buds. Wine-like, fruity, and floral with the signature Keemun sweetness and little astringency.",
        ["wine", "fruit", "floral"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.95, subcategory_id="keemun", tier=1,
    ),
    _tea(
        "keemun-maofeng", "Keemun Maofeng", "祁门毛峰", "black", "qimen",
        "Keemun made in a green-tea style with twisted leaves. Bright, floral, and slightly lighter than standard Keemun.",
        ["floral", "bright", "malt"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.95, subcategory_id="keemun", tier=2,
    ),
    _tea(
        "dianhong-gold-needle", "Dianhong Gold Needle", "滇红金针", "black", "yunnan",
        "Yunnan black tea made entirely of golden buds. Rich, malty, and honey-sweet with a thick, velvety body.",
        ["malt", "honey", "velvet"], BodyLevel.FULL, CaffeineLevel.HIGH,
        oxidation_level=0.95, subcategory_id="dianhong", tier=1,
    ),
    _tea(
        "yunnan-pure-bud", "Yunnan Pure Bud", "滇红金芽", "black", "yunnan",
        "Golden-bud Yunnan black tea with a mellow, sweet profile and notes of dried fruit and cocoa.",
        ["cocoa", "dried-fruit", "sweet"], BodyLevel.FULL, CaffeineLevel.HIGH,
        oxidation_level=0.95, subcategory_id="dianhong", tier=2,
    ),
    _tea(
        "yin-jun-mei", "Yin Jun Mei", "银骏眉", "black", "wuyi-mountains",
        "Silver Eyebrow black tea made from bud-and-leaf sets. Similar to Jin Jun Mei but more affordable, with a sweet, fruity character.",
        ["fruit", "sweet", "malt"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.95, subcategory_id="zhengshan-xiaozhong", tier=2,
    ),
    _tea(
        "tan-yang-gongfu", "Tan Yang Gongfu", "坦洋工夫", "black", "fujian",
        "Historic Fujian black tea from Tanyang. Smooth and sweet with a gentle fruity aroma and a clean finish.",
        ["fruit", "sweet", "smooth"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.95, tier=2,
    ),
    _tea(
        "bailin-gongfu", "Bailin Gongfu", "白琳工夫", "black", "fujian",
        "Traditional Fujian black tea from Bailin. Delicate, floral, and slightly sweet with a reddish-gold liquor.",
        ["floral", "sweet", "delicate"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.95, tier=2,
    ),
    _tea(
        "yingde-hong", "Yingde Hong", "英德红茶", "black", "guangdong",
        "Robust black tea from Yingde in Guangdong. Bold, malty, and excellent with milk or as a breakfast tea.",
        ["malt", "bold", "robust"], BodyLevel.FULL, CaffeineLevel.HIGH,
        oxidation_level=0.95, tier=2,
    ),

    # WHITE TEAS
    _tea(
        "gong-mei", "Gong Mei", "贡眉", "white", "fuding",
        "White tea made from larger leaves and fewer buds than Shou Mei. Earthy, sweet, and commonly aged for deeper flavor.",
        ["earthy", "sweet", "mellow"], BodyLevel.MEDIUM, CaffeineLevel.LOW,
        oxidation_level=0.10, subcategory_id="shoumei", tier=2,
    ),
    _tea(
        "yue-guang-bai", "Yue Guang Bai", "月光白", "white", "yunnan",
        "Moonlight White from Yunnan, made from large-leaf cultivars. Sweet, fruity, and remarkably smooth with a distinctive two-tone leaf appearance.",
        ["fruit", "sweet", "smooth"], BodyLevel.MEDIUM, CaffeineLevel.LOW,
        oxidation_level=0.12, tier=2,
    ),

    # PU'ER TEAS
    _tea(
        "menghai-7542", "Menghai 7542", "勐海7542", "puerh", "menghai",
        "Classic raw pu'er recipe from Menghai Tea Factory. Balanced, slightly bitter, and excellent for aging with notes of apricot and camphor.",
        ["apricot", "camphor", "bitter"], BodyLevel.MEDIUM_FULL, CaffeineLevel.HIGH,
        oxidation_level=0.10, subcategory_id="sheng", tier=1,
    ),
    _tea(
        "menghai-7572", "Menghai 7572", "勐海7572", "puerh", "menghai",
        "Classic ripe pu'er recipe from Menghai Tea Factory. Smooth, earthy, and reliable with notes of dark cocoa and wet forest.",
        ["cocoa", "earth", "smooth"], BodyLevel.FULL, CaffeineLevel.MODERATE,
        oxidation_level=0.85, subcategory_id="shou", tier=1,
    ),
    _tea(
        "yiwu-gushu", "Yiwu Gushu", "易武古树", "puerh", "yiwu",
        "Old-tree sheng pu'er from Yiwu. Elegant, floral, and honey-sweet with a soft, silky texture and long aftertaste.",
        ["honey", "floral", "silky"], BodyLevel.MEDIUM_FULL, CaffeineLevel.HIGH,
        oxidation_level=0.12, subcategory_id="sheng", tier=1,
    ),
    _tea(
        "jingmai-gushu", "Jingmai Gushu", "景迈古树", "puerh", "xishuangbanna",
        "Old-tree tea from Jingmai Mountain. Floral and honeyed with a distinctive orchid aroma and lingering sweetness.",
        ["orchid", "honey", "floral"], BodyLevel.MEDIUM_FULL, CaffeineLevel.HIGH,
        oxidation_level=0.12, subcategory_id="sheng", tier=1,
    ),
    _tea(
        "bingdao-sheng", "Bingdao Sheng", "冰岛生茶", "puerh", "lincang",
        "Prized sheng pu'er from Bingdao village. Intensely sweet, cooling, and floral with a thick body and long finish.",
        ["sweet", "floral", "cooling"], BodyLevel.FULL, CaffeineLevel.HIGH,
        oxidation_level=0.10, subcategory_id="sheng", tier=1,
    ),
    _tea(
        "xigui-sheng", "Xigui Sheng", "昔归生茶", "puerh", "lincang",
        "Sheng pu'er from Xigui in Lincang. Bold, fragrant, and slightly astringent with a powerful sweet aftertaste.",
        ["fragrant", "bold", "sweet"], BodyLevel.FULL, CaffeineLevel.HIGH,
        oxidation_level=0.12, subcategory_id="sheng", tier=2,
    ),

    # DARK TEAS
    _tea(
        "anhua-dark", "Anhua Dark Tea", "安化黑茶", "dark", "hunan",
        "Heicha from Anhua in Hunan province. Earthy, sweet, and smooth with notes of dried jujube and aged wood.",
        ["earth", "jujube", "wood"], BodyLevel.FULL, CaffeineLevel.LOW,
        oxidation_level=0.80, subcategory_id="fu-zhuan", tier=2,
    ),
    _tea(
        "qianliang-cha", "Qianliang Cha", "千两茶", "dark", "hunan",
        "Thousand Tael Tea - a massive column of compressed Anhua dark tea. Aged, woody, and sweet with a deep reddish-brown liquor.",
        ["woody", "sweet", "aged"], BodyLevel.FULL, CaffeineLevel.MODERATE,
        oxidation_level=0.80, subcategory_id="fu-zhuan", tier=2,
    ),
    _tea(
        "sichuan-biancha", "Sichuan Bian Cha", "四川边茶", "dark", "sichuan",
        "Border tea historically traded to Tibet. Robust, earthy, and slightly smoky with a thick, warming body.",
        ["earth", "smoke", "robust"], BodyLevel.FULL, CaffeineLevel.MODERATE,
        oxidation_level=0.85, tier=2,
    ),
    _tea(
        "hubei-qingzhuan", "Hubei Qing Zhuan", "湖北青砖", "dark", "hubei",
        "Green brick tea from Hubei, traditionally compressed for transport. Mellow, earthy, and slightly sweet.",
        ["earth", "mellow", "sweet"], BodyLevel.MEDIUM_FULL, CaffeineLevel.LOW,
        oxidation_level=0.75, tier=2,
    ),

    # SCENTED TEAS
    _tea(
        "jasmine-dragon-pearls", "Jasmine Dragon Pearls", "茉莉龙珠", "scented", "fujian",
        "Hand-rolled jasmine tea pearls that unfurl as they steep. Intensely fragrant, sweet, and soothing with a clean finish.",
        ["jasmine", "sweet", "soothing"], BodyLevel.LIGHT_MEDIUM, CaffeineLevel.LOW,
        oxidation_level=0.05, subcategory_id="jasmine", tier=1,
    ),
    _tea(
        "jasmine-snow-buds", "Jasmine Snow Buds", "茉莉雪芽", "scented", "fujian",
        "Delicate jasmine-scented white tea buds. Light, floral, and naturally sweet with a creamy mouthfeel.",
        ["jasmine", "creamy", "light"], BodyLevel.LIGHT, CaffeineLevel.LOW,
        oxidation_level=0.05, subcategory_id="jasmine", tier=2,
    ),
    _tea(
        "osmanthus-oolong", "Osmanthus Oolong", "桂花乌龙", "scented", "guangdong",
        "Oolong scented with osmanthus flowers. The toasty oolong base is lifted by sweet, fruity osmanthus fragrance.",
        ["osmanthus", "toasty", "fruity"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.30, subcategory_id="osmanthus", tier=2,
    ),
]
