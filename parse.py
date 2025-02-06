import config as cfg
import re
from datetime import datetime
from selenium import webdriver
from selenium_stealth import stealth
import json
import requests
from geopy.geocoders import Nominatim

def get_city_coordinate(city):
        """
        Получить координаты города
        :param city: Наименование города
        :return: Координаты города {'longitude': x, 'latitude': y}
        """
        nom = Nominatim(user_agent="getLoc")
        coord = nom.geocode(city)

        return {'longitude': coord.longitude, 'latitude':coord.latitude}

def get_posts_list(cookie_done,lsd_token, coords, query, user_id,fb_dtsg,url = 'https://www.facebook.com/api/graphql/'):
    """
        Получить список товаров
        :param cookie_done: Куки
        :param lsd_token: Токен
        :param coords: Координаты {'longitude': x, 'latitude': y}
        :param query: Текст запроса
        :param user_id: ID пользователя
        :param fb_dtsg: Токен
        :param url: Адрес API
        :return: Возвращает список словарей {'post_id' : x, 'seller_id' : y }
    """
    # Заголовок запроса
    headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-prefers-color-scheme": "light",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-asbd-id": "129477",
            "x-fb-friendly-name": "CometMarketplaceSearchContentPaginationQuery",
            "x-fb-lsd": lsd_token,
            'cookie': cookie_done,
    }

    # Тело запроса
    data = (f"av={user_id}"
                f"&__aaid=0&__user={user_id}&__a=1&__req=1t&__hs=20119.HYP%3Acomet_pkg.2.1...1&dpr=1&__ccg=GOOD&__rev=1019731595&__s=r4ljvx%3A01n6n6%3Ahu4da9&__hsi=7465943252667120547&__dyn=7xeXzWK1ixt0mUyEqxemh0noeEb8nwgUaqwk8KewSwAyUco2qwJyE2OwpUe8hwaG0Z82_CxS320qa321Rwwwqo462mcw5Mx62G5Usw9m1YwBgK7o6C0Mo4G1hwlo5qfK0zEkxe2GewGwkUe9obrwh8lwuEjUlDw-wUwxwjFovUaU3VwLyEbUGdG0HE5d08O321LyUaUbGxe6Uak0zU8oC1Hg6C13xe3a3Gfw-KufxamEbbxG1fBG2-2K2G0JU62&__csr=gjNkAIYJR5OWbHsrthlhTk8NBnkliONnbn2BvibZQCOKLNil8GbQxeyTSDayipaiGBZ9uBvnkGuZFp5Lrlcx27HrFDiiVpAVaqGEFa9GV99Ft99a_SFkhoizX-LDnuQ4epauqHzUngx0yS5VAbyFki4e8UjiCzkaKp7DKQrK4u4oGdglxTJedy9JpGhUpzUjz9bCwGwEAx6iudxOcyomyUy4EgwCCwAxS9zU4yfHx69Bz8qzEkxm6U8UvwkUiGcUtwxwGxO55Uy5EW19wgUogOfzo2mwzwkUCeyo8UaUkwxyXBxW2aUS0CEyuawl8fE6K04dqxC45w4QCw2nEO0xe0zo7aIBi06ExO0JValaq1qg491t2ox04Vw0Wcwl84a06g81qbw6dwaLw3fo0hlw7Dw5Jxm22awPDyo7F0Ug02PCG1qw41wvE13-u0rG4oc80HC2u0HU3Xw1Nm0ji0erw4Bw1AN02po0qXcaAw49wSwqU1gp2054w56w2go0thw0xIw70w4dw55A804dE3lwlE0tpwb-E3V8&__comet_req=15"
                f"&fb_dtsg={fb_dtsg}&jazoest=25065&lsd=_-RmkOd0soTw8kXNxiGeiS&__spin_r=1019731595&__spin_b=trunk&__spin_t=1738300373&fb_api_caller_class=RelayModern&fb_api_req_friendly_name=CometMarketplaceSearchContentPaginationQuery"
                f"&variables=%7B%22count%22%3A{cfg.COUNT_CARDS}%2C%22cursor%22%3A%22%7B%5C%22pg%5C%22%3A{int((cfg.COUNT_CARDS/24)-1)}%2C%5C%22b2c%5C%22%3A%7B%5C%22br%5C%22%3A%5C%22%5C%22%2C%5C%22it%5C%22%3A0%2C%5C%22hmsr%5C%22%3Afalse%2C%5C%22tbi%5C%22%3A0%7D%2C%5C%22c2c%5C%22%3A%7B%5C%22br%5C%22%3A%5C%22Abpt8_4ecCEErevCjVqBWk4l6ewEtJUsOJhATqWi145-726o3djZNcWtucOUXTIjWvegiQgt3ym_IQVo9zMXHOevQOWJYvBKH76tDNCdXC1HebkDbZkhfVHgt_WucdoGGsE7NTnWCfoKZHbj5v9hyz0VLwmE4sNj6wDJkTiQiJvecNhjRQ6w66mBKS0gxc4tKr2QASxoTzqX9WX4rPysD3FJvghwRpwDT7bJ_GNDmj18RpIdPaWZONP9G3fqh0B0h8a27fhvsp2ZvBB0vkUzwQtoFD1_wW5vx_-XcPTbR0XFD8BCHxw5Z95m3MJmpP_VjO_9A2V5fhNbHuxiebo9bf0Un7VP9pYuYcezWKss1kYj0Y5sNPv8FHmQYMnhRAQXx7mTM_ikuRMO6nnh-wa3gTxqdgekcc3NNrgVfOtF7G1wVWkUh5LM23bZgKz0PVSmXnBpGCh2YFuaKKqSflu9Ij2d_a4cUj3_vo4SA6bdgmz0i6w3Apm-99ifLFe642F0fBmAJiaeG4yt-taD8FWQrlXErf7uJwwN-ztwwoI4Hia5lQ%5C%22%2C%5C%22it%5C%22%3A93%2C%5C%22rpbr%5C%22%3A%5C%22%5C%22%2C%5C%22rphr%5C%22%3Afalse%2C%5C%22rmhr%5C%22%3Afalse%7D%2C%5C%22ads%5C%22%3A%7B%5C%22items_since_last_ad%5C%22%3A41%2C%5C%22items_retrieved%5C%22%3A93%2C%5C%22ad_index%5C%22%3A0%2C%5C%22ad_slot%5C%22%3A6%2C%5C%22dynamic_gap_rule%5C%22%3A0%2C%5C%22counted_organic_items%5C%22%3A0%2C%5C%22average_organic_score%5C%22%3A0%2C%5C%22is_dynamic_gap_rule_set%5C%22%3Afalse%2C%5C%22first_organic_score%5C%22%3A0%2C%5C%22is_dynamic_initial_gap_set%5C%22%3Afalse%2C%5C%22iterated_organic_items%5C%22%3A0%2C%5C%22top_organic_score%5C%22%3A0%2C%5C%22feed_slice_number%5C%22%3A0%2C%5C%22feed_retrieved_items%5C%22%3A0%2C%5C%22ad_req_id%5C%22%3A0%2C%5C%22refresh_ts%5C%22%3A0%2C%5C%22cursor_id%5C%22%3A5069%2C%5C%22mc_id%5C%22%3A0%2C%5C%22ad_index_e2e%5C%22%3A0%2C%5C%22seen_ads%5C%22%3A%7B%5C%22ad_ids%5C%22%3A%5B%5D%2C%5C%22page_ids%5C%22%3A%5B%5D%2C%5C%22campaign_ids%5C%22%3A%5B%5D%7D%2C%5C%22has_ad_index_been_reset%5C%22%3Afalse%2C%5C%22is_reconsideration_ads_dropped%5C%22%3Afalse%7D%2C%5C%22irr%5C%22%3Atrue%2C%5C%22serp_cta%5C%22%3Afalse%2C%5C%22rui%5C%22%3A%5B%5D%2C%5C%22mpid%5C%22%3A%5B%5D%2C%5C%22ubp%5C%22%3Anull%2C%5C%22ncrnd%5C%22%3A0%2C%5C%22irsr%5C%22%3Afalse%2C%5C%22bmpr%5C%22%3A%5B%5D%2C%5C%22bmpeid%5C%22%3A%5B%5D%2C%5C%22nmbmp%5C%22%3Afalse%2C%5C%22skrr%5C%22%3Afalse%2C%5C%22ioour%5C%22%3Afalse%2C%5C%22ise%5C%22%3Afalse%7D%22%2C%22params%22%3A%7B%22bqf%22%3A%7B%22callsite%22%3A%22COMMERCE_MKTPLACE_WWW%22%2C%22"
                f"query%22%3A%22{query}%22%7D%2C%22browse_request_params%22%3A%7B%22commerce_enable_local_pickup%22%3Atrue%2C%22commerce_enable_shipping%22%3Atrue%2C%22commerce_search_and_rp_available%22%3Atrue%2C%22commerce_search_and_rp_category_id%22%3A%5B%5D%2C%22commerce_search_and_rp_condition%22%3Anull%2C%22commerce_search_and_rp_ctime_days%22%3Anull%2C%22"
                f"filter_location_latitude%22%3A{coords['latitude']}%2C%22"
                f"filter_location_longitude%22%3A{coords['longitude']}%2C%22"
                f"filter_price_lower_bound%22%3A{cfg.MIN_PRICE_PRODUCT}%2C%22"
                f"filter_price_upper_bound%22%3A{cfg.MAX_PRICE_PRODUCT}%2C%22filter_radius_km%22%3A805%7D%2C%22custom_request_params%22%3A%7B%22browse_context%22%3Anull%2C%22contextual_filters%22%3A%5B%5D%2C%22referral_code%22%3Anull%2C%22saved_search_strid%22%3Anull%2C%22search_vertical%22%3A%22C2C%22%2C%22seo_url%22%3Anull%2C%22surface%22%3A%22SEARCH%22%2C%22virtual_contextual_filters%22%3A%5B%5D%7D%7D%2C%22scale%22%3A1%7D&server_timestamps=true&doc_id=8558510667564038")

    # Отправка POST-запроса
    response = requests.post(url, headers=headers, data=data)

    # Обработка ответа
    if response.status_code == 200:
        links=response.json()['data']['marketplace_search']['feed_units']['edges'] # Список ссылок

        posts=[]
        for link in links:
            posts.append({
                    'post_id' : link['node']['story_key'],
                    'seller_id' : link['node']['listing']['marketplace_listing_seller']['id']
            })
        return posts
    else:
        return f'Ошибка: {response.status_code} - {response.text}'

