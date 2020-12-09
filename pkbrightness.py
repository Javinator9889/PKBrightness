#!/usr/bin/python3
#                             PKBrightness
#                  Copyright (C) 2020 - Javinator9889
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#                   (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#               GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
import os
import dbus
import argparse
import traceback
import configparser
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from dataclasses import dataclass
from daemonize import Daemonize
from pynput import mouse, keyboard
from typing import Union
from threading import Lock, Timer

# Init DBus main loop for signal handling
DBusGMainLoop(set_as_default=True)


@dataclass
class MouseInteractionOptions:
    on_move: bool
    on_click: bool
    on_scroll: bool


@dataclass
class Config:
    pid_file: str
    dim_time: int
    mouse_interactions: MouseInteractionOptions


class InteractionHandler:
    def __init__(self, config: Config):
        self.config = config
        self.lock = Lock()
        self.timeout = None
        self.mouse_listener = None
        self.kbd_listener = None
        self.bus = dbus.SystemBus()
        self.backlight_manager = dbus.Interface(
            self.bus.get_object('org.freedesktop.UPower',
                                '/org/freedesktop/UPower/KbdBacklight'),
            'org.freedesktop.UPower.KbdBacklight'
        )
        self.current = self.backlight_manager.GetBrightness()
        self.maximum = self.backlight_manager.GetMaxBrightness()
        self.backlight_manager.connect_to_signal(
            'BrightnessChangedWithSource',
            self.on_brightness_changed
        )

    def on_interaction(self, *args, **kwargs):
        self._set_brightness(self.current)
        self._update_timeout()

    def on_brightness_changed(self, value: dbus.Int32, source: dbus.String):
        # HW brightness changed
        if source == 'internal':
            with self.lock:
                self.current = value
            self._update_timeout()

    def setup_listeners(self):
        move_listener = self.on_interaction \
            if self.config.mouse_interactions.on_move \
            else None
        click_listener = self.on_interaction \
            if self.config.mouse_interactions.on_click \
            else None
        scroll_listener = self.on_interaction \
            if self.config.mouse_interactions.on_scroll \
            else None
        self.mouse_listener = mouse.Listener(
            on_move=move_listener,
            on_click=click_listener,
            on_scroll=scroll_listener
        )
        self.kbd_listener = keyboard.Listener(
            on_press=self.on_interaction,
            on_release=self.on_interaction
        )
        self.mouse_listener.start()
        self.kbd_listener.start()
        self._update_timeout()

    def _update_timeout(self):
        with self.lock:
            if self.timeout is not None:
                self.timeout.cancel()
            self.timeout = Timer(self.config.dim_time,
                                 self._set_brightness, args=(0,))
            self.timeout.start()

    def _set_brightness(self, brightness_level: Union[int, dbus.Int32]):
        with self.lock:
            self.backlight_manager.SetBrightness(brightness_level)


def load_config(
        filename: str = os.path.expanduser('~/.config/pkb/pkb.conf')) -> Config:
    config = configparser.ConfigParser(allow_no_value=False)

    if not os.path.exists(filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        config['System'] = {
            'pid file': os.path.expanduser('~/.config/pkb/pkb.pid'),
        }
        config['Mouse.Interactions'] = {
            'on move': False,
            'on click': True,
            'on scroll': True
        }
        config['Keyboard options'] = {'dim time': 20}

        with open(filename, 'w') as configfile:
            config.write(configfile)

    config.read(filename, encoding='utf-8')
    pid_file = config['System']['pid file']
    dim_time = config.getint('Keyboard options', 'dim time')
    mouse_interactions = MouseInteractionOptions(
        config['Mouse.Interactions'].getboolean('on move'),
        config['Mouse.Interactions'].getboolean('on click'),
        config['Mouse.Interactions'].getboolean('on scroll')
    )

    return Config(pid_file, dim_time, mouse_interactions)


def main(exec_config):
    try:
        handler = InteractionHandler(exec_config)
        handler.setup_listeners()
        loop = GLib.MainLoop()
        loop.run()
    except KeyboardInterrupt:
        loop.quit()
        exit(0)
    except Exception as e:
        print(f"Unexpected error {e}!")
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Daemon that dims the keyboard when inactive')
    parser.add_argument('--config',
                        type=str,
                        default=os.path.expanduser('~/.config/pkb/pkb.conf'),
                        help='Configuration file',
                        required=False)
    args = parser.parse_args()
    config = load_config(args.config)
    main(config)
    daemon = Daemonize(app='pkbrightness',
                       pid=config.pid_file,
                       action=lambda: main(config))
    daemon.start()
