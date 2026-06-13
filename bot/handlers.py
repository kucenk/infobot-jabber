"""
Message handler and command processor
"""

import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)


class MessageHandler:
    """Processes and routes messages"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def handle_chat_message(self, msg):
        """Handle direct chat messages"""
        sender = msg['from'].bare
        text = msg['body']
        
        logger.info(f"💬 Chat from {sender}: {text}")
        
        # Check if admin
        is_admin = sender in self.bot.admin_jids
        
        # Process commands
        if text.startswith('!'):
            await self.process_command(sender, text, is_admin, msg)
        else:
            # Echo or default response
            response = f"Terima kasih atas pesan Anda! Ketik !help untuk bantuan."
            msg.reply(response).send()
    
    async def handle_groupchat_message(self, msg):
        """Handle groupchat messages"""
        room = msg['from'].bare
        sender = msg['from'].resource
        text = msg['body']
        
        # Ignore own messages
        if sender == self.bot.bot_nick:
            return
        
        # Update last activity
        if room in self.bot.rooms:
            from datetime import datetime
            self.bot.rooms[room]['last_activity'] = datetime.now()
        
        logger.info(f"💬 [{room}] {sender}: {text}")
        
        # Find sender's JID
        try:
            sender_jid = self.bot['xep_0045'].get_jid(room, sender)
            is_admin = sender_jid in self.bot.admin_jids
        except:
            is_admin = False
        
        # Process commands
        if text.startswith('!'):
            await self.process_command(room, text, is_admin, msg, is_groupchat=True)
    
    async def process_command(self, target: str, text: str, is_admin: bool, 
                            msg=None, is_groupchat: bool = False):
        """Process command and send response"""
        parts = text.split(maxsplit=1)
        command = parts[0].lower()[1:]  # Remove '!'
        args = parts[1] if len(parts) > 1 else ""
        
        logger.info(f"⚡ Command: {command} from {target}, args: {args}")
        
        # Route to command handler
        if command == 'help':
            response = await self.cmd_help(is_admin)
        elif command == 'cuaca':
            response = await self.cmd_weather(args)
        elif command == 'gempa':
            response = await self.cmd_earthquake()
        elif command == 'server':
            response = await self.cmd_server()
        elif command == 'status':
            response = await self.cmd_status(args, is_admin)
        elif command == 'admin' and is_admin:
            response = await self.cmd_admin(args)
        elif command == 'ping':
            response = "🏓 Pong!"
        elif command == 'uptime':
            response = await self.cmd_uptime()
        else:
            response = f"❌ Perintah tidak dikenali: {command}\nKetik !help untuk bantuan"
        
        # Send response
        if is_groupchat and msg:
            self.bot.send_message(
                mto=target,
                mbody=response,
                mtype='groupchat'
            )
        elif msg:
            msg.reply(response).send()
        else:
            self.bot.send_message(mto=target, mbody=response, mtype='chat')
    
    async def cmd_help(self, is_admin: bool) -> str:
        """Help command"""
        help_text = """📚 INFO BOT - BANTUAN PERINTAH

Perintah Umum:
  !help          - Tampilkan bantuan ini
  !cuaca [kota]  - Cek cuaca saat ini
  !gempa         - Info gempa terakhir
  !server        - Status server Armbian
  !uptime        - Uptime server
  !status [msg]  - Update status bot
  !ping          - Cek koneksi

Admin Commands:"""
        if is_admin:
            help_text += """
  !admin reload  - Reload konfigurasi
  !admin stop    - Stop bot
  !admin rooms   - Daftar ruangan
  !admin stats   - Statistik bot"""
        return help_text.strip()
    
    async def cmd_weather(self, city: str) -> str:
        """Weather command"""
        if not city:
            city = "Jakarta"
        
        try:
            weather = await self.bot.weather.get_weather(city)
            if not weather:
                return f"❌ Cuaca untuk '{city}' tidak ditemukan"
            
            return self.bot.weather.format_weather(weather)
        except Exception as e:
            logger.error(f"Weather error: {e}")
            return f"⚠️ Gagal mengambil data cuaca: {str(e)[:50]}"
    
    async def cmd_earthquake(self) -> str:
        """Earthquake command"""
        try:
            quakes = await self.bot.earthquake.get_latest()
            if not quakes:
                return "✅ Tidak ada gempa signifikan terakhir ini"
            
            latest = quakes[0]
            return self.bot.format_earthquake_alert(latest)
        except Exception as e:
            logger.error(f"Earthquake error: {e}")
            return f"⚠️ Gagal mengambil data gempa: {str(e)[:50]}"
    
    async def cmd_server(self) -> str:
        """Server monitoring command"""
        try:
            stats = await self.bot.monitor.get_system_stats()
            return self.bot.monitor.format_stats(stats)
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            return f"⚠️ Gagal membaca status server: {str(e)[:50]}"
    
    async def cmd_status(self, message: str, is_admin: bool) -> str:
        """Update status command"""
        if not is_admin:
            return "❌ Hanya admin yang bisa mengubah status"
        
        if message:
            self.bot.send_presence(pstatus=message)
            return f"✅ Status diperbarui: {message}"
        return "⚠️ Gunakan: !status [pesan]"
    
    async def cmd_uptime(self) -> str:
        """Uptime command"""
        try:
            stats = await self.bot.monitor.get_system_stats()
            return f"⏱️ Uptime: {stats.get('uptime_str', 'N/A')}"
        except Exception as e:
            return f"⚠️ Error: {str(e)[:50]}"
    
    async def cmd_admin(self, args: str) -> str:
        """Admin commands"""
        if not args:
            return "❌ Gunakan: !admin [reload|stop|rooms|stats]"
        
        subcommand = args.split()[0].lower()
        
        if subcommand == 'reload':
            return "🔄 Reload belum diimplementasikan"
        elif subcommand == 'stop':
            return "🛑 Bot akan distop"
        elif subcommand == 'rooms':
            rooms_list = "\n".join(self.bot.rooms.keys())
            return f"📍 Ruangan Bot:\n{rooms_list}"
        elif subcommand == 'stats':
            stats = {
                'active_rooms': len(self.bot.active_rooms),
                'total_rooms': len(self.bot.rooms),
                'admin_count': len(self.bot.admin_jids)
            }
            return f"📊 Stats Bot:\n" + "\n".join(f"  {k}: {v}" for k, v in stats.items())
        
        return "❌ Subcommand tidak dikenali"