def get_post_info(cookie_done, lsd_token, user_id, fb_dtsg, post, url='https://www.facebook.com/api/graphql/'):
    """
    Получить год регистрации, количество товаров и отзывов продавца
    :param cookie_done: Куки
    :param lsd_token: Токен
    :param user_id: ID пользователя
    :param fb_dtsg: Токен
    :param post: Словарь {'post_id' : x, 'seller_id' : y }
    :param url: Адрес API
    :return: Словарь {"year_join": x, "ratings_count": y, "count_posts": z }
    """
    # Заголовок запроса
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-prefers-color-scheme": "light",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-asbd-id": "129477",
        'x-fb-friendly-name': 'MarketplacePDPContainerQuery',
        'content-type': 'application/x-www-form-urlencoded',
        "x-fb-lsd": lsd_token,
        'cookie': cookie_done,
    }

    # Тело запроса
    data = (
        f"av={user_id}"
        f"&__aaid=0&__user={user_id}"
        f"&__a=1&__req=2q&__hs=20122.HYP%3Acomet_pkg.2.1...1&dpr=1&__ccg=GOOD&__rev=1019778292&__s=n2qd14%3Awoah8l%3Azut2zo&__hsi=7467075467027461186&__dyn=7xeXzWK1ixt0mUyEqxemh0noeEb8nwgUaqwk8KewSwAyUco2qwJyE2OwpUe8hwaG0Z82_CxS320qa321Rwwwqo462mcw5Mx62G5Usw9m1YwBgK7o6C0Mo4G1hwlo5qfK0zEkxe2GewGwkUe9obrwh8lwuEjUlDw-wUwxwjFovUaU3VwLyEbUGdG0HE5d08O3216wEyUaUbGxe6Uak0zU8oC1Hg6C13xe3a3Gfw-KufxamEbbxG1fBG2-2K2G0JU62&__csr=gT2ZjiN4aROl4OR5hHdd4gJ9nmyWf178wzNankYhQxsJqEh9iZON4BsNQXFtaBiWaSKB_pV5lcjgFan_nGlDy5VGKZGSmQHLHtAFbmQihyHJai8jCDUDAijht9oO2iiiUECimFayKVkcG5aCyt4DVGUhWAAAjz4ExAVXBDUKdArUmx2uimaG7vxl13LWCwGzrWxe4-8x6UG6kbxqbxO2iip12688Rx5e8CzEG9LAzVVVEK32awSy98pyo8U8omwFwxzU8UGidwJx27EKcwSyFEa8oxG1UwByFQ36q1VDCwhElx-UaU9p8mwJgW3C3y0B8C688o3Gwlo720Ao6W0I82Xwxwq8lw9u1FwwwoU1mUW1lDw8i0ha0gq1jG0JzyVXa5KWwh8mwape15wai0BE4aGqxF1PG03VC0nG8w2QUowlo0Oa00X781Co0lyBu0g109qu8gGp04CCyo1XQ0oC0YE1c816E2XwkE4O0gG0f3wep3Uhg0Hcxac22Hxe0bxQdw3J83lg0aLE4O05Ho0ze06N80iCwAwn8567E0tz804ko24a0b2wmbzE13A&__comet_req=15"
        f"&fb_dtsg={fb_dtsg}&jazoest=25828&lsd=vtld_waQCj2-d3Vta7YChj&__spin_r=1019778292&__spin_b=trunk&__spin_t=1738563987&fb_api_caller_class=RelayModern&fb_api_req_friendly_name=MarketplacePDPContainerQuery"
        f"&variables=%7B%22isCOBMOB%22%3Afalse%2C%22isSelfProfile%22%3Afalse%2C%22"
        f"productID%22%3A%22{post['post_id']}%22%2C%22scale%22%3A1%2C%22"
        f"sellerId%22%3A%22{post['seller_id']}%22%2C%22useContextualViewHeader%22%3Atrue%7D&server_timestamps=true&doc_id=8886684371398510"
    )
    # Отправка POST-запроса
    response = requests.post(url, headers=headers, data=data)

    # Обработка ответа
    if response.status_code == 200:
        result = response.json()
        result_dict = {
            "year_join": datetime.fromtimestamp(result['data']['user']['registration_time']).year,
            "ratings_count": result['data']['user']['marketplace_ratings_stats_by_role']['seller_stats']['five_star_total_rating_count_by_role'],
            "count_posts": result['data']['user']['marketplace_inventory_count']
        }
        return result_dict
    else:
        return f'Ошибка: {response.status_code} - {response.text}'

