import os


def setup_proxy(proxy_user, proxy_password, proxy_ip, proxy_port):
    """
    Установка прокси для запросов к API Groq
    :param proxy_user: Имя пользователя прокси
    :param proxy_password: Пароль пользователя прокси
    :param proxy_ip: IP прокси
    :param proxy_port: Порт прокси
    :return: None
    """
    # Указываем прокси для HTTP и HTTPS
    os.environ['http_proxy'] = f"http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}"
    os.environ['https_proxy'] = f"http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}"
