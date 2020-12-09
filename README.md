# PKBrightness
Python daemon script for dimming keyboard when not active - monitors both keyboard and mouse

## Motivation
In Windows, there are some services running in the background monitoring
whether the system is active or idle. In Linux, due to the non-proper support
from the vendors, there is no such feature.

This project aims to create a simple daemon that is running in the background
monitoring if the system is idle or not, dimming the keyboard when necessary
for saving power.

## Installation
There is no package available at PyPi, but it can be installed directly
from Github and (almost) without root permissions.

First, the following packages are required:

```shell
sudo apt install python3 python3-pip python3-dbus upower
```

Additionally, you can opt for installing `git` so if there is any updates
those can be easily applied.

Then, we need to download the repository. We will use the `home` folder
as the default location:

```shell
cd && git clone https://github.com/Javinator9889/PKBrightness.git
```

Inside the downloaded folder (`PKBrightness`), we have to install the
required dependencies:

```shell
pip3 install -r requirements.txt
```

After all this process, you will notice there is a file called
`pkbrightness.service`. This file consists on a SystemD service which will
manage the entire service and process for us, without the need of root
permissions.

 + Firstly, edit that file and change all `YOUR_USER` occurrences with your
   Unix user.
 + Create a copy of that file at your user SystemD service folder as follows:
```shell
cp pkbrightness.service ~/.config/systemd/user
```
 + Enable the just created service with the following commands:
```shell
systemctl --user daemon-reload
systemctl --user enable --now pkbrightness.service
systemctl --user status pkbrightness.service
```

The output for the latest command would be:
```shell
 systemctl --user status pkbrightness.service 
● pkbrightness.service - Keyboard brightness service
     Loaded: loaded (/home/YOUR_USER/.config/systemd/user/pkbrightness.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2020-12-09 13:22:47 CET; 12min ago
    Process: 297077 ExecStart=/usr/bin/python3 /home/YOUR_USER/PKBrightness/pkbrightness.py --config /home/YOUR_USER/.config/pkg/pkg.conf (code=exited, status=0/SUCCESS)
   Main PID: 297079 (python3)
     CGroup: /user.slice/user-1000.slice/user@1000.service/pkbrightness.service
             └─297079 /usr/bin/python3 /home/YOUR_USER/PKBrightness/pkbrightness.py --config /home/YOUR_USER/.config/pkg/pkg.conf

dic 09 13:22:47 systemd[7535]: Starting Keyboard brightness service...
dic 09 13:22:47 pkbrightness[297079]: Starting daemon.
dic 09 13:22:47 systemd[7535]: Started Keyboard brightness service.
```

### *Disclaimer*
As you may seen, the script relies on system Python 3 version. This 
requirement is mandatory: the `dbus` interface is only provided to
system version of Python 3.

In addition, at least Python 3.6 is required. A possible future addition
would be the inclusion of lower Python versions (but all of them based
on Python 3).

## Uninstall
Removing the service is as simple as executing:
```shell
systemctl --user stop pkbrightness.service
systemctl --user disable pkbrightness.service
rm -rf ~/PKBrightness
rm -r ~/.config/systemd/user/pkbrightness.service
```

This way, the service will stop and will be removed from the system.

If you just want to stop and/or restart the service, execute:
```shell
systemctl --user stop pkbrightness.service  # for stopping it
systemctl --user restart pkbrightness.service  # for restarting it (i.e.: config changes)
```

## Upgrading
If there is any new release available, with just a command the service
can be updated:
```shell
cd ~/PKBrightness && git pull
```

Then, restart the SystemD service:
```shell
systemctl --user restart pkbrightness.service
```

**Note:** if there are any changes in the `.service` file, you will need
to do again the steps explained before substituting `YOUR_USER` with your
Unix username and replacing the old service with the new one. Then,
reload the SystemD daemon:
```shell
systemctl --user daemon-reload
```

## License
```
                                PKBrightness
                    Copyright (C) 2020  Javinator9889

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
```
