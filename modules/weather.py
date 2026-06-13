"""
OpenWeather API integration
"""

import logging
import aiohttp
import asyncio

logger = logging.getLogger(__name__)


class WeatherAPI:
    """Get weather data from OpenWeather API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def get_weather(self, city: str) -> dict:
        """Get current weather for city"""
        if not self.api_key:
            logger.warning("OpenWeather API key not configured")
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/weather?q={city}&appid={self.api_key}&units=metric&lang=id"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        logger.error(f"Weather API error: {resp.status}")
                        return None
        except Exception as e:
            logger.error(f"Weather API exception: {e}")
            return None
    
    def format_weather(self, weather: dict) -> str:
        """Format weather data"""
        city = weather.get('name', 'Unknown')
        temp = weather.get('main', {}).get('temp', 'N/A')
        feels_like = weather.get('main', {}).get('feels_like', 'N/A')
        humidity = weather.get('main', {}).get('humidity', 'N/A')
        description = weather.get('weather', [{}])[0].get('description', 'Unknown')
        wind_speed = weather.get('wind', {}).get('speed', 'N/A')
        
        emoji = self._get_weather_emoji(weather.get('weather', [{}])[0].get('main', ''))
        
        msg = f"{emoji} CUACA {city.upper()}\n"
        msg += f"├─ Suhu: {temp}°C (terasa {feels_like}°C)\n"
        msg += f"├─ Kelembaban: {humidity}%\n"
        msg += f"├─ Angin: {wind_speed} m/s\n"
        msg += f"└─ {description.capitalize()}"
        
        return msg
    
    def _get_weather_emoji(self, condition: str) -> str:
        """Get emoji for weather condition"""
        condition_map = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Drizzle': '🌦️',
            'Thunderstorm': '⛈️',
            'Snow': '❄️',
            'Mist': '🌫️',
        }
        return condition_map.get(condition, '🌡️')
