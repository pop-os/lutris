import os
from gettext import gettext as _

from lutris import settings
from lutris.services.base import BaseService
from lutris.services.service_game import ServiceGame
from lutris.services.service_media import ServiceMedia
from lutris.util import system
from lutris.util.dolphin.cache_reader import DOLPHIN_GAME_CACHE_FILE, DolphinCacheReader
from lutris.util.strings import slugify


class DolphinBanner(ServiceMedia):
    service = "dolphin"
    source = "local"
    size = (120, 30)
    file_pattern = "%s"
    dest_path = os.path.join(settings.CACHE_DIR, "dolphin/banners/small")


class DolphinService(BaseService):
    id = "dolphin"
    icon = "dolphin"
    name = _("Dolphin")
    medias = {
        "icon": DolphinBanner
    }

    def load(self):
        if not system.path_exists(DOLPHIN_GAME_CACHE_FILE):
            self.emit("service-games-loaded")
            return
        cache_reader = DolphinCacheReader()
        dolphin_games = [DolphinGame.new_from_cache(game) for game in cache_reader.get_games()]
        for game in dolphin_games:
            game.save()
        self.emit("service-games-loaded")


class DolphinGame(ServiceGame):
    """Game for the Dolphin emulator"""

    service = "dolphin"
    installer_slug = "dolphin"

    @classmethod
    def new_from_cache(cls, cache_entry):
        """Create a service game from an entry from the Dolphin cache"""
        service_game = cls()
        service_game.name = cls.get_game_name(cache_entry)
        service_game.appid = str(cache_entry["code_1"])
        service_game.slug = slugify(cache_entry["name_long"])
        service_game.icon = ""
        return service_game

    @staticmethod
    def get_game_name(cache_entry):
        names = cache_entry["name_long"]
        name_index = 1 if len(names.keys()) > 1 else 0
        return str(names[list(names.keys())[name_index]])
