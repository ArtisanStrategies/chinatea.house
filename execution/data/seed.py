"""
Seed data for chinatea.house database.

Populates initial categories, regions, and core teas.
"""

from typing import TYPE_CHECKING

from .models import (
    Category, Subcategory, Region, Tea, Occasion, Teaware, BrewingMethod,
    TeaCategory, RegionType, RoastLevel, CaffeineLevel, BodyLevel,
    TeawareType, BrewingParams, PriceRange
)

if TYPE_CHECKING:
    from .db import Database


def seed_database(db: "Database") -> dict:
    """Seed the database with initial data."""
    counts = {}

    counts["categories"] = _seed_categories(db)
    counts["subcategories"] = _seed_subcategories(db)
    counts["regions"] = _seed_regions(db)
    counts["occasions"] = _seed_occasions(db)
    counts["teaware"] = _seed_teaware(db)
    counts["brewing_methods"] = _seed_brewing_methods(db)
    counts["teas"] = _seed_teas(db)

    return counts


def _seed_categories(db: "Database") -> int:
    """Seed the 7 main tea categories."""
    categories = [
        Category(
            id="green",
            name_en="Green Tea",
            name_zh="绿茶",
            description="Green tea is minimally oxidized, preserving the fresh, vegetal character of the tea leaves. The leaves are quickly heated after picking to halt oxidation, resulting in a light, refreshing flavor profile with notes ranging from grassy and marine to nutty and sweet. Green tea is the most produced tea in China, with famous varieties including Longjing (Dragon Well), Biluochun, and Huangshan Maofeng.",
            oxidation_range_min=0.0,
            oxidation_range_max=0.05,
            color_hex="#90B77D"
        ),
        Category(
            id="white",
            name_en="White Tea",
            name_zh="白茶",
            description="White tea undergoes minimal processing with no rolling or shaping, allowing the leaves to wither and dry naturally. This gentle approach preserves the tea's delicate, subtle flavors with notes of honey, melon, and hay. The most famous white teas come from Fujian province, including Bai Hao Yin Zhen (Silver Needle) and Bai Mudan (White Peony). White tea is known for its high antioxidant content and aging potential.",
            oxidation_range_min=0.05,
            oxidation_range_max=0.15,
            color_hex="#F5E6CC"
        ),
        Category(
            id="yellow",
            name_en="Yellow Tea",
            name_zh="黄茶",
            description="Yellow tea is the rarest of the six main tea categories, produced through a unique 'sealed yellowing' process that gives it a mellower, less grassy flavor than green tea. The leaves undergo a slow oxidation under damp cloth or paper, developing a distinctive yellow hue and smooth, sweet character. Famous yellow teas include Junshan Yinzhen and Huoshan Huangya. Production is limited due to the labor-intensive process.",
            oxidation_range_min=0.05,
            oxidation_range_max=0.20,
            color_hex="#F0E68C"
        ),
        Category(
            id="oolong",
            name_en="Oolong Tea",
            name_zh="乌龙茶",
            description="Oolong tea spans a wide oxidation range from 15% to 85%, creating remarkable diversity from light, floral teas to dark, roasted varieties. The leaves are bruised to initiate oxidation, then heated to halt it at the desired level. Famous oolongs include Tie Guan Yin, Da Hong Pao, Dancong, and Taiwanese high mountain oolongs. Oolong is prized for its complex flavors and excellent re-steeping potential.",
            oxidation_range_min=0.15,
            oxidation_range_max=0.85,
            color_hex="#DAA520"
        ),
        Category(
            id="black",
            name_en="Black Tea",
            name_zh="红茶",
            description="Black tea (called 'red tea' in Chinese for its reddish liquor) is fully oxidized, resulting in bold, robust flavors with notes of malt, honey, cocoa, and dried fruit. Chinese black teas are generally more nuanced than their Indian counterparts, with famous varieties including Keemun, Dianhong (Yunnan Gold), and Lapsang Souchong. Black tea was developed in the 17th century in Fujian's Wuyi Mountains.",
            oxidation_range_min=0.85,
            oxidation_range_max=1.0,
            color_hex="#8B4513"
        ),
        Category(
            id="dark",
            name_en="Dark Tea",
            name_zh="黑茶",
            description="Dark tea, including pu-erh, undergoes microbial fermentation after oxidation, developing earthy, smooth, and complex flavors that improve with age. Sheng (raw) pu-erh ferments slowly over decades, while shou (ripe) pu-erh uses accelerated fermentation. Other dark teas include Liu Bao and Fu Zhuan. Dark tea is often compressed into cakes, bricks, or other shapes for aging and is prized by collectors.",
            oxidation_range_min=0.0,
            oxidation_range_max=1.0,
            color_hex="#3D2914"
        ),
        Category(
            id="scented",
            name_en="Scented Tea",
            name_zh="花茶",
            description="Scented teas are created by layering tea leaves with fresh flowers, allowing the tea to absorb the floral aroma naturally. Jasmine tea is the most famous, traditionally using green tea as a base, though white and oolong bases are also used. Other scented teas include osmanthus, rose, and chrysanthemum varieties. High-quality jasmine tea may be scented seven or more times to achieve intense fragrance.",
            oxidation_range_min=0.0,
            oxidation_range_max=0.85,
            color_hex="#E8D5E0"
        ),
    ]

    for cat in categories:
        try:
            db.insert_category(cat)
        except Exception:
            pass  # Already exists

    return len(categories)


def _seed_subcategories(db: "Database") -> int:
    """Seed tea subcategories."""
    subcategories = [
        # Green tea subcategories
        Subcategory(id="longjing", category_id="green", name_en="Longjing (Dragon Well)", name_zh="龙井",
                   description="Pan-fired green tea from Hangzhou known for its flat, smooth leaves and chestnut flavor."),
        Subcategory(id="biluochun", category_id="green", name_en="Biluochun", name_zh="碧螺春",
                   description="Spiral-shaped green tea from Jiangsu with fruity, floral notes."),
        Subcategory(id="maofeng", category_id="green", name_en="Maofeng", name_zh="毛峰",
                   description="Downy tip green teas, most famously from Huangshan."),
        Subcategory(id="gunpowder", category_id="green", name_en="Gunpowder", name_zh="珠茶",
                   description="Tightly rolled green tea pellets, primarily for export."),

        # Oolong subcategories
        Subcategory(id="tieguanyin", category_id="oolong", name_en="Tie Guan Yin", name_zh="铁观音",
                   description="Famous Anxi oolong with orchid aroma, ranging from light to heavily roasted."),
        Subcategory(id="wuyi-yancha", category_id="oolong", name_en="Wuyi Rock Tea", name_zh="武夷岩茶",
                   description="Mineral-rich oolongs from Wuyi Mountains, including Da Hong Pao."),
        Subcategory(id="dancong", category_id="oolong", name_en="Phoenix Dancong", name_zh="凤凰单丛",
                   description="Single-bush oolongs from Guangdong with distinct varietal fragrances."),
        Subcategory(id="taiwan-gaoshan", category_id="oolong", name_en="Taiwan High Mountain", name_zh="台湾高山茶",
                   description="Light, floral oolongs grown above 1000m in Taiwan."),

        # Black tea subcategories
        Subcategory(id="keemun", category_id="black", name_en="Keemun", name_zh="祁门红茶",
                   description="Anhui black tea known for wine-like aroma and smooth finish."),
        Subcategory(id="dianhong", category_id="black", name_en="Yunnan Black", name_zh="滇红",
                   description="Golden-tipped Yunnan black teas with malty, honeyed notes."),
        Subcategory(id="zhengshan-xiaozhong", category_id="black", name_en="Zhengshan Xiaozhong", name_zh="正山小种",
                   description="Original Lapsang Souchong from Wuyi, traditionally pine-smoked."),

        # Dark tea subcategories
        Subcategory(id="sheng-puerh", category_id="dark", name_en="Sheng Pu-erh (Raw)", name_zh="生普洱",
                   description="Naturally aged pu-erh that evolves over decades."),
        Subcategory(id="shou-puerh", category_id="dark", name_en="Shou Pu-erh (Ripe)", name_zh="熟普洱",
                   description="Accelerated fermentation pu-erh with earthy, smooth character."),
        Subcategory(id="liu-bao", category_id="dark", name_en="Liu Bao", name_zh="六堡茶",
                   description="Guangxi dark tea with betel nut aroma."),

        # White tea subcategories
        Subcategory(id="yinzhen", category_id="white", name_en="Bai Hao Yin Zhen", name_zh="白毫银针",
                   description="Silver Needle - buds only, the highest grade white tea."),
        Subcategory(id="baimudan", category_id="white", name_en="Bai Mudan", name_zh="白牡丹",
                   description="White Peony - buds with two leaves attached."),
        Subcategory(id="shoumei", category_id="white", name_en="Shou Mei", name_zh="寿眉",
                   description="Mature leaves, often aged for deeper flavor."),

        # Scented tea subcategories
        Subcategory(id="jasmine", category_id="scented", name_en="Jasmine Tea", name_zh="茉莉花茶",
                   description="Green or white tea scented with jasmine blossoms."),
        Subcategory(id="osmanthus", category_id="scented", name_en="Osmanthus Tea", name_zh="桂花茶",
                   description="Tea scented with sweet osmanthus flowers."),
    ]

    for sub in subcategories:
        try:
            db.insert_subcategory(sub)
        except Exception:
            pass

    return len(subcategories)