def get_webdriver():
    """
    Создаёт и настраивает webdriver
    :return: webdriver
    """
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    dr = webdriver.Chrome(options=options)
    dr.implicitly_wait(12)
    stealth(dr,
            user_agent='Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.2354.155 Safari/537.36',
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
    )

    return dr

def auth(dr, path_cookies):
    """
    Выполняет авторизацию в Facebook
    :param dr: webdriver
    :param path_cookies: Путь до файла с куками
    :return: При успешной авторизации - True, иначе - False
    """
    dr.get('https://facebook.com/')

    cookies = json.load(open(path_cookies, "r"))
    for cookie in cookies:
        dr.add_cookie(cookie)
    dr.get('https://facebook.com/profile/')
    if dr.current_url == "https://www.facebook.com/login/?next=https%3A%2F%2Fwww.facebook.com%2F":
        return False
    return True

def parse(driver, query, city):
    """
    Собирает товары
    :param driver: webdriver
    :param query: Текст запроса
    :param city: Город
    :return: Список подходящих постов
    """
    jsn = driver.get_cookies()
    cookies = {}

    for item in jsn:
        cookies[item['name']] = item['value']

    coords = get_city_coordinate(city) # Получение координат города
    cookie_done = '; '.join(f'{key}={value}' for key, value in cookies.items()) # Приводит куки в нужный вид
    # Получение lsd_token
    rsp = requests.get('https://www.facebook.com/marketplace/')
    html_content = rsp.text
    html_content = html_content.replace(" ", "").replace("\n", "")
    lsd_token_match = re.search(r'"LSD",\[\],{"token":"(\w+)"},\d+\]', html_content)
    lsd_token = lsd_token_match.group(1) if lsd_token_match else None
    # Получение lsd_token

    fb_dtsg = driver.execute_script("return fb_dtsg;") # Получение fb_dtsg

    driver.quit() # Закрытие браузера т.к. Необходимые данные собраны

    posts_list = get_posts_list(cookie_done=cookie_done,
                                lsd_token=lsd_token,
                                coords=coords,
                                query=query,
                                user_id=cookies['c_user'],
                                fb_dtsg=fb_dtsg)
    accept_posts=[]

    for post in posts_list:
        pst = get_post_info(cookie_done=cookie_done,
                                    lsd_token=lsd_token,
                                    post=post,
                                    user_id=cookies['c_user'],
                                    fb_dtsg=fb_dtsg)

        if int(pst['year_join']) < cfg.MAX_YEAR:

            count_ratings = pst['ratings_count']

            if int(count_ratings) >= cfg.MIN_RATINGS:
                if int(pst['count_posts']) >= cfg.MIN_ACTIVE_LISTINGS:
                    accept_posts.append(f"https://www.facebook.com/marketplace/item/{post['post_id']}")
                else:
                    print(f"Товаров < {cfg.MIN_ACTIVE_LISTINGS}: {post['post_id']}")
            else:
                print(f"Отзывов < {cfg.MIN_RATINGS}: {post['post_id']}")
        else:
            print(f"Аккаунт младше {cfg.MAX_YEAR} года: {post['post_id']}")

    return accept_posts
