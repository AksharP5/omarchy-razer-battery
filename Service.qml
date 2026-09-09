import QtQuick
import Quickshell
import Quickshell.Io

Item {
  id: root

  property var shell: null
  property var devices: []
  property string error: ""
  property bool ready: false

  function refresh() {
    if (!reader.running) reader.running = true
  }

  function status() {
    return JSON.stringify({ devices: devices, error: error, ready: ready })
  }

  // newgrp picks up membership immediately, including before the first logout.
  readonly property string readerCommand: "exec python3 '"
    + decodeURIComponent(Qt.resolvedUrl("battery.py").toString().replace(/^file:\/\//, ""))
      .replace(/'/g, "'\\''") + "'"

  Process {
    id: reader
    command: ["timeout", "10s", "newgrp", "openrazer", "-c", root.readerCommand]
    stdout: StdioCollector { id: output }
    stderr: StdioCollector { id: errors }
    onExited: function(exitCode) {
      root.ready = true
      if (exitCode !== 0) {
        root.devices = []
        root.error = exitCode === 124 ? "Battery query timed out."
          : errors.text.trim() || "Battery reader failed with exit code " + exitCode + "."
        return
      }
      try {
        var result = JSON.parse(output.text)
        root.devices = result.devices
        root.error = result.error
      } catch (error) {
        root.devices = []
        root.error = "Cannot read battery response: " + error
      }
    }
  }

  Timer {
    interval: 60000
    running: true
    repeat: true
    triggeredOnStart: true
    onTriggered: root.refresh()
  }

  IpcHandler {
    target: "akshar.razer-battery"
    function refresh(): void { root.refresh() }
    function status(): string { return root.status() }
  }
}
