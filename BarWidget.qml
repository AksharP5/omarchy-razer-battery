import QtQuick
import qs.Ui

BarWidget {
  id: root
  moduleName: "akshar.razer-battery"

  readonly property var service: bar?.shell?.serviceFor(moduleName) ?? null
  readonly property var devices: service ? service.devices : []
  readonly property bool low: devices.some(function(device) {
    return !device.charging && device.percentage <= 20
  })
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

  BarIconButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: "\udb80\udf7d"
    active: root.low
    dimmed: root.devices.length === 0
    tooltipText: root.detail
    onPressed: if (root.service) root.service.refresh()
  }
}