def _seed_regions(db: "Database") -> int:
    """Seed geographic regions."""
    regions = [
        # Root
        Region(id="china", parent_id=None, name_en="China", name_zh="中国",
               region_type=RegionType.COUNTRY),

        # Major tea provinces
        Region(id="fujian", parent_id="china", name_en="Fujian", name_zh="福建",
               name_pinyin="Fújiàn", region_type=RegionType.PROVINCE,
               terroir_notes="Subtropical climate, mountainous terrain. Birthplace of oolong, white, and black tea."),
        Region(id="zhejiang", parent_id="china", name_en="Zhejiang", name_zh="浙江",
               name_pinyin="Zhèjiāng", region_type=RegionType.PROVINCE,
               terroir_notes="Mild climate with abundant rainfall. Famous for Longjing and other green teas."),
        Region(id="yunnan", parent_id="china", name_en="Yunnan", name_zh="云南",
               name_pinyin="Yúnnán", region_type=RegionType.PROVINCE,
               terroir_notes="Diverse terrain from tropical to alpine. Ancient tea trees and pu-erh origin."),
        Region(id="anhui", parent_id="china", name_en="Anhui", name_zh="安徽",
               name_pinyin="Ānhuī", region_type=RegionType.PROVINCE,
               terroir_notes="Mountain ranges with misty climate. Home to Keemun and Huangshan teas."),
        Region(id="jiangsu", parent_id="china", name_en="Jiangsu", name_zh="江苏",
               name_pinyin="Jiāngsū", region_type=RegionType.PROVINCE,
               terroir_notes="Temperate climate near Tai Lake. Famous for Biluochun."),
        Region(id="guangdong", parent_id="china", name_en="Guangdong", name_zh="广东",
               name_pinyin="Guǎngdōng", region_type=RegionType.PROVINCE,
               terroir_notes="Subtropical climate. Home to Phoenix Mountain dancong oolongs."),
        Region(id="sichuan", parent_id="china", name_en="Sichuan", name_zh="四川",
               name_pinyin="Sìchuān", region_type=RegionType.PROVINCE,
               terroir_notes="Basin climate with high humidity. Ancient tea cultivation region."),
        Region(id="hunan", parent_id="china", name_en="Hunan", name_zh="湖南",
               name_pinyin="Húnán", region_type=RegionType.PROVINCE,
               terroir_notes="Subtropical monsoon climate. Known for yellow tea and dark tea."),
        Region(id="jiangxi", parent_id="china", name_en="Jiangxi", name_zh="江西",
               name_pinyin="Jiāngxī", region_type=RegionType.PROVINCE,
               terroir_notes="Hilly terrain with mild climate. Historical tea production area."),
        Region(id="taiwan", parent_id="china", name_en="Taiwan", name_zh="台湾",
               name_pinyin="Táiwān", region_type=RegionType.PROVINCE,
               terroir_notes="Mountainous island with varied microclimates. Famous for high mountain oolongs."),
        Region(id="guangxi", parent_id="china", name_en="Guangxi", name_zh="广西",
               name_pinyin="Guǎngxī", region_type=RegionType.PROVINCE,
               terroir_notes="Subtropical karst landscape. Origin of Liu Bao dark tea."),
        Region(id="guizhou", parent_id="china", name_en="Guizhou", name_zh="贵州",
               name_pinyin="Guìzhōu", region_type=RegionType.PROVINCE,
               terroir_notes="High plateau with cool, misty climate. Emerging quality tea region."),
        Region(id="henan", parent_id="china", name_en="Henan", name_zh="河南",
               name_pinyin="Hénán", region_type=RegionType.PROVINCE,
               terroir_notes="Continental climate. Home to Xinyang Maojian green tea."),
        Region(id="hubei", parent_id="china", name_en="Hubei", name_zh="湖北",
               name_pinyin="Húběi", region_type=RegionType.PROVINCE,
               terroir_notes="Central China with varied terrain. Historical tea trading center."),

        # Fujian sub-regions
        Region(id="wuyi-mountains", parent_id="fujian", name_en="Wuyi Mountains", name_zh="武夷山",
               name_pinyin="Wǔyíshān", region_type=RegionType.MOUNTAIN,
               elevation_min_m=200, elevation_max_m=2158,
               terroir_notes="UNESCO site with unique mineral-rich soil. Origin of rock oolongs and Lapsang Souchong."),
        Region(id="anxi", parent_id="fujian", name_en="Anxi County", name_zh="安溪",
               name_pinyin="Ānxī", region_type=RegionType.COUNTY,
               terroir_notes="Subtropical highland climate. Origin of Tie Guan Yin oolong."),
        Region(id="fuding", parent_id="fujian", name_en="Fuding", name_zh="福鼎",
               name_pinyin="Fúdǐng", region_type=RegionType.COUNTY,
               terroir_notes="Coastal mountain area. Origin of Fuding white tea."),
        Region(id="zhenghe", parent_id="fujian", name_en="Zhenghe", name_zh="政和",
               name_pinyin="Zhènghé", region_type=RegionType.COUNTY,
               terroir_notes="Mountainous inland county. Origin of Zhenghe white tea."),

        # Zhejiang sub-regions
        Region(id="hangzhou", parent_id="zhejiang", name_en="Hangzhou", name_zh="杭州",
               name_pinyin="Hángzhōu", region_type=RegionType.PREFECTURE,
               terroir_notes="West Lake area with mild, humid climate. Home of Longjing."),
        Region(id="west-lake", parent_id="hangzhou", name_en="West Lake", name_zh="西湖",
               name_pinyin="Xīhú", region_type=RegionType.COUNTY,
               elevation_min_m=50, elevation_max_m=300,
               terroir_notes="Protected origin for authentic Xi Hu Longjing."),
        Region(id="anji", parent_id="zhejiang", name_en="Anji County", name_zh="安吉",
               name_pinyin="Ānjí", region_type=RegionType.COUNTY,
               terroir_notes="Bamboo forests with cool climate. Origin of Anji Bai Cha."),

        # Yunnan sub-regions
        Region(id="xishuangbanna", parent_id="yunnan", name_en="Xishuangbanna", name_zh="西双版纳",
               name_pinyin="Xīshuāngbǎnnà", region_type=RegionType.PREFECTURE,
               terroir_notes="Tropical climate with ancient tea forests. Major pu-erh region."),
        Region(id="lincang", parent_id="yunnan", name_en="Lincang", name_zh="临沧",
               name_pinyin="Líncāng", region_type=RegionType.PREFECTURE,
               terroir_notes="Highland area with ancient tea trees. Includes Mengku and Bingdao."),
        Region(id="puerh-city", parent_id="yunnan", name_en="Pu'er City", name_zh="普洱市",
               name_pinyin="Pǔ'ěr", region_type=RegionType.PREFECTURE,
               terroir_notes="Historical trading hub for pu-erh tea. Diverse microclimates."),
        Region(id="menghai", parent_id="xishuangbanna", name_en="Menghai", name_zh="勐海",
               name_pinyin="Měnghǎi", region_type=RegionType.COUNTY,
               terroir_notes="Famous for Banzhang and Nannuo mountain teas."),
        Region(id="yiwu", parent_id="xishuangbanna", name_en="Yiwu", name_zh="易武",
               name_pinyin="Yìwǔ", region_type=RegionType.COUNTY,
               terroir_notes="Ancient tea trade route. Known for soft, elegant pu-erh."),

        # Anhui sub-regions
        Region(id="huangshan", parent_id="anhui", name_en="Huangshan", name_zh="黄山",
               name_pinyin="Huángshān", region_type=RegionType.PREFECTURE,
               elevation_min_m=400, elevation_max_m=1864,
               terroir_notes="Misty mountains with dramatic peaks. UNESCO World Heritage site."),
        Region(id="qimen", parent_id="anhui", name_en="Qimen County", name_zh="祁门",
               name_pinyin="Qímén", region_type=RegionType.COUNTY,
               terroir_notes="Birthplace of Keemun black tea. Humid, forested hills."),

        # Jiangsu sub-regions
        Region(id="suzhou", parent_id="jiangsu", name_en="Suzhou", name_zh="苏州",
               name_pinyin="Sūzhōu", region_type=RegionType.PREFECTURE,
               terroir_notes="Tai Lake region. Home of Biluochun."),
        Region(id="dongting", parent_id="suzhou", name_en="Dongting Mountain", name_zh="洞庭山",
               name_pinyin="Dòngtíngshān", region_type=RegionType.MOUNTAIN,
               terroir_notes="Island in Tai Lake. Protected origin for Biluochun."),

        # Guangdong sub-regions
        Region(id="chaozhou", parent_id="guangdong", name_en="Chaozhou", name_zh="潮州",
               name_pinyin="Cháozhōu", region_type=RegionType.PREFECTURE,
               terroir_notes="Gongfu tea culture heartland. Home to Phoenix Mountain."),
        Region(id="phoenix-mountain", parent_id="chaozhou", name_en="Phoenix Mountain", name_zh="凤凰山",
               name_pinyin="Fènghuángshān", region_type=RegionType.MOUNTAIN,
               elevation_min_m=400, elevation_max_m=1497,
               terroir_notes="Ancient single-bush dancong oolongs. Unique varietal diversity."),

        # Taiwan sub-regions
        Region(id="alishan", parent_id="taiwan", name_en="Alishan", name_zh="阿里山",
               name_pinyin="Ālǐshān", region_type=RegionType.MOUNTAIN,
               elevation_min_m=1000, elevation_max_m=2663,
               terroir_notes="High altitude with cool temperatures. Famous high mountain oolong."),
        Region(id="lishan", parent_id="taiwan", name_en="Lishan", name_zh="梨山",
               name_pinyin="Líshān", region_type=RegionType.MOUNTAIN,
               elevation_min_m=1800, elevation_max_m=2500,
               terroir_notes="Highest elevation tea in Taiwan. Premium oolong production."),
        Region(id="dong-ding", parent_id="taiwan", name_en="Dong Ding", name_zh="冻顶",
               name_pinyin="Dòngdǐng", region_type=RegionType.MOUNTAIN,
               terroir_notes="Traditional roasted oolong origin. Lower elevation Nantou area."),

        # Hunan sub-regions
        Region(id="junshan", parent_id="hunan", name_en="Junshan Island", name_zh="君山",
               name_pinyin="Jūnshān", region_type=RegionType.COUNTY,
               terroir_notes="Island in Dongting Lake. Origin of Junshan Yinzhen yellow tea."),

        # Sichuan sub-regions
        Region(id="emeishan", parent_id="sichuan", name_en="Mount Emei", name_zh="峨眉山",
               name_pinyin="Éméishān", region_type=RegionType.MOUNTAIN,
               elevation_min_m=500, elevation_max_m=3099,
               terroir_notes="Sacred Buddhist mountain. Ancient tea cultivation site."),
        Region(id="mengding", parent_id="sichuan", name_en="Mengding Mountain", name_zh="蒙顶山",
               name_pinyin="Méngdǐngshān", region_type=RegionType.MOUNTAIN,
               terroir_notes="Claimed birthplace of cultivated tea. Yellow tea production."),
    ]

    for region in regions:
        try:
            db.insert_region(region)
        except Exception:
            pass

    return len(regions)


