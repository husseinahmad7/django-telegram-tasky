"""
PyInstaller runtime hook for asyncio.
Fixes event loop issues when running as executable.
"""
import sys
import asyncio
import warnings

# Suppress deprecation warnings for asyncio event loop policy
warnings.filterwarnings('ignore', category=DeprecationWarning, module='asyncio')

# For Python 3.14+, we don't need to set event loop policy explicitly
# The default policy works fine. Only override for older versions if needed.
# if sys.platform == 'win32' and sys.version_info <= (3, 14):
#     try:
#         asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#     except AttributeError:
#         pass


# Critical fix for PyInstaller with asyncio
if sys.platform == 'win32':
    # For Python 3.8+, we need to ensure the event loop policy is set
    # before any asyncio operations occur
    if sys.version_info >= (3, 8):
        # Don't set policy for 3.14+ as it causes deprecation warnings
        # Instead, ensure we have a proper event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            # No event loop, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
