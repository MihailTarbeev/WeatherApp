from pathlib import Path

from weather_api_service import get_weather
from weather_formatter import format_weather
from exceptions import ApiServiceError
from history import save_weather, PlainFileWeatherStorage


def main():
    city = input('Введите название города: ')
    country_code = input('Введите код страны по ISO 3166-1, например, "ru": ')
    if len(country_code) == 0 or len(country_code) > 3:
        print('Неверный формат кода страны')
        exit(1)
    try:
        weather = get_weather(city, country_code)
    except ApiServiceError:
        print(f'Не удалось получить погоду в данном городе: {city}, {country_code}')
        exit(1)
    print(format_weather(weather))

    save_weather(weather, PlainFileWeatherStorage(Path.cwd() / "history.txt"))


if __name__ == '__main__':
    main()
