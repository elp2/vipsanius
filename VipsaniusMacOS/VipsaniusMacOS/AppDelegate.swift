import Cocoa

class AppDelegate: NSObject, NSApplicationDelegate {
    var statusItem: NSStatusItem?
    var executor: PythonExecutor?

    func applicationDidFinishLaunching(_ notification: Notification) {
        executor = PythonExecutor()
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        if let button = statusItem?.button {
            button.image = NSImage(named: "tray_icon")
            button.image?.isTemplate = true
        }
        
        let menu = NSMenu()
        for name in executor!.getConfig().keys {
            let menuItem = NSMenuItem(title: "Unblock " + name, action: #selector(unblockSelected), keyEquivalent: "")
            menuItem.representedObject = name
            menu.addItem(menuItem)
        }

        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Quit", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q"))
        statusItem?.menu = menu
    }

    @objc func unblockSelected(_ sender: NSMenuItem) {
        if let name = sender.representedObject as? String {
            executor!.unblock(name: name)
        }
    }
}