def _seed_occasions(db: "Database") -> int:
    """Seed tea drinking occasions."""
    occasions = [
        Occasion(
            id="morning-energy",
            name="Morning Energy",
            description="Teas to start the day with sustained energy and mental clarity.",
            preferred_categories=["black", "oolong", "dark"],
            preferred_attributes={"caffeine_level": ["moderate", "high"]},
            time_of_day="morning"
        ),
        Occasion(
            id="afternoon-focus",
            name="Afternoon Focus",
            description="Teas for maintaining concentration during work or study.",
            preferred_categories=["green", "oolong"],
            preferred_attributes={"caffeine_level": ["moderate"]},
            time_of_day="afternoon"
        ),
        Occasion(
            id="evening-relaxation",
            name="Evening Relaxation",
            description="Calming teas for winding down without disrupting sleep.",
            preferred_categories=["white", "dark"],
            preferred_attributes={"caffeine_level": ["low", "very-low"]},
            time_of_day="evening"
        ),
        Occasion(
            id="meditation",
            name="Meditation & Mindfulness",
            description="Teas that promote calm, focused awareness.",
            preferred_categories=["white", "green", "oolong"],
            preferred_attributes={"body": ["light", "light-medium"]},
            time_of_day=None
        ),
        Occasion(
            id="digestion",
            name="After Meal Digestion",
            description="Teas traditionally enjoyed after heavy meals to aid digestion.",
            preferred_categories=["dark", "oolong"],
            preferred_attributes={},
            time_of_day=None
        ),
        Occasion(
            id="guests",
            name="Hosting Guests",
            description="Impressive teas for sharing with visitors.",
            preferred_categories=["oolong", "white", "green"],
            preferred_attributes={"tier": [1, 2]},
            time_of_day=None
        ),
        Occasion(
            id="summer-cooling",
            name="Summer Cooling",
            description="Refreshing teas to cool down in hot weather.",
            preferred_categories=["green", "white"],
            preferred_attributes={},
            season="summer"
        ),
        Occasion(
            id="winter-warming",
            name="Winter Warming",
            description="Robust teas to warm up during cold months.",
            preferred_categories=["black", "dark", "oolong"],
            preferred_attributes={"roast_level": ["medium", "heavy"]},
            season="winter"
        ),
        Occasion(
            id="daily-drinking",
            name="Daily Drinking",
            description="Reliable, affordable teas for everyday enjoyment.",
            preferred_categories=["green", "black", "oolong"],
            preferred_attributes={"tier": [2, 3]},
            time_of_day=None
        ),
        Occasion(
            id="special-occasion",
            name="Special Occasions",
            description="Premium teas for celebrations and important moments.",
            preferred_categories=["oolong", "white", "dark"],
            preferred_attributes={"tier": [1]},
            time_of_day=None
        ),
    ]

    for occasion in occasions:
        try:
            db.insert_occasion(occasion)
        except Exception:
            pass

    return len(occasions)


def _seed_teaware(db: "Database") -> int:
    """Seed teaware items."""
    teaware_items = [
        Teaware(
            id="yixing-teapot",
            name_en="Yixing Clay Teapot",
            name_zh="宜兴紫砂壶",
            teaware_type=TeawareType.TEAPOT,
            materials=["zisha clay", "purple clay"],
            origin_region_id="jiangsu",
            description="Unglazed clay teapots from Yixing that absorb tea oils over time, developing a unique patina. Best dedicated to a single tea type. Renowned for enhancing the flavor of oolong and dark teas.",
            best_for_categories=["oolong", "dark", "black"],
            care_instructions="Rinse with hot water only, never soap. Allow to dry completely between uses."
        ),
        Teaware(
            id="gaiwan",
            name_en="Gaiwan",
            name_zh="盖碗",
            teaware_type=TeawareType.GAIWAN,
            materials=["porcelain", "glass", "clay"],
            description="Three-piece lidded bowl consisting of saucer, bowl, and lid. Versatile brewing vessel suitable for all tea types. Allows direct observation of leaves and precise control over steeping.",
            best_for_categories=["green", "white", "oolong", "black", "dark"],
            care_instructions="Porcelain gaiwans can be washed with mild soap. Handle carefully when hot."
        ),
        Teaware(
            id="glass-teapot",
            name_en="Glass Teapot",
            name_zh="玻璃壶",
            teaware_type=TeawareType.TEAPOT,
            materials=["borosilicate glass"],
            description="Heat-resistant glass teapot ideal for watching leaves unfurl. Does not retain flavors between sessions. Perfect for showcasing beautiful whole-leaf teas.",
            best_for_categories=["green", "white", "scented"],
            care_instructions="Allow to cool before washing. Avoid thermal shock."
        ),
        Teaware(
            id="cha-hai",
            name_en="Cha Hai (Fairness Pitcher)",
            name_zh="茶海",
            teaware_type=TeawareType.PITCHER,
            materials=["glass", "porcelain", "clay"],
            description="Decanting pitcher used to ensure even distribution of tea strength. Essential for gongfu brewing to prevent over-steeping while serving multiple cups.",
            best_for_categories=["oolong", "dark", "black", "green"],
            care_instructions="Clean after each session to prevent buildup."
        ),
        Teaware(
            id="gongfu-cups",
            name_en="Gongfu Tasting Cups",
            name_zh="品茗杯",
            teaware_type=TeawareType.CUP,
            materials=["porcelain", "clay", "glass"],
            description="Small cups (30-50ml) designed for savoring tea in small sips. Often paired with aroma cups for appreciating fragrance before taste.",
            best_for_categories=["oolong", "dark", "black"],
            care_instructions="Warm before use. Clean thoroughly between different teas."
        ),
        Teaware(
            id="bamboo-tea-tray",
            name_en="Bamboo Tea Tray",
            name_zh="茶盘",
            teaware_type=TeawareType.TRAY,
            materials=["bamboo", "wood"],
            description="Drainage tray that catches overflow and rinse water during gongfu brewing. Creates a dedicated workspace for the tea ceremony.",
            best_for_categories=["oolong", "dark", "black"],
            care_instructions="Dry thoroughly after use. Oil periodically to prevent cracking."
        ),
        Teaware(
            id="variable-kettle",
            name_en="Variable Temperature Kettle",
            name_zh="变温电水壶",
            teaware_type=TeawareType.KETTLE,
            materials=["stainless steel", "glass"],
            description="Electric kettle with precise temperature control. Essential for brewing delicate teas that require lower temperatures.",
            best_for_categories=["green", "white", "yellow"],
            care_instructions="Descale regularly. Use filtered water for best results."
        ),
        Teaware(
            id="tetsubin",
            name_en="Cast Iron Tetsubin",
            name_zh="铁壶",
            teaware_type=TeawareType.KETTLE,
            materials=["cast iron"],
            origin_region_id=None,
            description="Traditional cast iron kettle that adds trace minerals to water and retains heat well. Originally Japanese but widely used in Chinese tea culture.",
            best_for_categories=["dark", "black", "oolong"],
            care_instructions="Dry immediately after use to prevent rust. Never use soap."
        ),
    ]

    for item in teaware_items:
        try:
            db.insert_teaware(item)
        except Exception:
            pass

    return len(teaware_items)


