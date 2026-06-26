"""
Second batch of extended Chinese teas for chinatea.house.
Adds ~40 more famous varieties to grow comparison and ranking surface.
"""

from .tea_data_extended import _tea
from .models import CaffeineLevel, BodyLevel, RoastLevel


ADDITIONAL_TEAS_BATCH2 = [
    # YELLOW TEAS
    _tea(
        "weishan-maojian", "Weishan Maojian", "沩山毛尖", "yellow", "hunan",
        "Yellow tea from Weishan in Hunan. Plump buds yield a rich, sweet, and mellow liquor with a subtle roast.",
        ["sweet", "mellow", "subtle-roast"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.12, tier=2,
    ),

    # WHITE TEAS
    _tea(
        "cangling-baicha", "Cangling Baicha", "苍岭白茶", "white", "zhejiang",
        "White tea from Cangling in Zhejiang. Delicate, floral, and refreshingly sweet with a pale golden liquor.",
        ["floral", "sweet", "delicate"], BodyLevel.LIGHT, CaffeineLevel.LOW,
        oxidation_level=0.08, tier=2,
    ),
    _tea(
        "taimu-shan-baimudan", "Taimu Shan Baimudan", "太姥山白牡丹", "white", "fuding",
        "White Peony from Taimu Mountain in Fuding. Floral, fruity, and honeyed with a fuller body than Silver Needle.",
        ["floral", "fruity", "honey"], BodyLevel.LIGHT_MEDIUM, CaffeineLevel.LOW,
        oxidation_level=0.10, subcategory_id="baimudan", tier=2,
    ),
    _tea(
        "fuding-shoumei", "Fuding Shoumei", "福鼎寿眉", "white", "fuding",
        "Leafy white tea from Fuding with a robust, sweet, and slightly earthy character. Excellent for aging.",
        ["earthy", "sweet", "robust"], BodyLevel.MEDIUM, CaffeineLevel.LOW,
        oxidation_level=0.12, subcategory_id="shoumei", tier=2,
    ),

    # SCENTED TEAS
    _tea(
        "chrysanthemum-puer", "Chrysanthemum Pu'er", "菊花普洱", "scented", "yunnan",
        "Ripe pu'er blended with chrysanthemum flowers. Earthy, cooling, and soothing with a gentle floral lift.",
        ["chrysanthemum", "earth", "cooling"], BodyLevel.MEDIUM, CaffeineLevel.LOW,
        oxidation_level=0.85, subcategory_id="shou", tier=2,
    ),
    _tea(
        "magnolia-oolong", "Magnolia Oolong", "玉兰乌龙", "scented", "fujian",
        "Oolong scented with magnolia flowers. Creamy, floral, and elegant with a lingering fragrance.",
        ["magnolia", "creamy", "floral"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.30, subcategory_id="taiwan-gaoshan", tier=3,
    ),
    _tea(
        "lotus-green-tea", "Lotus Green Tea", "莲花绿茶", "scented", "zhejiang",
        "Green tea scented with lotus flowers. Fresh, floral, and delicately sweet with a clean finish.",
        ["lotus", "fresh", "floral"], BodyLevel.LIGHT, CaffeineLevel.LOW,
        oxidation_level=0.03, tier=3,
    ),

    # DARK TEAS
    _tea(
        "tian-jian", "Tian Jian", "天尖", "dark", "hunan",
        "High-grade Anhua dark tea made from tender buds. Sweet, smooth, and complex with notes of dried fruit.",
        ["dried-fruit", "sweet", "smooth"], BodyLevel.MEDIUM_FULL, CaffeineLevel.MODERATE,
        oxidation_level=0.80, subcategory_id="fu-zhuan", tier=2,
    ),
    _tea(
        "gong-jian", "Gong Jian", "贡尖", "dark", "hunan",
        "Medium-grade Anhua dark tea with a robust, earthy profile and a mellow sweet aftertaste.",
        ["earth", "robust", "mellow"], BodyLevel.FULL, CaffeineLevel.MODERATE,
        oxidation_level=0.82, subcategory_id="fu-zhuan", tier=2,
    ),
    _tea(
        "kangzhuan", "Kang Zhuan", "康砖", "dark", "sichuan",
        "Traditional Tibetan border tea brick. Robust, earthy, and slightly smoky with a thick body.",
        ["earth", "smoke", "robust"], BodyLevel.FULL, CaffeineLevel.MODERATE,
        oxidation_level=0.85, tier=2,
    ),

    # GREEN TEAS
    _tea(
        "wuyuan-mei-cha", "Wuyuan Meicha", "婺源茗眉", "green", "jiangxi",
        "Curved eyebrow-shaped green tea from Wuyuan. Fresh, vegetal, and mildly nutty with a sweet finish.",
        ["vegetal", "nutty", "sweet"], BodyLevel.LIGHT_MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.02, tier=2,
    ),
    _tea(
        "guzhu-zisun", "Guzhu Zisun", "顾渚紫笋", "green", "zhejiang",
        "Purple bamboo shoot green tea from Guzhu. Tender purple-tinged buds with a sweet, floral, and refreshing character.",
        ["floral", "sweet", "refreshing"], BodyLevel.LIGHT, CaffeineLevel.LOW,
        oxidation_level=0.02, tier=2,
    ),
    _tea(
        "gougunao", "Gougunao", "狗牯脑", "green", "jiangxi",
        "Fine green tea from Suichuan in Jiangxi. Tiny twisted leaves produce a bright, brisk, and sweet infusion.",
        ["brisk", "sweet", "bright"], BodyLevel.LIGHT, CaffeineLevel.MODERATE,
        oxidation_level=0.02, tier=2,
    ),
    _tea(
        "jingshan-xiangcha", "Jingshan Xiangcha", "径山茶", "green", "zhejiang",
        "Green tea from Jingshan with a long monastic history. Delicate, sweet, and mildly nutty with a clean finish.",
        ["nutty", "sweet", "delicate"], BodyLevel.LIGHT, CaffeineLevel.LOW,
        oxidation_level=0.02, tier=2,
    ),

    # OOLONG TEAS
    _tea(
        "maoxie", "Mao Xie", "毛蟹", "oolong", "anxi",
        "Anxi oolong known as Hairy Crab. Light, floral, and slightly creamy with a brisk finish.",
        ["floral", "creamy", "brisk"], BodyLevel.LIGHT_MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.25, subcategory_id="tieguanyin", tier=2,
    ),
    _tea(
        "daye-oolong", "Da Ye Oolong", "大叶乌龙", "oolong", "anxi",
        "Large-leaf Anxi oolong with a full, smooth body and a long-lasting floral aroma.",
        ["floral", "smooth", "full"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.30, subcategory_id="tieguanyin", tier=2,
    ),
    _tea(
        "shuixian-shuixian", "Shuixian Shuixian", "水仙水仙", "oolong", "wuyi-mountains",
        "Aged Wuyi Shui Xian with deep woody, mineral, and orchid notes. Smooth and resonant with excellent depth.",
        ["woody", "mineral", "orchid"], BodyLevel.FULL, CaffeineLevel.MODERATE,
        oxidation_level=0.60, subcategory_id="wuyi-yancha", roast_level=RoastLevel.MEDIUM_HEAVY, tier=2,
    ),
    _tea(
        "shuijin-gui", "Shui Jin Gui", "水金龟", "oolong", "wuyi-mountains",
        "Golden Turtle Wuyi yancha. Smooth, mineral, and floral with a sweet, lasting aftertaste.",
        ["mineral", "floral", "sweet"], BodyLevel.MEDIUM_FULL, CaffeineLevel.MODERATE,
        oxidation_level=0.55, subcategory_id="wuyi-yancha", roast_level=RoastLevel.MEDIUM, tier=2,
    ),
    _tea(
        "buzhi-chun", "Bu Zhi Chun", "不知春", "oolong", "wuyi-mountains",
        "Wuyi yancha named after the late-arriving spring. Light, floral, and mineral with a refreshing character.",
        ["floral", "mineral", "refreshing"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.45, subcategory_id="wuyi-yancha", roast_level=RoastLevel.LIGHT, tier=2,
    ),
    _tea(
        "zhangping-shuixian", "Zhangping Shuixian", "漳平水仙", "oolong", "fujian",
        "Compressed square cakes of Fujian Shuixian oolong. Floral, creamy, and smooth with a distinctive pressed shape.",
        ["floral", "creamy", "smooth"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.35, subcategory_id="tieguanyin", tier=2,
    ),
    _tea(
        "baozhong-nantou", "Nantou Baozhong", "南投包种", "oolong", "taiwan",
        "Baozhong-style oolong from Nantou, Taiwan. Light, floral, and silky with a lingering aroma.",
        ["floral", "silky", "light"], BodyLevel.LIGHT_MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.15, subcategory_id="taiwan-gaoshan", tier=2,
    ),
    _tea(
        "ruby-red", "Ruby Red Oolong", "红玉乌龙", "oolong", "taiwan",
        "Taiwanese red oolong from Sun Moon Lake. Honeyed, cinnamon-spiced, and full-bodied with a malty depth.",
        ["honey", "cinnamon", "malty"], BodyLevel.FULL, CaffeineLevel.MODERATE,
        oxidation_level=0.65, subcategory_id="taiwan-gaoshan", tier=2,
    ),
    _tea(
        "qilan-xiang", "Qi Lan Xiang Dancong", "奇兰香单丛", "oolong", "phoenix-mountain",
        "Rare Orchid Fragrance dancong. Elegant, floral, and complex with a long, sweet finish.",
        ["orchid", "floral", "elegant"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.50, subcategory_id="dancong", tier=2,
    ),

    # BLACK TEAS
    _tea(
        "zhenghe-gongfu", "Zhenghe Gongfu", "政和工夫", "black", "fujian",
        "Traditional Fujian black tea from Zhenghe. Smooth, sweet, and slightly floral with a reddish liquor.",
        ["floral", "sweet", "smooth"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.95, tier=2,
    ),
    _tea(
        "sichuan-hongya", "Sichuan Hongya", "四川红芽", "black", "sichuan",
        "Sichuan red tea made from tender buds. Sweet, mellow, and slightly fruity with a clean finish.",
        ["fruity", "sweet", "mellow"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.95, tier=2,
    ),
    _tea(
        "hunan-black", "Hunan Black Tea", "湖南红茶", "black", "hunan",
        "Robust black tea from Hunan. Bold, sweet, and slightly smoky with a thick, warming body.",
        ["sweet", "smoky", "bold"], BodyLevel.FULL, CaffeineLevel.HIGH,
        oxidation_level=0.95, tier=2,
    ),
    _tea(
        "keemun-hongcha", "Keemun Hongcha", "祁门红茶", "black", "qimen",
        "Classic Keemun black tea. Fruity, floral, and wine-like with the signature Keemun sweetness.",
        ["fruit", "floral", "wine"], BodyLevel.MEDIUM, CaffeineLevel.MODERATE,
        oxidation_level=0.95, subcategory_id="keemun", tier=1,
    ),

    # PU'ER TEAS
    _tea(
        "menghai-8582", "Menghai 8582", "勐海8582", "puerh", "menghai",
        "Classic raw pu'er recipe with larger leaves. Balanced, slightly astringent, and excellent for aging.",
        ["balanced", "astringent", "aged"], BodyLevel.MEDIUM_FULL, CaffeineLevel.HIGH,
        oxidation_level=0.12, subcategory_id="sheng", tier=2,
    ),
    _tea(
        "laobanzhang-ripe", "Lao Banzhang Ripe", "老班章熟茶", "puerh", "lincang",
        "Ripe pu'er from Lao Banzhang village. Thick, earthy, and powerful with a sweet, lasting finish.",
        ["earth", "thick", "sweet"], BodyLevel.FULL, CaffeineLevel.MODERATE,
        oxidation_level=0.85, subcategory_id="shou", tier=1,
    ),
    _tea(
        "menghai-raw", "Menghai Raw", "勐海生茶", "puerh", "menghai",
        "Representative raw pu'er from Menghai. Floral, bitter-sweet, and evolving with age.",
        ["floral", "bitter-sweet", "evolving"], BodyLevel.MEDIUM_FULL, CaffeineLevel.HIGH,
        oxidation_level=0.12, subcategory_id="sheng", tier=2,
    ),
    _tea(
        "nuo-xiang", "Nuoxiang Pu'er", "糯香普洱", "puerh", "yunnan",
        "Ripe pu'er with sticky rice fragrance. Sweet, earthy, and comforting with a distinctive aromatic note.",
        ["sticky-rice", "sweet", "earthy"], BodyLevel.FULL, CaffeineLevel.MODERATE,
        oxidation_level=0.85, subcategory_id="shou", tier=2,
    ),
]
