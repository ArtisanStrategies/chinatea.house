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
            description="Dark tea (黑茶/heicha) undergoes post-fermentation through microbial activity, developing earthy, smooth, and complex flavors. Unlike pu'er which has its own category, heicha includes regional specialties like Liu Bao from Guangxi with its distinctive betel nut aroma, Fu Zhuan from Hunan with its golden flower fungus (金花), and other brick and compressed teas from Sichuan, Hubei, and Shaanxi. These teas are prized for their digestive benefits and improve with age.",
            oxidation_range_min=0.0,
            oxidation_range_max=1.0,
            color_hex="#3D2914"
        ),
        Category(
            id="puerh",
            name_en="Pu'er Tea",
            name_zh="普洱茶",
            description="Pu'er is a unique tea tradition from Yunnan province made exclusively from large-leaf tea cultivars (大叶种). Sheng (raw) pu'er is sun-dried and can be enjoyed young for its vibrant, complex character or aged for decades to develop deeper, smoother notes. Shou (ripe) pu'er undergoes accelerated pile fermentation (wodui) to create immediate earthy, smooth flavors. Both styles are often compressed into cakes, bricks, or other shapes. Pu'er stands apart from other teas due to its unique terroir, cultivar requirements, and aging tradition.",
            oxidation_range_min=0.0,
            oxidation_range_max=1.0,
            color_hex="#5C4033"
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
        Subcategory(id="liu-bao", category_id="dark", name_en="Liu Bao", name_zh="六堡茶",
                   description="Guangxi dark tea with distinctive betel nut aroma."),
        Subcategory(id="fu-zhuan", category_id="dark", name_en="Fu Zhuan", name_zh="茯砖茶",
                   description="Hunan brick tea with golden flower fungus (金花)."),

        # Pu'er subcategories
        Subcategory(id="sheng", category_id="puerh", name_en="Sheng Pu'er (Raw)", name_zh="生普洱",
                   description="Sun-dried pu'er that can be enjoyed young for vibrant, complex flavors or aged for decades. Young sheng is often bitter and astringent with floral and fruity notes, mellowing over time into smooth, sweet complexity."),
        Subcategory(id="shou", category_id="puerh", name_en="Shou Pu'er (Ripe)", name_zh="熟普洱",
                   description="Pile-fermented (wodui) pu'er developed in the 1970s to mimic aged sheng. Produces immediate earthy, smooth, and mellow flavors with notes of dark chocolate, wet earth, and dried fruit."),

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
               terroir_notes="Diverse terrain from tropical to alpine. Ancient tea trees and pu'er origin."),
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
               terroir_notes="Tropical climate with ancient tea forests. Major pu'er region."),
        Region(id="lincang", parent_id="yunnan", name_en="Lincang", name_zh="临沧",
               name_pinyin="Líncāng", region_type=RegionType.PREFECTURE,
               terroir_notes="Highland area with ancient tea trees. Includes Mengku and Bingdao."),
        Region(id="puerh-city", parent_id="yunnan", name_en="Pu'er City", name_zh="普洱市",
               name_pinyin="Pǔ'ěr", region_type=RegionType.PREFECTURE,
               terroir_notes="Historical trading hub for pu'er tea. Diverse microclimates."),
        Region(id="menghai", parent_id="xishuangbanna", name_en="Menghai", name_zh="勐海",
               name_pinyin="Měnghǎi", region_type=RegionType.COUNTY,
               terroir_notes="Famous for Banzhang and Nannuo mountain teas."),
        Region(id="yiwu", parent_id="xishuangbanna", name_en="Yiwu", name_zh="易武",
               name_pinyin="Yìwǔ", region_type=RegionType.COUNTY,
               terroir_notes="Ancient tea trade route. Known for soft, elegant pu'er."),

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
            preferred_categories=["black", "oolong", "puerh"],
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
            preferred_categories=["white", "puerh", "dark"],
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
            preferred_categories=["puerh", "dark", "oolong"],
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
            preferred_categories=["black", "puerh", "dark", "oolong"],
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
            preferred_categories=["oolong", "white", "puerh"],
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
            description="Unglazed clay teapots from Yixing that absorb tea oils over time, developing a unique patina. Best dedicated to a single tea type. Renowned for enhancing the flavor of oolong and pu'er teas.",
            best_for_categories=["oolong", "puerh", "black"],
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
    """Seed tea data from comprehensive tea_data module."""
    try:
        from .tea_data import ALL_TEAS
        teas = ALL_TEAS
    except ImportError:
        # Fallback to minimal inline data if tea_data.py not available
        teas = _get_minimal_teas()

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


def _get_minimal_teas() -> list:
    """Minimal fallback tea data if tea_data.py is not available."""
    return [
        Tea(
            id="xi-hu-longjing",
            name_en="Xi Hu Longjing (Dragon Well)",
            name_zh="西湖龙井",
            category_id="green",
            region_id="west-lake",
            oxidation_level=0.02,
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["chestnut", "vegetal", "sweet"],
            body=BodyLevel.LIGHT_MEDIUM,
            description_brief="China's most famous green tea.",
            tier=1
        ),
        Tea(
            id="da-hong-pao",
            name_en="Da Hong Pao (Big Red Robe)",
            name_zh="大红袍",
            category_id="oolong",
            region_id="wuyi-mountains",
            oxidation_level=0.65,
            roast_level=RoastLevel.MEDIUM_HEAVY,
            caffeine_level=CaffeineLevel.MODERATE,
            flavor_primary=["mineral", "roasted", "dark chocolate"],
            body=BodyLevel.FULL,
            description_brief="The king of Wuyi rock oolongs.",
            tier=1
        ),
        Tea(
            id="bai-hao-yinzhen",
            name_en="Bai Hao Yin Zhen (Silver Needle)",
            name_zh="白毫银针",
            category_id="white",
            region_id="fuding",
            oxidation_level=0.08,
            caffeine_level=CaffeineLevel.LOW,
            flavor_primary=["melon", "honey", "hay"],
            body=BodyLevel.LIGHT,
            description_brief="The highest grade of white tea.",
            tier=1
        ),
    ]