def _seed_brewing_methods(db: "Database") -> int:
    """Seed brewing methods."""
    # This would be implemented with db.insert_brewing_method
    # Keeping stub for now
    return 0


def _seed_teas(db: "Database") -> int:
    """Seed initial tea data."""
    teas = [
        # =====================================================================
        # TIER 1 - Famous teas with complete data
        # =====================================================================

        # Green Teas
        Tea(
            id="xi-hu-longjing",
            name_en="Xi Hu Longjing (Dragon Well)",
            name_zh="西湖龙井",
            name_pinyin="Xīhú Lóngjǐng",
            category_id="green",
            subcategory_id="longjing",
            region_id="west-lake",
            oxidation_level=0.02,
            harvest_season="spring",
            cultivar="Longjing #43",
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["chestnut", "vegetal", "sweet"],
            flavor_secondary=["orchid", "butter", "grass"],
            aroma=["toasted", "floral", "fresh"],
            body=BodyLevel.LIGHT_MEDIUM,
            finish="Sweet, lingering",
            mouthfeel="Silky, coating",
            brewing_gongfu=BrewingParams(
                water_temp_c=80, water_temp_f=176,
                leaf_ratio_g_per_100ml=4,
                first_steep_seconds=30,
                subsequent_steep_seconds=20,
                steep_increment_seconds=5,
                num_steeps=5,
                rinse_recommended=False
            ),
            brewing_western=BrewingParams(
                water_temp_c=80, water_temp_f=176,
                leaf_ratio_g_per_100ml=2,
                first_steep_seconds=120,
                subsequent_steep_seconds=150,
                steep_increment_seconds=30,
                num_steeps=3,
                rinse_recommended=False
            ),
            price_budget=PriceRange(min_usd_per_50g=8, max_usd_per_50g=15),
            price_mid=PriceRange(min_usd_per_50g=20, max_usd_per_50g=50),
            price_premium=PriceRange(min_usd_per_50g=80, max_usd_per_50g=300),
            best_for=["morning-energy", "afternoon-focus", "guests"],
            similar_tea_ids=["biluochun", "anji-bai-cha"],
            description_brief="China's most famous green tea, prized for its flat, smooth leaves and distinctive chestnut flavor. Authentic Xi Hu Longjing comes only from the West Lake area of Hangzhou and is hand-pan-fired to halt oxidation.",
            tier=1
        ),

        Tea(
            id="biluochun",
            name_en="Biluochun (Green Snail Spring)",
            name_zh="碧螺春",
            name_pinyin="Bìluóchūn",
            category_id="green",
            subcategory_id="biluochun",
            region_id="dongting",
            oxidation_level=0.02,
            harvest_season="spring",
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["fruity", "floral", "fresh"],
            flavor_secondary=["apricot", "honey", "vegetal"],
            aroma=["floral", "fruity", "fresh"],
            body=BodyLevel.LIGHT,
            finish="Clean, sweet",
            mouthfeel="Delicate, refreshing",
            brewing_gongfu=BrewingParams(
                water_temp_c=75, water_temp_f=167,
                leaf_ratio_g_per_100ml=4,
                first_steep_seconds=25,
                subsequent_steep_seconds=20,
                steep_increment_seconds=5,
                num_steeps=4,
                rinse_recommended=False
            ),
            brewing_western=BrewingParams(
                water_temp_c=75, water_temp_f=167,
                leaf_ratio_g_per_100ml=2,
                first_steep_seconds=90,
                subsequent_steep_seconds=120,
                steep_increment_seconds=30,
                num_steeps=3,
                rinse_recommended=False
            ),
            price_budget=PriceRange(min_usd_per_50g=10, max_usd_per_50g=20),
            price_mid=PriceRange(min_usd_per_50g=25, max_usd_per_50g=60),
            price_premium=PriceRange(min_usd_per_50g=80, max_usd_per_50g=200),
            best_for=["morning-energy", "summer-cooling", "guests"],
            similar_tea_ids=["xi-hu-longjing", "anji-bai-cha"],
            description_brief="Prized spring green tea from Dongting Mountain near Tai Lake, known for its tightly curled spiral shape resembling snail shells. Grown among fruit trees, it absorbs natural fruity sweetness with delicate floral notes.",
            tier=1
        ),

        Tea(
            id="huangshan-maofeng",
            name_en="Huangshan Maofeng",
            name_zh="黄山毛峰",
            name_pinyin="Huángshān Máofēng",
            category_id="green",
            subcategory_id="maofeng",
            region_id="huangshan",
            oxidation_level=0.02,
            harvest_season="spring",
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["orchid", "chestnut", "sweet"],
            flavor_secondary=["apricot", "grass", "mineral"],
            aroma=["floral", "fresh", "misty"],
            body=BodyLevel.LIGHT_MEDIUM,
            finish="Smooth, lingering sweetness",
            mouthfeel="Velvety, clean",
            brewing_gongfu=BrewingParams(
                water_temp_c=80, water_temp_f=176,
                leaf_ratio_g_per_100ml=4,
                first_steep_seconds=30,
                subsequent_steep_seconds=25,
                steep_increment_seconds=5,
                num_steeps=5,
                rinse_recommended=False
            ),
            brewing_western=BrewingParams(
                water_temp_c=80, water_temp_f=176,
                leaf_ratio_g_per_100ml=2,
                first_steep_seconds=120,
                subsequent_steep_seconds=150,
                steep_increment_seconds=30,
                num_steeps=3,
                rinse_recommended=False
            ),
            price_budget=PriceRange(min_usd_per_50g=6, max_usd_per_50g=12),
            price_mid=PriceRange(min_usd_per_50g=15, max_usd_per_50g=40),
            price_premium=PriceRange(min_usd_per_50g=60, max_usd_per_50g=150),
            best_for=["morning-energy", "meditation", "daily-drinking"],
            similar_tea_ids=["xi-hu-longjing", "taiping-houkui"],
            description_brief="Premium green tea from the misty peaks of Huangshan (Yellow Mountain) in Anhui province. Named for its downy white tips (maofeng means 'fur peak'), it produces a delicate orchid-like fragrance with sweet, lasting flavor.",
            tier=1
        ),

        # Oolong Teas
        Tea(
            id="da-hong-pao",
            name_en="Da Hong Pao (Big Red Robe)",
            name_zh="大红袍",
            name_pinyin="Dà Hóng Páo",
            category_id="oolong",
            subcategory_id="wuyi-yancha",
            region_id="wuyi-mountains",
            oxidation_level=0.65,
            roast_level=RoastLevel.MEDIUM_HEAVY,
            harvest_season="spring",
            cultivar="Da Hong Pao",
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["mineral", "roasted", "dark chocolate"],
            flavor_secondary=["dried fruit", "cinnamon", "honey"],
            aroma=["roasted", "mineral", "orchid"],
            body=BodyLevel.FULL,
            finish="Long, warming, mineral",
            mouthfeel="Thick, coating, smooth",
            brewing_gongfu=BrewingParams(
                water_temp_c=95, water_temp_f=203,
                leaf_ratio_g_per_100ml=7,
                first_steep_seconds=15,
                subsequent_steep_seconds=10,
                steep_increment_seconds=5,
                num_steeps=8,
                rinse_recommended=True
            ),
            brewing_western=BrewingParams(
                water_temp_c=95, water_temp_f=203,
                leaf_ratio_g_per_100ml=3,
                first_steep_seconds=180,
                subsequent_steep_seconds=240,
                steep_increment_seconds=60,
                num_steeps=4,
                rinse_recommended=True
            ),
            price_budget=PriceRange(min_usd_per_50g=15, max_usd_per_50g=30),
            price_mid=PriceRange(min_usd_per_50g=40, max_usd_per_50g=100),
            price_premium=PriceRange(min_usd_per_50g=150, max_usd_per_50g=500),
            best_for=["guests", "evening-relaxation", "digestion", "winter-warming"],
            similar_tea_ids=["rou-gui", "shui-xian", "tie-luo-han"],
            description_brief="The king of Wuyi rock oolongs, legendary for the original mother trees that produced tea worth more than gold. Modern Da Hong Pao captures the essence of yancha: deep mineral character from the rocky terroir, balanced roast, and extraordinary complexity.",
            tier=1
        ),

        Tea(
            id="tie-guan-yin",
            name_en="Tie Guan Yin (Iron Goddess of Mercy)",
            name_zh="铁观音",
            name_pinyin="Tiě Guānyīn",
            category_id="oolong",
            subcategory_id="tieguanyin",
            region_id="anxi",
            oxidation_level=0.25,
            roast_level=RoastLevel.LIGHT,
            harvest_season="spring",
            cultivar="Tie Guan Yin",
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["orchid", "butter", "sweet"],
            flavor_secondary=["cream", "lily", "honey"],
            aroma=["orchid", "gardenia", "fresh"],
            body=BodyLevel.MEDIUM,
            finish="Creamy, floral, lingering",
            mouthfeel="Silky, full",
            brewing_gongfu=BrewingParams(
                water_temp_c=90, water_temp_f=194,
                leaf_ratio_g_per_100ml=7,
                first_steep_seconds=20,
                subsequent_steep_seconds=15,
                steep_increment_seconds=5,
                num_steeps=7,
                rinse_recommended=True
            ),
            brewing_western=BrewingParams(
                water_temp_c=90, water_temp_f=194,
                leaf_ratio_g_per_100ml=3,
                first_steep_seconds=150,
                subsequent_steep_seconds=180,
                steep_increment_seconds=30,
                num_steeps=4,
                rinse_recommended=True
            ),
            price_budget=PriceRange(min_usd_per_50g=8, max_usd_per_50g=15),
            price_mid=PriceRange(min_usd_per_50g=20, max_usd_per_50g=50),
            price_premium=PriceRange(min_usd_per_50g=70, max_usd_per_50g=200),
            best_for=["afternoon-focus", "guests", "daily-drinking"],
            similar_tea_ids=["alishan-oolong", "dong-ding", "huang-jin-gui"],
            description_brief="China's most popular oolong, named after the Buddhist bodhisattva Guanyin. Modern Anxi Tie Guan Yin is typically lightly oxidized, showcasing intense orchid fragrance and creamy texture with a distinctively sweet finish.",
            tier=1
        ),

        Tea(
            id="fenghuang-dancong",
            name_en="Phoenix Dancong",
            name_zh="凤凰单丛",
            name_pinyin="Fènghuáng Dāncóng",
            category_id="oolong",
            subcategory_id="dancong",
            region_id="phoenix-mountain",
            oxidation_level=0.50,
            roast_level=RoastLevel.MEDIUM,
            harvest_season="spring",
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["honey orchid", "stone fruit", "floral"],
            flavor_secondary=["honey", "peach", "almond"],
            aroma=["orchid", "honey", "gardenia"],
            body=BodyLevel.MEDIUM_FULL,
            finish="Complex, perfumed, lasting",
            mouthfeel="Silky, layered",
            brewing_gongfu=BrewingParams(
                water_temp_c=95, water_temp_f=203,
                leaf_ratio_g_per_100ml=8,
                first_steep_seconds=10,
                subsequent_steep_seconds=8,
                steep_increment_seconds=3,
                num_steeps=10,
                rinse_recommended=True
            ),
            brewing_western=BrewingParams(
                water_temp_c=90, water_temp_f=194,
                leaf_ratio_g_per_100ml=3,
                first_steep_seconds=180,
                subsequent_steep_seconds=210,
                steep_increment_seconds=30,
                num_steeps=4,
                rinse_recommended=True
            ),
            price_budget=PriceRange(min_usd_per_50g=12, max_usd_per_50g=25),
            price_mid=PriceRange(min_usd_per_50g=35, max_usd_per_50g=80),
            price_premium=PriceRange(min_usd_per_50g=100, max_usd_per_50g=400),
            best_for=["afternoon-focus", "guests", "meditation"],
            similar_tea_ids=["mi-lan-xiang", "ya-shi-xiang", "tie-guan-yin"],
            description_brief="Single-bush oolongs from Phoenix Mountain in Guangdong, each tree producing leaves with unique aromatic profiles. Mi Lan Xiang (Honey Orchid) is the most famous variety, offering intense natural fragrance that mimics specific flowers or fruits.",
            tier=1
        ),

        # White Teas
        Tea(
            id="bai-hao-yinzhen",
            name_en="Bai Hao Yin Zhen (Silver Needle)",
            name_zh="白毫银针",
            name_pinyin="Báiháo Yínzhēn",
            category_id="white",
            subcategory_id="yinzhen",
            region_id="fuding",
            oxidation_level=0.08,
            harvest_season="spring",
            cultivar="Da Bai",
            caffeine_level=CaffeineLevel.LOW,
            flavor_primary=["melon", "honey", "hay"],
            flavor_secondary=["cucumber", "straw", "vanilla"],
            aroma=["fresh", "honey", "subtle floral"],
            body=BodyLevel.LIGHT,
            finish="Clean, sweet, refreshing",
            mouthfeel="Silky, delicate",
            brewing_gongfu=BrewingParams(
                water_temp_c=80, water_temp_f=176,
                leaf_ratio_g_per_100ml=5,
                first_steep_seconds=45,
                subsequent_steep_seconds=30,
                steep_increment_seconds=10,
                num_steeps=6,
                rinse_recommended=False
            ),
            brewing_western=BrewingParams(
                water_temp_c=80, water_temp_f=176,
                leaf_ratio_g_per_100ml=3,
                first_steep_seconds=180,
                subsequent_steep_seconds=240,
                steep_increment_seconds=60,
                num_steeps=3,
                rinse_recommended=False
            ),
            price_budget=PriceRange(min_usd_per_50g=15, max_usd_per_50g=25),
            price_mid=PriceRange(min_usd_per_50g=35, max_usd_per_50g=70),
            price_premium=PriceRange(min_usd_per_50g=100, max_usd_per_50g=300),
            best_for=["evening-relaxation", "meditation", "summer-cooling"],
            similar_tea_ids=["bai-mudan", "shoumei"],
            description_brief="The highest grade of white tea, made exclusively from unopened buds covered in silvery-white down. From Fuding in Fujian province, this delicate tea offers subtle sweetness with notes of melon, hay, and honey.",
            tier=1
        ),

        Tea(
            id="bai-mudan",
            name_en="Bai Mudan (White Peony)",
            name_zh="白牡丹",
            name_pinyin="Bái Mǔdān",
            category_id="white",
            subcategory_id="baimudan",
            region_id="fuding",
            oxidation_level=0.10,
            harvest_season="spring",
            cultivar="Da Bai",
            caffeine_level=CaffeineLevel.LOW,
            flavor_primary=["floral", "honey", "hay"],
            flavor_secondary=["peony", "melon", "grass"],
            aroma=["floral", "fresh", "sweet"],
            body=BodyLevel.LIGHT_MEDIUM,
            finish="Sweet, clean, refreshing",
            mouthfeel="Smooth, fuller than Silver Needle",
            brewing_gongfu=BrewingParams(
                water_temp_c=85, water_temp_f=185,
                leaf_ratio_g_per_100ml=5,
                first_steep_seconds=40,
                subsequent_steep_seconds=30,
                steep_increment_seconds=10,
                num_steeps=5,
                rinse_recommended=False
            ),
            brewing_western=BrewingParams(
                water_temp_c=85, water_temp_f=185,
                leaf_ratio_g_per_100ml=3,
                first_steep_seconds=180,
                subsequent_steep_seconds=210,
                steep_increment_seconds=30,
                num_steeps=3,
                rinse_recommended=False
            ),
            price_budget=PriceRange(min_usd_per_50g=8, max_usd_per_50g=15),
            price_mid=PriceRange(min_usd_per_50g=20, max_usd_per_50g=45),
            price_premium=PriceRange(min_usd_per_50g=60, max_usd_per_50g=150),
            best_for=["evening-relaxation", "meditation", "daily-drinking"],
            similar_tea_ids=["bai-hao-yinzhen", "shoumei", "gongmei"],
            description_brief="White tea featuring one bud and two leaves, offering more body and complexity than Silver Needle at a more accessible price. Named for its resemblance to peony flowers when the leaves unfurl in water.",
            tier=1
        ),

        # Black Teas
        Tea(
            id="qimen-hongcha",
            name_en="Keemun (Qimen Black Tea)",
            name_zh="祁门红茶",
            name_pinyin="Qímén Hóngchá",
            category_id="black",
            subcategory_id="keemun",
            region_id="qimen",
            oxidation_level=0.95,
            harvest_season="spring",
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["wine", "cocoa", "malt"],
            flavor_secondary=["orchid", "stone fruit", "pine"],
            aroma=["wine-like", "smoky", "floral"],
            body=BodyLevel.MEDIUM,
            finish="Smooth, slightly smoky, lingering",
            mouthfeel="Velvety, refined",
            brewing_gongfu=BrewingParams(
                water_temp_c=90, water_temp_f=194,
                leaf_ratio_g_per_100ml=5,
                first_steep_seconds=20,
                subsequent_steep_seconds=15,
                steep_increment_seconds=5,
                num_steeps=6,
                rinse_recommended=False
            ),
            brewing_western=BrewingParams(
                water_temp_c=90, water_temp_f=194,
                leaf_ratio_g_per_100ml=2.5,
                first_steep_seconds=180,
                subsequent_steep_seconds=210,
                steep_increment_seconds=30,
                num_steeps=3,
                rinse_recommended=False
            ),
            price_budget=PriceRange(min_usd_per_50g=8, max_usd_per_50g=15),
            price_mid=PriceRange(min_usd_per_50g=20, max_usd_per_50g=50),
            price_premium=PriceRange(min_usd_per_50g=70, max_usd_per_50g=200),
            best_for=["morning-energy", "afternoon-focus", "daily-drinking"],
            similar_tea_ids=["dianhong", "zhengshan-xiaozhong", "jin-jun-mei"],
            description_brief="The 'Burgundy of teas,' Keemun is prized for its wine-like aroma and smooth, complex flavor. Created in 1875 in Anhui province, it became a key component of English Breakfast blends and remains one of China's most celebrated black teas.",
            tier=1
        ),

        Tea(
            id="dianhong-gongfu",
            name_en="Yunnan Gold (Dianhong)",
            name_zh="滇红工夫",
            name_pinyin="Diānhóng Gōngfū",
            category_id="black",
            subcategory_id="dianhong",
            region_id="yunnan",
            oxidation_level=0.95,
            harvest_season="spring",
            cultivar="Yunnan large-leaf",
            caffeine_level=CaffeineLevel.HIGH,
            flavor_primary=["malt", "honey", "cocoa"],
            flavor_secondary=["pepper", "dried fruit", "caramel"],
            aroma=["malty", "honey", "sweet"],
            body=BodyLevel.FULL,
            finish="Sweet, honeyed, long",
            mouthfeel="Thick, smooth, coating",
            brewing_gongfu=BrewingParams(
                water_temp_c=90, water_temp_f=194,
                leaf_ratio_g_per_100ml=5,
                first_steep_seconds=15,
                subsequent_steep_seconds=10,
                steep_increment_seconds=5,
                num_steeps=6,
                rinse_recommended=False
            ),
            brewing_western=BrewingParams(
                water_temp_c=90, water_temp_f=194,
                leaf_ratio_g_per_100ml=2.5,
                first_steep_seconds=180,
                subsequent_steep_seconds=210,
                steep_increment_seconds=30,
                num_steeps=3,
                rinse_recommended=False
            ),
            price_budget=PriceRange(min_usd_per_50g=8, max_usd_per_50g=15),
            price_mid=PriceRange(min_usd_per_50g=20, max_usd_per_50g=45),
            price_premium=PriceRange(min_usd_per_50g=60, max_usd_per_50g=150),
            best_for=["morning-energy", "winter-warming", "daily-drinking"],
            similar_tea_ids=["qimen-hongcha", "jin-jun-mei", "zhengshan-xiaozhong"],
            description_brief="Robust black tea from Yunnan made with large-leaf varietals, displaying abundant golden tips. Known for its bold malty sweetness, honeyed character, and lack of astringency even when brewed strong.",
            tier=1
        ),

        # Dark Teas
        Tea(
            id="menghai-shou-puerh",
            name_en="Menghai Shou Pu-erh",
            name_zh="勐海熟普洱",
            name_pinyin="Měnghǎi Shú Pǔ'ěr",
            category_id="dark",
            subcategory_id="shou-puerh",
            region_id="menghai",
            oxidation_level=1.0,
            is_aged=True,
            age_years=5,
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["earth", "wood", "leather"],
            flavor_secondary=["dates", "mushroom", "chocolate"],
            aroma=["earthy", "aged", "sweet"],
            body=BodyLevel.FULL,
            finish="Smooth, warming, lingering",
            mouthfeel="Thick, velvety, coating",
            brewing_gongfu=BrewingParams(
                water_temp_c=100, water_temp_f=212,
                leaf_ratio_g_per_100ml=7,
                first_steep_seconds=10,
                subsequent_steep_seconds=8,
                steep_increment_seconds=3,
                num_steeps=15,
                rinse_recommended=True
            ),
            brewing_western=BrewingParams(
                water_temp_c=100, water_temp_f=212,
                leaf_ratio_g_per_100ml=3,
                first_steep_seconds=180,
                subsequent_steep_seconds=240,
                steep_increment_seconds=60,
                num_steeps=5,
                rinse_recommended=True
            ),
            price_budget=PriceRange(min_usd_per_50g=5, max_usd_per_50g=12),
            price_mid=PriceRange(min_usd_per_50g=15, max_usd_per_50g=40),
            price_premium=PriceRange(min_usd_per_50g=50, max_usd_per_50g=150),
            best_for=["digestion", "evening-relaxation", "winter-warming"],
            similar_tea_ids=["yiwu-sheng-puerh", "lincang-puerh", "liu-bao"],
            description_brief="Ripe pu-erh from the renowned Menghai region, processed using accelerated fermentation (wo dui) to achieve aged characteristics. Offers smooth, earthy complexity with notes of forest floor, dates, and dark chocolate.",
            tier=1
        ),

        Tea(
            id="yiwu-sheng-puerh",
            name_en="Yiwu Sheng Pu-erh",
            name_zh="易武生普洱",
            name_pinyin="Yìwǔ Shēng Pǔ'ěr",
            category_id="dark",
            subcategory_id="sheng-puerh",
            region_id="yiwu",
            oxidation_level=0.15,
            is_aged=True,
            age_years=10,
            caffeine_level=CaffeineLevel.HIGH,
            flavor_primary=["honey", "floral", "apricot"],
            flavor_secondary=["camphor", "mineral", "leather"],
            aroma=["floral", "honey", "aged wood"],
            body=BodyLevel.MEDIUM_FULL,
            finish="Long, complex, evolving",
            mouthfeel="Silky, coating, huigan (returning sweetness)",
            brewing_gongfu=BrewingParams(
                water_temp_c=95, water_temp_f=203,
                leaf_ratio_g_per_100ml=7,
                first_steep_seconds=15,
                subsequent_steep_seconds=10,
                steep_increment_seconds=5,
                num_steeps=15,
                rinse_recommended=True
            ),
            brewing_western=BrewingParams(
                water_temp_c=95, water_temp_f=203,
                leaf_ratio_g_per_100ml=3,
                first_steep_seconds=180,
                subsequent_steep_seconds=210,
                steep_increment_seconds=30,
                num_steeps=5,
                rinse_recommended=True
            ),
            price_budget=PriceRange(min_usd_per_50g=15, max_usd_per_50g=30),
            price_mid=PriceRange(min_usd_per_50g=40, max_usd_per_50g=100),
            price_premium=PriceRange(min_usd_per_50g=150, max_usd_per_50g=1000),
            best_for=["special-occasion", "afternoon-focus", "meditation"],
            similar_tea_ids=["menghai-shou-puerh", "lincang-puerh", "banzhang"],
            description_brief="Raw pu-erh from the historic Yiwu tea region, known for producing elegant, aromatic sheng that ages gracefully. Yiwu teas are characterized by their honey sweetness, floral notes, and silky mouthfeel.",
            tier=1
        ),

        # Scented Tea
        Tea(
            id="jasmine-dragon-pearl",
            name_en="Jasmine Dragon Pearl",
            name_zh="茉莉龙珠",
            name_pinyin="Mòlì Lóngzhū",
            category_id="scented",
            subcategory_id="jasmine",
            region_id="fujian",
            oxidation_level=0.02,
            harvest_season="spring",
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["jasmine", "floral", "sweet"],
            flavor_secondary=["honey", "vegetal", "cream"],
            aroma=["jasmine", "gardenia", "fresh"],
            body=BodyLevel.LIGHT_MEDIUM,
            finish="Sweet, floral, clean",
            mouthfeel="Smooth, coating",
            brewing_gongfu=BrewingParams(
                water_temp_c=85, water_temp_f=185,
                leaf_ratio_g_per_100ml=4,
                first_steep_seconds=30,
                subsequent_steep_seconds=25,
                steep_increment_seconds=5,
                num_steeps=5,
                rinse_recommended=False
            ),
            brewing_western=BrewingParams(
                water_temp_c=85, water_temp_f=185,
                leaf_ratio_g_per_100ml=2,
                first_steep_seconds=150,
                subsequent_steep_seconds=180,
                steep_increment_seconds=30,
                num_steeps=3,
                rinse_recommended=False
            ),
            price_budget=PriceRange(min_usd_per_50g=8, max_usd_per_50g=15),
            price_mid=PriceRange(min_usd_per_50g=20, max_usd_per_50g=45),
            price_premium=PriceRange(min_usd_per_50g=60, max_usd_per_50g=120),
            best_for=["afternoon-focus", "guests", "daily-drinking"],
            similar_tea_ids=["jasmine-yin-hao", "osmanthus-oolong"],
            description_brief="Hand-rolled green tea pearls scented with fresh jasmine blossoms over multiple nights. Watch the pearls unfurl to release intense floral fragrance that perfectly balances the underlying tea's sweet, vegetal character.",
            tier=1
        ),

        # =====================================================================
        # TIER 2 - Well-known teas with good data
        # =====================================================================

        Tea(
            id="anji-bai-cha",
            name_en="Anji Bai Cha",
            name_zh="安吉白茶",
            name_pinyin="Ānjí Báichá",
            category_id="green",
            region_id="anji",
            oxidation_level=0.02,
            harvest_season="spring",
            caffeine_level=CaffeineLevel.LOW,
            flavor_primary=["umami", "chestnut", "bamboo"],
            flavor_secondary=["sweet", "grassy"],
            aroma=["fresh", "bamboo", "subtle"],
            body=BodyLevel.LIGHT,
            finish="Sweet, refreshing",
            brewing_gongfu=BrewingParams(
                water_temp_c=80, water_temp_f=176,
                leaf_ratio_g_per_100ml=4,
                first_steep_seconds=30,
                subsequent_steep_seconds=25,
                steep_increment_seconds=5,
                num_steeps=4,
                rinse_recommended=False
            ),
            price_mid=PriceRange(min_usd_per_50g=20, max_usd_per_50g=50),
            best_for=["morning-energy", "summer-cooling"],
            similar_tea_ids=["xi-hu-longjing", "biluochun"],
            description_brief="A unique green tea (not white, despite the name) from Anji county known for its pale color and high amino acid content. The albino cultivar produces exceptionally umami-rich, sweet tea with low astringency.",
            tier=2
        ),

        Tea(
            id="rou-gui",
            name_en="Rou Gui (Cinnamon)",
            name_zh="肉桂",
            name_pinyin="Ròu Guì",
            category_id="oolong",
            subcategory_id="wuyi-yancha",
            region_id="wuyi-mountains",
            oxidation_level=0.60,
            roast_level=RoastLevel.MEDIUM_HEAVY,
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["cinnamon", "mineral", "floral"],
            flavor_secondary=["spice", "cream", "dark fruit"],
            aroma=["cinnamon", "roasted", "floral"],
            body=BodyLevel.FULL,
            finish="Warming, spicy, long",
            brewing_gongfu=BrewingParams(
                water_temp_c=95, water_temp_f=203,
                leaf_ratio_g_per_100ml=7,
                first_steep_seconds=15,
                subsequent_steep_seconds=10,
                steep_increment_seconds=5,
                num_steeps=8,
                rinse_recommended=True
            ),
            price_mid=PriceRange(min_usd_per_50g=30, max_usd_per_50g=80),
            best_for=["winter-warming", "digestion"],
            similar_tea_ids=["da-hong-pao", "shui-xian"],
            description_brief="Popular Wuyi rock oolong known for its distinctive cinnamon-like aroma and spicy character. Often blended with Shui Xian to create balanced yancha.",
            tier=2
        ),

        Tea(
            id="shui-xian",
            name_en="Shui Xian (Water Sprite)",
            name_zh="水仙",
            name_pinyin="Shuǐ Xiān",
            category_id="oolong",
            subcategory_id="wuyi-yancha",
            region_id="wuyi-mountains",
            oxidation_level=0.55,
            roast_level=RoastLevel.MEDIUM,
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["orchid", "mineral", "honey"],
            flavor_secondary=["dark chocolate", "wood"],
            aroma=["floral", "mineral", "aged"],
            body=BodyLevel.MEDIUM_FULL,
            finish="Smooth, sweet, mineral",
            brewing_gongfu=BrewingParams(
                water_temp_c=95, water_temp_f=203,
                leaf_ratio_g_per_100ml=7,
                first_steep_seconds=15,
                subsequent_steep_seconds=10,
                steep_increment_seconds=5,
                num_steeps=7,
                rinse_recommended=True
            ),
            price_mid=PriceRange(min_usd_per_50g=25, max_usd_per_50g=60),
            best_for=["afternoon-focus", "guests"],
            similar_tea_ids=["da-hong-pao", "rou-gui"],
            description_brief="Ancient Wuyi cultivar producing smooth, orchid-scented rock oolong. Often aged, developing deeper complexity over time.",
            tier=2
        ),

        Tea(
            id="alishan-oolong",
            name_en="Alishan High Mountain Oolong",
            name_zh="阿里山乌龙",
            name_pinyin="Ālǐshān Wūlóng",
            category_id="oolong",
            subcategory_id="taiwan-gaoshan",
            region_id="alishan",
            oxidation_level=0.20,
            roast_level=RoastLevel.NONE,
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["floral", "butter", "cream"],
            flavor_secondary=["lily", "honey", "milk"],
            aroma=["floral", "fresh", "mountain"],
            body=BodyLevel.MEDIUM,
            finish="Sweet, floral, lasting",
            brewing_gongfu=BrewingParams(
                water_temp_c=90, water_temp_f=194,
                leaf_ratio_g_per_100ml=6,
                first_steep_seconds=25,
                subsequent_steep_seconds=20,
                steep_increment_seconds=5,
                num_steeps=7,
                rinse_recommended=True
            ),
            price_mid=PriceRange(min_usd_per_50g=30, max_usd_per_50g=70),
            best_for=["afternoon-focus", "meditation"],
            similar_tea_ids=["tie-guan-yin", "li-shan-oolong"],
            description_brief="Lightly oxidized oolong from Taiwan's Alishan mountain range, grown above 1000m. Known for intense floral fragrance and creamy texture.",
            tier=2
        ),

        Tea(
            id="dong-ding",
            name_en="Dong Ding Oolong",
            name_zh="冻顶乌龙",
            name_pinyin="Dòngdǐng Wūlóng",
            category_id="oolong",
            subcategory_id="taiwan-gaoshan",
            region_id="dong-ding",
            oxidation_level=0.30,
            roast_level=RoastLevel.MEDIUM,
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["roasted", "floral", "honey"],
            flavor_secondary=["caramel", "orchid", "butter"],
            aroma=["roasted", "floral", "sweet"],
            body=BodyLevel.MEDIUM_FULL,
            finish="Sweet, warming, complex",
            brewing_gongfu=BrewingParams(
                water_temp_c=95, water_temp_f=203,
                leaf_ratio_g_per_100ml=6,
                first_steep_seconds=20,
                subsequent_steep_seconds=15,
                steep_increment_seconds=5,
                num_steeps=6,
                rinse_recommended=True
            ),
            price_mid=PriceRange(min_usd_per_50g=25, max_usd_per_50g=55),
            best_for=["afternoon-focus", "winter-warming"],
            similar_tea_ids=["tie-guan-yin", "alishan-oolong"],
            description_brief="Traditional Taiwanese oolong with medium roast, offering balance between floral freshness and toasty warmth. One of Taiwan's original famous teas.",
            tier=2
        ),

        Tea(
            id="jin-jun-mei",
            name_en="Jin Jun Mei (Golden Eyebrow)",
            name_zh="金骏眉",
            name_pinyin="Jīn Jùn Méi",
            category_id="black",
            region_id="wuyi-mountains",
            oxidation_level=0.95,
            harvest_season="spring",
            caffeine_level=CaffeineLevel.HIGH,
            flavor_primary=["honey", "cocoa", "sweet potato"],
            flavor_secondary=["longan", "floral", "malt"],
            aroma=["honey", "sweet", "floral"],
            body=BodyLevel.MEDIUM_FULL,
            finish="Sweet, smooth, lingering",
            brewing_gongfu=BrewingParams(
                water_temp_c=90, water_temp_f=194,
                leaf_ratio_g_per_100ml=5,
                first_steep_seconds=15,
                subsequent_steep_seconds=10,
                steep_increment_seconds=5,
                num_steeps=8,
                rinse_recommended=False
            ),
            price_mid=PriceRange(min_usd_per_50g=50, max_usd_per_50g=120),
            price_premium=PriceRange(min_usd_per_50g=150, max_usd_per_50g=500),
            best_for=["special-occasion", "guests"],
            similar_tea_ids=["qimen-hongcha", "zhengshan-xiaozhong"],
            description_brief="Premium black tea from Wuyi made entirely from golden buds. Created in 2005, it quickly became one of China's most sought-after teas for its intense sweetness and complexity.",
            tier=2
        ),

        Tea(
            id="zhengshan-xiaozhong",
            name_en="Zhengshan Xiaozhong (Lapsang Souchong)",
            name_zh="正山小种",
            name_pinyin="Zhèngshān Xiǎozhǒng",
            category_id="black",
            subcategory_id="zhengshan-xiaozhong",
            region_id="wuyi-mountains",
            oxidation_level=0.95,
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["longan", "honey", "smoke"],
            flavor_secondary=["dried fruit", "pine", "chocolate"],
            aroma=["smoky", "sweet", "fruity"],
            body=BodyLevel.MEDIUM_FULL,
            finish="Sweet, slightly smoky",
            brewing_gongfu=BrewingParams(
                water_temp_c=95, water_temp_f=203,
                leaf_ratio_g_per_100ml=5,
                first_steep_seconds=20,
                subsequent_steep_seconds=15,
                steep_increment_seconds=5,
                num_steeps=6,
                rinse_recommended=False
            ),
            price_mid=PriceRange(min_usd_per_50g=20, max_usd_per_50g=50),
            best_for=["morning-energy", "winter-warming"],
            similar_tea_ids=["qimen-hongcha", "jin-jun-mei"],
            description_brief="The original black tea, created in the Wuyi Mountains during the Ming Dynasty. Traditional versions are pine-smoked, while modern styles focus on the natural longan-like sweetness.",
            tier=2
        ),

        Tea(
            id="liu-bao",
            name_en="Liu Bao Hei Cha",
            name_zh="六堡茶",
            name_pinyin="Liù Bǎo Chá",
            category_id="dark",
            subcategory_id="liu-bao",
            region_id="guangxi",
            oxidation_level=0.90,
            is_aged=True,
            caffeine_level=CaffeineLevel.LOW,
            flavor_primary=["betel nut", "earth", "wood"],
            flavor_secondary=["dates", "herbs", "mineral"],
            aroma=["betel nut", "aged", "earthy"],
            body=BodyLevel.MEDIUM_FULL,
            finish="Smooth, cooling, clean",
            brewing_gongfu=BrewingParams(
                water_temp_c=100, water_temp_f=212,
                leaf_ratio_g_per_100ml=6,
                first_steep_seconds=15,
                subsequent_steep_seconds=10,
                steep_increment_seconds=5,
                num_steeps=12,
                rinse_recommended=True
            ),
            price_mid=PriceRange(min_usd_per_50g=15, max_usd_per_50g=40),
            best_for=["digestion", "evening-relaxation"],
            similar_tea_ids=["menghai-shou-puerh", "fu-zhuan"],
            description_brief="Dark tea from Guangxi province with distinctive betel nut aroma. Ages beautifully and is traditionally valued for its digestive properties.",
            tier=2
        ),

        Tea(
            id="shoumei",
            name_en="Shou Mei (Longevity Eyebrow)",
            name_zh="寿眉",
            name_pinyin="Shòu Méi",
            category_id="white",
            subcategory_id="shoumei",
            region_id="fuding",
            oxidation_level=0.12,
            caffeine_level=CaffeineLevel.LOW,
            flavor_primary=["hay", "honey", "dates"],
            flavor_secondary=["herbs", "wood", "sweet"],
            aroma=["hay", "honey", "dried fruit"],
            body=BodyLevel.MEDIUM,
            finish="Sweet, warming, smooth",
            brewing_gongfu=BrewingParams(
                water_temp_c=90, water_temp_f=194,
                leaf_ratio_g_per_100ml=5,
                first_steep_seconds=30,
                subsequent_steep_seconds=25,
                steep_increment_seconds=10,
                num_steeps=6,
                rinse_recommended=False
            ),
            price_budget=PriceRange(min_usd_per_50g=5, max_usd_per_50g=12),
            best_for=["daily-drinking", "evening-relaxation"],
            similar_tea_ids=["bai-mudan", "bai-hao-yinzhen"],
            description_brief="Made from mature white tea leaves, offering more body than Silver Needle or White Peony. Ages exceptionally well, developing rich, sweet complexity over years.",
            tier=2
        ),

        Tea(
            id="taiping-houkui",
            name_en="Taiping Houkui (Monkey King)",
            name_zh="太平猴魁",
            name_pinyin="Tàipíng Hóukuí",
            category_id="green",
            region_id="anhui",
            oxidation_level=0.02,
            harvest_season="spring",
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["orchid", "sweet", "vegetal"],
            flavor_secondary=["magnolia", "chestnut"],
            aroma=["orchid", "fresh", "subtle"],
            body=BodyLevel.LIGHT_MEDIUM,
            finish="Sweet, smooth, lasting",
            brewing_gongfu=BrewingParams(
                water_temp_c=80, water_temp_f=176,
                leaf_ratio_g_per_100ml=3,
                first_steep_seconds=45,
                subsequent_steep_seconds=30,
                steep_increment_seconds=10,
                num_steeps=4,
                rinse_recommended=False
            ),
            price_mid=PriceRange(min_usd_per_50g=25, max_usd_per_50g=60),
            best_for=["guests", "special-occasion"],
            similar_tea_ids=["huangshan-maofeng", "xi-hu-longjing"],
            description_brief="Distinctive green tea with exceptionally large, flat leaves pressed during processing. One of China's Top Ten Famous Teas, prized for its elegant orchid fragrance.",
            tier=2
        ),

        Tea(
            id="junshan-yinzhen",
            name_en="Junshan Yinzhen (Junshan Silver Needle)",
            name_zh="君山银针",
            name_pinyin="Jūnshān Yínzhēn",
            category_id="yellow",
            region_id="junshan",
            oxidation_level=0.10,
            harvest_season="spring",
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["sweet corn", "chestnut", "mellow"],
            flavor_secondary=["honey", "apricot"],
            aroma=["toasted grain", "sweet", "subtle"],
            body=BodyLevel.LIGHT_MEDIUM,
            finish="Smooth, sweet, lingering",
            brewing_gongfu=BrewingParams(
                water_temp_c=80, water_temp_f=176,
                leaf_ratio_g_per_100ml=4,
                first_steep_seconds=45,
                subsequent_steep_seconds=35,
                steep_increment_seconds=10,
                num_steeps=4,
                rinse_recommended=False
            ),
            price_premium=PriceRange(min_usd_per_50g=80, max_usd_per_50g=250),
            best_for=["special-occasion", "meditation"],
            similar_tea_ids=["bai-hao-yinzhen", "huoshan-huangya"],
            description_brief="The most famous yellow tea, made only on Junshan Island in Dongting Lake. The unique 'sealed yellowing' process creates a mellower flavor than green tea.",
            tier=2
        ),
    ]

    inserted = 0
    # First pass: insert all teas (without similar relationships)
    for tea in teas:
        try:
            db.insert_tea(tea)
            inserted += 1
        except Exception as e:
            print(f"Failed to insert tea {tea.id}: {e}")

    # Second pass: link similar teas (now that all teas exist)
    for tea in teas:
        if tea.similar_tea_ids:
            try:
                db.link_similar_teas(tea.id, tea.similar_tea_ids)
            except Exception:
                pass  # Silently ignore missing similar teas

    return inserted
