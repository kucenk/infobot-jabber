"""
BMKG Earthquake API integration
"""

import logging
import aiohttp
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class EarthquakeAPI:
    """Get earthquake data from BMKG API"""
    
    def __init__(self):
        self.base_url = "https://data.bmkg.go.id/DataMKG/TEWS"
        self.api_url = "https://data.bmkg.go.id/autoparse/json/gempa/terkini"
    
    async def get_latest(self, limit: int = 5) -> list:
        """Get latest earthquakes from BMKG"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.api_url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._parse_bmkg_data(data, limit)
                    else:
                        logger.error(f"BMKG API error: {resp.status}")
                        return []
        except Exception as e:
            logger.error(f"BMKG API exception: {e}")
            return []
    
    def _parse_bmkg_data(self, data: dict, limit: int) -> list:
        """Parse BMKG JSON response"""
        try:
            earthquakes = []
            
            # Get gempa terkini (latest)
            gempa = data.get('Infogempa', {}).get('gempa', [])
            
            for quake_data in gempa[:limit]:
                quake = {
                    'magnitude': float(quake_data.get('Magnitude', 0)),
                    'location': quake_data.get('Wilayah', 'Unknown'),
                    'depth': quake_data.get('Kedalaman', 'N/A').replace(' km', ''),
                    'latitude': quake_data.get('Lintang', ''),
                    'longitude': quake_data.get('Bujur', ''),
                    'time': quake_data.get('Jam', ''),
                    'date': quake_data.get('Tanggal', ''),
                    'impact': quake_data.get('Potensi', 'Unknown'),
                }
                earthquakes.append(quake)
            
            return earthquakes
        except Exception as e:
            logger.error(f"Error parsing BMKG data: {e}")
            return []
