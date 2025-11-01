"""
Dynamic handler registry for modular bot apps.
Automatically discovers and registers handlers from INSTALLED_APPS.
"""
import importlib
import logging
from django.conf import settings
from django.apps import apps

logger = logging.getLogger(__name__)


class BotHandlerRegistry:
    """Registry for bot handlers from installed apps."""
    
    def __init__(self):
        self.app_configs = []
        self._discover_apps()
    
    def _discover_apps(self):
        """Discover all apps with bot_config.py."""
        for app_name in settings.INSTALLED_APPS:
            # Skip Django built-in apps
            if app_name.startswith('django.'):
                continue
            
            # Skip rest_framework
            if app_name.startswith('rest_framework'):
                continue
            
            try:
                # Try to import bot_config from the app
                bot_config = importlib.import_module(f'{app_name}.bot_config')
                
                app_info = {
                    'name': app_name,
                    'config': bot_config,
                    'app_name': getattr(bot_config, 'APP_NAME', app_name),
                    'emoji': getattr(bot_config, 'APP_EMOJI', '📦'),
                    'description': getattr(bot_config, 'APP_DESCRIPTION', ''),
                    'order': getattr(bot_config, 'APP_ORDER', 999),
                }
                
                self.app_configs.append(app_info)
                logger.info(f"✅ Discovered bot app: {app_name}")
                
            except (ImportError, AttributeError) as e:
                # App doesn't have bot_config.py, skip it
                logger.debug(f"Skipping {app_name}: no bot_config.py")
                continue
        
        # Sort by order
        self.app_configs.sort(key=lambda x: x['order'])
        logger.info(f"📦 Loaded {len(self.app_configs)} bot apps")
    
    def register_all_handlers(self, application):
        """Register handlers from all discovered apps."""
        logger.info("🔧 Registering handlers from all apps...")
        
        for app_info in self.app_configs:
            try:
                config = app_info['config']
                if hasattr(config, 'register_handlers'):
                    config.register_handlers(application)
                    logger.info(f"  ✅ Registered handlers for {app_info['app_name']}")
                else:
                    logger.warning(f"  ⚠️  {app_info['name']} has no register_handlers()")
            except Exception as e:
                logger.error(f"  ❌ Error registering {app_info['name']}: {e}", exc_info=True)
    
    def get_menu_buttons(self):
        """Get menu buttons from all apps."""
        buttons = []
        
        for app_info in self.app_configs:
            try:
                config = app_info['config']
                if hasattr(config, 'get_menu_buttons'):
                    app_buttons = config.get_menu_buttons()
                    if app_buttons:
                        buttons.extend(app_buttons)
            except Exception as e:
                logger.error(f"Error getting menu buttons from {app_info['name']}: {e}")
        
        return buttons
    
    def get_help_text(self):
        """Get help text from all apps."""
        help_sections = []
        
        for app_info in self.app_configs:
            try:
                config = app_info['config']
                if hasattr(config, 'get_help_text'):
                    help_text = config.get_help_text()
                    if help_text:
                        help_sections.append(help_text)
            except Exception as e:
                logger.error(f"Error getting help text from {app_info['name']}: {e}")
        
        return '\n'.join(help_sections)
    
    def get_app_names(self):
        """Get list of registered app names."""
        return [app['app_name'] for app in self.app_configs]


# Global registry instance
registry = BotHandlerRegistry()

