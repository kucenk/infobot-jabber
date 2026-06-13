#!/usr/bin/env python3
"""
InfoBot Jabber - Advanced XMPP Bot for Armbian
Main entry point with graceful shutdown and auto-restart
"""

import logging
import asyncio
import signal
import sys
from pathlib import Path
import yaml

# Ensure directories exist FIRST (before logging)
Path('logs').mkdir(exist_ok=True)
Path('config').mkdir(exist_ok=True)
Path('data').mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/infobot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from bot.core import InfoBot


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load YAML configuration file"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        logger.info("Creating from template...")
        import shutil
        shutil.copy("config/config.example.yaml", config_path)
        sys.exit(1)


class BotManager:
    """Manages bot lifecycle with auto-restart capability"""
    
    def __init__(self, config: dict):
        self.config = config
        self.bot = None
        self.running = True
        self.restart_count = 0
        self.max_restarts = 5
        
    async def start(self):
        """Start bot with auto-restart"""
        while self.running:
            try:
                self.bot = InfoBot(self.config)
                logger.info("🤖 InfoBot starting...")
                await self.bot.connect()
                logger.info("✅ InfoBot connected and running")
                self.restart_count = 0
            except Exception as e:
                logger.error(f"❌ Bot error: {e}", exc_info=True)
                self.restart_count += 1
                
                if self.restart_count >= self.max_restarts:
                    logger.critical(f"Max restarts ({self.max_restarts}) reached. Exiting.")
                    self.running = False
                    break
                
                wait_time = min(30, 5 * self.restart_count)
                logger.info(f"Restarting in {wait_time}s (attempt {self.restart_count})...")
                await asyncio.sleep(wait_time)
    
    async def stop(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down InfoBot...")
        self.running = False
        if self.bot:
            await self.bot.disconnect()
        logger.info("✅ InfoBot stopped")


async def main():
    """Main async entry point"""
    # Load config
    config = load_config()
    
    # Create bot manager
    manager = BotManager(config)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}")
        asyncio.create_task(manager.stop())
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start bot
    await manager.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
