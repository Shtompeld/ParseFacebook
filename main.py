import parse as fb
import config as cfg

def main():

    driver = fb.get_webdriver()
    is_auth = fb.auth(driver,f"{cfg.COOKIES_PATH}")

    if is_auth:

        product_list = fb.parse(driver,cfg.QUERY,cfg.CITY)

        if len(product_list)>1:
            with open('output.txt', 'w', encoding='utf-8') as file:
                file.write('\n'.join(product_list))

            print("Сохранение завершено")
        else:
            print("Подходящих товаров не было найдено")
    else:
        print(f"Авторизация не прошла!")

main()