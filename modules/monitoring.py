"""
System monitoring for Armbian
"""

import logging
import psutil
import asyncio
from datetime import timedelta

logger = logging.getLogger(__name__)


class SystemMonitor:
    """Monitor Armbian system resources"""
    
    async def get_system_stats(self) -> dict:
        """Get comprehensive system statistics"""
        try:
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory info
            mem = psutil.virtual_memory()
            
            # Disk info
            disk = psutil.disk_usage('/')
            
            # Temperature (if available)
            try:
                temps = psutil.sensors_temperatures()
                temp = next(iter(temps.values()))[0].current if temps else None
            except:
                temp = None
            
            # Uptime
            uptime_seconds = self._get_uptime()
            uptime_str = self._format_uptime(uptime_seconds)
            
            # System load
            load_avg = psutil.getloadavg()
            
            return {
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'cpu_load': load_avg,
                'memory_total': mem.total,
                'memory_used': mem.used,
                'memory_percent': mem.percent,
                'disk_total': disk.total,
                'disk_used': disk.used,
                'disk_percent': disk.percent,
                'temperature': temp,
                'uptime_seconds': uptime_seconds,
                'uptime_str': uptime_str,
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def _get_uptime(self) -> int:
        """Get system uptime in seconds"""
        try:
            with open('/proc/uptime', 'r') as f:
                return int(float(f.readline().split()[0]))
        except:
            return 0
    
    def _format_uptime(self, seconds: int) -> str:
        """Format uptime nicely"""
        td = timedelta(seconds=seconds)
        days = td.days
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        
        return " ".join(parts) or "< 1m"
    
    def _format_bytes(self, bytes_val: int) -> str:
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f}{unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f}PB"
    
    def format_stats(self, stats: dict) -> str:
        """Format stats as readable message"""
        if not stats:
            return "⚠️ Tidak dapat membaca status server"
        
        msg = "🖥️ STATUS SERVER ARMBIAN\n"
        msg += f"├─ CPU: {stats.get('cpu_percent', 0):.1f}% ({stats.get('cpu_count', 0)} cores)\n"
        msg += f"├─ Memory: {stats.get('memory_percent', 0):.1f}% "
        msg += f"({self._format_bytes(stats.get('memory_used', 0))}/"
        msg += f"{self._format_bytes(stats.get('memory_total', 0))})\n"
        msg += f"├─ Disk: {stats.get('disk_percent', 0):.1f}% "
        msg += f"({self._format_bytes(stats.get('disk_used', 0))}/"
        msg += f"{self._format_bytes(stats.get('disk_total', 0))})\n"
        
        if stats.get('temperature'):
            msg += f"├─ Temperature: {stats['temperature']:.1f}°C\n"
        
        msg += f"└─ Uptime: {stats.get('uptime_str', 'N/A')}"
        
        return msg
