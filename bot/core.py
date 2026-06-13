"""
Core InfoBot XMPP Client
"""

import logging
import asyncio
from typing import Dict, List, Optional, Set
import slixmpp
from slixmpp.exceptions import XMPPError
from datetime import datetime
import threading

from bot.handlers import MessageHandler
from modules.database import Database
from modules.monitoring import SystemMonitor
from modules.weather import WeatherAPI
from modules.earthquake import EarthquakeAPI
from modules.notifications import NotificationManager

logger = logging.getLogger(__name__)


class InfoBot(slixmpp.ClientXMPP):
    """
    Advanced InfoBot with multi-room support and feature-rich functionality
    """
    
    def __init__(self, config: dict):
        self.config = config
        
        # Bot credentials
        bot_config = config.get('bot', {})
        jid = bot_config.get('jid')
        password = bot_config.get('password')
        
        super().__init__(jid, password)
        
        # Initialize components
        self.db = Database()
        self.monitor = SystemMonitor()
        self.weather = WeatherAPI(config.get('openweather', {}).get('api_key'))
        self.earthquake = EarthquakeAPI()
        self.notifications = NotificationManager(self)
        self.message_handler = MessageHandler(self)
        
        # Bot state
        self.rooms: Dict[str, dict] = {}
        self.active_rooms: Set[str] = set()
        self.admin_jids: Set[str] = set()
        self.bot_nick = bot_config.get('nick', 'InfoBot')
        self.presence_type = 'available'
        
        # Initialize rooms from config
        self._init_rooms()
        
        # Register event handlers
        self._register_handlers()
        
        # Feature flags
        self.features_enabled = {
            'weather': config.get('features', {}).get('weather', True),
            'earthquake': config.get('features', {}).get('earthquake', True),
            'monitoring': config.get('features', {}).get('monitoring', True),
            'greetings': config.get('features', {}).get('greetings', True),
        }
        
        logger.info(f"🤖 InfoBot initialized as {jid}")
    
    def _init_rooms(self):
        """Initialize rooms from configuration"""
        rooms_config = self.config.get('rooms', [])
        
        for room_config in rooms_config:
            room_jid = room_config.get('name')
            self.rooms[room_jid] = {
                'config': room_config,
                'joined': False,
                'users': set(),
                'last_activity': None,
                'status': 'offline'
            }
            
            # Add admin JID
            admin_jid = room_config.get('admin_jid')
            if admin_jid:
                self.admin_jids.add(admin_jid)
            
            logger.info(f"📌 Room configured: {room_jid}")
    
    def _register_handlers(self):
        """Register XMPP event handlers"""
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.on_message)
        self.add_event_handler("muc::got_online", self.on_muc_online)
        self.add_event_handler("muc::got_offline", self.on_muc_offline)
        self.add_event_handler("muc::got_unavailable", self.on_muc_offline)
        self.add_event_handler("groupchat_message", self.on_groupchat_message)
        self.add_event_handler("presence_subscribe", self.on_presence_subscribe)
        self.add_event_handler("disconnected", self.on_disconnected)
        
        # Register plugins
        self.register_plugin('xep_0045')  # Multi-User Chat (MUC)
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # XMPP Ping
        self.register_plugin('xep_0115')  # Entity Capabilities
        
        logger.info("✅ Event handlers registered")
    
    async def start(self, event):
        """Handle session start"""
        try:
            self.send_presence()
            await self.get_roster()
            
            logger.info("✅ Session started, joining rooms...")
            
            # Join all configured rooms
            for room_jid, room_info in self.rooms.items():
                await self.join_room(room_jid, room_info['config'])
            
            # Start background tasks
            asyncio.create_task(self.monitor_activity())
            asyncio.create_task(self.check_alerts())
            
            logger.info("🚀 InfoBot fully operational")
        except Exception as e:
            logger.error(f"Error in start: {e}", exc_info=True)
    
    async def join_room(self, room_jid: str, room_config: dict):
        """Join a MUC room"""
        try:
            nick = room_config.get('nickname', self.bot_nick)
            
            # Use join_muc without wait parameter for Slixmpp compatibility
            self['xep_0045'].join_muc(room_jid, nick)
            
            # Small delay to allow join to process
            await asyncio.sleep(0.5)
            
            room_info = self.rooms[room_jid]
            room_info['joined'] = True
            room_info['status'] = 'online'
            self.active_rooms.add(room_jid)
            
            logger.info(f"✅ Joined room: {room_jid} as {nick}")
            
            # Send welcome message
            if self.features_enabled['greetings']:
                welcome_msg = room_config.get('welcome_message', 
                    f"Halo! Saya {nick} siap membantu 🤖")
                await asyncio.sleep(1)
                self.send_message(
                    mto=room_jid,
                    mbody=welcome_msg,
                    mtype='groupchat'
                )
        except Exception as e:
            logger.error(f"Failed to join {room_jid}: {e}")
    
    async def on_message(self, msg):
        """Handle incoming messages"""
        if msg['type'] in ('chat', 'normal'):
            await self.message_handler.handle_chat_message(msg)
    
    async def on_groupchat_message(self, msg):
        """Handle groupchat messages"""
        if msg['body']:
            await self.message_handler.handle_groupchat_message(msg)
    
    async def on_muc_online(self, presence):
        """Handle user joining room"""
        room = presence['muc']['room']
        nick = presence['muc']['nick']
        jid = presence['muc']['jid']
        
        if room in self.rooms:
            self.rooms[room]['users'].add(nick)
            self.rooms[room]['last_activity'] = datetime.now()
            
            logger.info(f"👤 {nick} joined {room}")
            
            # Send greeting if enabled
            if self.features_enabled['greetings'] and nick != self.bot_nick:
                greeting = f"Selamat datang @{nick}! 👋"
                await asyncio.sleep(0.5)
                self.send_message(mto=room, mbody=greeting, mtype='groupchat')
    
    async def on_muc_offline(self, presence):
        """Handle user leaving room"""
        room = presence['muc']['room']
        nick = presence['muc']['nick']
        
        if room in self.rooms:
            self.rooms[room]['users'].discard(nick)
            logger.info(f"👤 {nick} left {room}")
    
    def on_presence_subscribe(self, presence):
        """Handle subscription requests"""
        self.send_presence_subscription(pto=presence['from'])
    
    async def on_disconnected(self, event):
        """Handle disconnection"""
        logger.warning("⚠️ Disconnected from XMPP server")
        await asyncio.sleep(5)
        # Don't try to reconnect here - let main loop handle it
    
    async def monitor_activity(self):
        """Monitor room activity and update status"""
        while True:
            try:
                for room_jid, room_info in self.rooms.items():
                    if room_jid not in self.active_rooms:
                        continue
                    
                    # Check activity
                    last_activity = room_info.get('last_activity')
                    if last_activity:
                        idle_seconds = (datetime.now() - last_activity).total_seconds()
                        
                        # Update status based on activity
                        if idle_seconds > 3600:  # 1 hour
                            new_status = 'away'
                        else:
                            new_status = 'online'
                        
                        if room_info['status'] != new_status:
                            room_info['status'] = new_status
                            self.send_presence(
                                pshow=new_status,
                                pstatus=f"Monitoring {len(self.active_rooms)} rooms"
                            )
                
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Error in monitor_activity: {e}")
                await asyncio.sleep(60)
    
    async def check_alerts(self):
        """Check for earthquake and weather alerts"""
        while True:
            try:
                # Check earthquakes every 5 minutes
                if self.features_enabled['earthquake']:
                    await self.check_earthquakes()
                
                # Check weather every 10 minutes
                if self.features_enabled['weather']:
                    await self.check_weather_alerts()
                
                await asyncio.sleep(300)
            except Exception as e:
                logger.error(f"Error in check_alerts: {e}")
                await asyncio.sleep(300)
    
    async def check_earthquakes(self):
        """Check for recent earthquakes"""
        try:
            quakes = await self.earthquake.get_latest()
            if quakes:
                latest = quakes[0]
                
                # Check if new and significant
                if latest.get('magnitude', 0) >= 5.0:
                    alert_msg = self.format_earthquake_alert(latest)
                    await self.broadcast_alert(alert_msg, 'earthquake')
        except Exception as e:
            logger.error(f"Error checking earthquakes: {e}")
    
    async def check_weather_alerts(self):
        """Check for weather alerts"""
        try:
            for room_jid, room_info in self.rooms.items():
                if not room_info['joined']:
                    continue
                
                config = room_info['config']
                city = config.get('weather_city', 'Jakarta')
                
                weather = await self.weather.get_weather(city)
                if weather and weather.get('alerts'):
                    alert_msg = self.format_weather_alert(weather)
                    await self.send_room_message(room_jid, alert_msg)
        except Exception as e:
            logger.error(f"Error checking weather: {e}")
    
    async def broadcast_alert(self, message: str, alert_type: str):
        """Broadcast alert to all active rooms"""
        for room_jid in self.active_rooms:
            try:
                self.send_message(mto=room_jid, mbody=message, mtype='groupchat')
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Failed to send alert to {room_jid}: {e}")
    
    async def send_room_message(self, room_jid: str, message: str):
        """Send message to specific room"""
        try:
            self.send_message(mto=room_jid, mbody=message, mtype='groupchat')
        except Exception as e:
            logger.error(f"Failed to send message to {room_jid}: {e}")
    
    def format_earthquake_alert(self, quake: dict) -> str:
        """Format earthquake data into alert message"""
        magnitude = quake.get('magnitude', 'N/A')
        location = quake.get('location', 'Unknown')
        depth = quake.get('depth', 'N/A')
        time = quake.get('time', 'N/A')
        
        return (
            f"🚨 PERINGATAN GEMPA BUMI\n"
            f"└─ Magnitude: {magnitude}\n"
            f"└─ Lokasi: {location}\n"
            f"└─ Kedalaman: {depth} km\n"
            f"└─ Waktu: {time}\n"
            f"⚠️ Waspada dan cari tempat aman!"
        )
    
    def format_weather_alert(self, weather: dict) -> str:
        """Format weather alert"""
        alerts = weather.get('alerts', [])
        if not alerts:
            return ""
        
        msg = "⚠️ PERINGATAN CUACA:\n"
        for alert in alerts[:3]:  # Max 3 alerts
            msg += f"└─ {alert.get('event', 'Alert')}\n"
        
        return msg
    
    async def disconnect(self):
        """Graceful disconnect"""
        try:
            logger.info("Disconnecting from XMPP server...")
            self.disconnect(send_close=True)
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
