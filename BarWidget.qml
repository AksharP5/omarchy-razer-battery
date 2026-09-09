import QtQuick
import qs.Ui

BarWidget {
  id: root
  moduleName: "akshar.razer-battery"

  readonly property var service: bar?.shell?.serviceFor(moduleName) ?? null
  readonly property var devices: service ? service.devices : []
  readonly property var battery: {
    if (devices.length === 0) return null
    return devices.reduce(function(lowest, device) {
      return device.percentage < lowest.percentage ? device : lowest
    })
  }
  readonly property bool low: battery !== null && !battery.charging && battery.percentage <= 20
  readonly property string detail: {
    if (!service || !service.ready) return "Reading mouse battery..."
    var lines = devices.map(function(device) {
      return device.name + ": " + device.percentage + "%"
        + (device.charging ? " · Charging" : "")
    })
    if (service.error) lines.push(service.error)
    if (lines.length === 0) lines.push("No wireless Razer mouse responding")
    lines.push("Click to refresh")
    return lines.join("\n")
  }

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: (root.vertical ? "Mouse\n" : "Mouse ")
      + (root.battery ? root.battery.percentage + "%" : "?")
      + (root.battery && root.battery.charging ? " \uf0e7" : "")
    active: root.low
    dimmed: root.battery === null
    tooltipText: root.detail
    onPressed: if (root.service) root.service.refresh()
  }
}
