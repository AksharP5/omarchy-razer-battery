# Razer Battery for Omarchy

A small mouse icon in the Omarchy bar. Hover for battery percentage and charging status. The icon highlights battery levels at or below 20%. Readings refresh once a minute, or immediately when clicked.

Requires Omarchy's Quickshell plugin system. This does not support older Waybar-based Omarchy installations.

## Install

Install OpenRazer and the headers matching your kernel. For Omarchy's default `linux` kernel:

```sh
omarchy pkg add linux-headers openrazer-daemon
sudo gpasswd -a "$USER" openrazer
```

Use `linux-lts-headers` or `linux-zen-headers` instead if you run that kernel. OpenRazer builds its driver with DKMS. Reconnect your mouse and receiver after installation so the driver and its permissions apply. If your running kernel and installed headers differ, reboot first.

```sh
omarchy plugin add https://github.com/AksharP5/omarchy-razer-battery.git --enable --yes
```

The widget appears on the right by default. To place it immediately left of Radio Atlas, if installed:

```sh
omarchy bar move akshar.razer-battery --before akshar.radio-atlas
```

## Behavior

- A mouse icon with battery percentage and charging status available on hover.
- Low battery uses the current theme's urgent color.
- A dimmed icon means there is no responding mouse or a read failed. Hover for details.
- One reader serves every monitor. Each query has a ten-second timeout.
- Multiple mice appear in the tooltip; the icon highlights when any mouse has low battery and is not charging.
- A receiver with an empty serial response is ignored, avoiding a false 0% when its mouse is off or connected by cable. Two connections reporting the same serial count as one mouse.

Tested with the DeathAdder V3 Pro, USB IDs `1532:00b6` and `1532:00b7`. Other OpenRazer mice exposing the same battery attributes may work, but have not been tested.

The reader uses OpenRazer's `razermouse` driver directly. The `openrazer-daemon` package supplies the driver and udev permission rules; its daemon does not need to run. The plugin only reads battery, charging, name, and serial attributes. Serial numbers stay in memory for deduplication and are not included in its output. It does not change DPI, polling rate, lighting, or mouse settings.

The reader runs as your user through `newgrp openrazer`, so newly added group membership works without logging out. It does not run as root or request administrator access.

## Troubleshooting

```sh
omarchy-shell akshar.razer-battery refresh
omarchy-shell akshar.razer-battery status
```

If the driver is missing, check `dkms status` and reconnect the mouse. If access is denied, confirm `id "$USER"` lists the `openrazer` group. A sleeping mouse may need to be moved before it responds; click the widget to retry. Readings depend on the mouse firmware and OpenRazer driver.

## Development

```sh
python3 -m unittest discover -s tests -v
omarchy plugin validate .
newgrp openrazer -c 'python3 battery.py'
```

Update an installed checkout with `omarchy plugin update akshar.razer-battery`.

MIT licensed. Uses the separately installed [OpenRazer](https://openrazer.github.io/) driver.
