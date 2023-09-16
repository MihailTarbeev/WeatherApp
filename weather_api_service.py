from datetime import datetime
from enum import Enum
import json
from json.decoder import JSONDecodeError
from typing import Literal, NamedTuple
import urllib.request
from urllib.error import URLError
import config
from exceptions import ApiServiceError
from urllib.parse import quote_plus

Celsius = int


class WeatherType(Enum):
    thunderstorm = 'Гроза'
    drizzle = 'Изморозь'
    rain = 'Дождь'
    snow = 'Снег'
    clear = 'Ясно'
    fog = 'Туман'
    clouds = 'Облачно'


class Weather(NamedTuple):
    temperature: Celsius
    weather_type: WeatherType
    sunrise: datetime
    sunset: datetime
    city: str


def get_weather(city: str, country_code: str) -> Weather:
    """Создаёт запрос в OpenWeather API и обрабатывает его"""
    openweather_response = _get_openweather_response(city, country_code)
    weather = _parse_openweather_response(openweather_response)
    return weather


def _get_openweather_response(city: str, country_code: str) -> str:
    url = config.OPENWEATHER_URL.format(city=quote_plus(city), country_code=country_code)
    try:
        return urllib.request.urlopen(url).read()
    except URLError:
        raise ApiServiceError


def _parse_openweather_response(openweather_response: str) -> Weather:
    try:
        openweather_dict = json.loads(openweather_response)
    except JSONDecodeError:
        raise ApiServiceError
    return Weather(
        temperature=_parse_temperature(openweather_dict),
        weather_type=_parse_weather_type(openweather_dict),
        sunrise=_parse_sun_time(openweather_dict, 'sunrise'),
        sunset=_parse_sun_time(openweather_dict, 'sunset'),
        city=_parse_name_city(openweather_dict),
    )


def _parse_temperature(openweather_dict: dict) -> Celsius:
    return round(openweather_dict["main"]["temp"])


def _parse_weather_type(openweather_dict: dict) -> WeatherType:
    try:
        weather_type_id = str(openweather_dict["weather"][0]["id"])
    except (IndexError, KeyError):
        raise ApiServiceError
    weather_types = {
        "2": WeatherType.thunderstorm,
        "3": WeatherType.drizzle,
        "5": WeatherType.rain,
        "6": WeatherType.snow,
        "7": WeatherType.fog,
        "800": WeatherType.clear,
        "80": WeatherType.clouds
    }
    for _id, _weather_type in weather_types.items():
        if weather_type_id.startswith(_id):
            return _weather_type
    raise ApiServiceError


def _parse_sun_time(openweather_dict: dict,
                    time: Literal['sunrise'] | Literal['sunset']) -> datetime:
    return datetime.fromtimestamp(openweather_dict['sys'][time])


def _parse_name_city(openweather_dict: dict):
    return openweather_dict['name']


if __name__ == "__main__":
    print(get_weather('London', 'vg'))
