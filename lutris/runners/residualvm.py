"""ResidualVM runner"""
# Standard Library
import os
import subprocess
from gettext import gettext as _

# Lutris Modules
from lutris.runners.runner import Runner

RESIDUALVM_CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".residualvmrc")


class residualvm(Runner):
    human_name = _("ResidualVM")
    platforms = [_("Linux")]  # TODO
    description = _("3D point-and-click adventure games engine")
    runner_executable = "residualvm/residualvm"
    game_options = [
        {
            "option": "game_id",
            "type": "string",
            "label": _("Game identifier")
        },
        {
            "option": "path",
            "type": "directory_chooser",
            "label": _("Game files location")
        },
        {
            "option": "subtitles",
            "label": _("Enable subtitles (if the game has voice)"),
            "type": "bool",
            "default": False,
        },
    ]
    runner_options = [
        {
            "option": "fullscreen",
            "label": _("Fullscreen"),
            "type": "bool",
            "default": False,
        },
        {
            "option": "renderer",
            "label": _("Renderer"),
            "type": "choice",
            "choices": (
                ("OpenGL", "opengl"),
                (_("OpenGL shaders"), "opengl_shaders"),
                (_("Software"), "software"),
            ),
            "default": "opengl",
        },
        {
            "option": "show-fps",
            "label": _("Display FPS information"),
            "type": "bool",
            "default": False,
        },
    ]

    @property
    def game_path(self):
        return self.game_config.get("path")

    def get_residualvm_data_dir(self):
        root_dir = os.path.dirname(self.get_executable())
        return os.path.join(root_dir, "data")

    def play(self):
        command = [
            self.get_executable(),
            "--extrapath=%s" % self.get_residualvm_data_dir(),
            "--themepath=%s" % self.get_residualvm_data_dir(),
        ]

        # Options

        if self.game_config.get("subtitles"):
            command.append("--subtitles")

        if self.runner_config.get("fullscreen"):
            command.append("--fullscreen")
        else:
            command.append("--no-fullscreen")

        renderer = self.runner_config.get("renderer")
        if renderer:
            command.append("--renderer=%s" % renderer)

        if self.runner_config.get("show-fps"):
            command.append("--show-fps")
        else:
            command.append("--no-show-fps")
        # /Options

        command.append("--path=%s" % self.game_path)
        command.append(self.game_config.get("game_id"))

        launch_info = {"command": command}

        return launch_info

    def get_game_list(self):
        """Return the entire list of games supported by ResidualVM."""
        with subprocess.Popen([self.get_executable(), "--list-games"],
                              stdout=subprocess.PIPE, encoding="utf-8", universal_newlines=True) as residualvm_process:
            residual_output = residualvm_process.communicate()[0]
            game_list = str.split(residual_output, "\n")
        game_array = []
        game_list_start = False
        for game in game_list:
            if game_list_start:
                if len(game) > 1:
                    dir_limit = game.index(" ")
                else:
                    dir_limit = None
                if dir_limit is not None:
                    game_dir = game[0:dir_limit]
                    game_name = game[dir_limit + 1:len(game)].strip()
                    game_array.append([game_dir, game_name])
            # The actual list is below a separator
            if game.startswith("-----"):
                game_list_start = True
        return game_array
