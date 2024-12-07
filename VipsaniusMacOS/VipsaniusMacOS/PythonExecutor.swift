import Foundation

class PythonExecutor {
    private func getConfigString() -> String {
        let maybeConfig = executeCommand(arguments: ["config"])
        if let config = maybeConfig {
            print("Got config:", config)
            return config
        }
        return ""
    }
    
    func getConfig() -> [String: [String]] {
        if let jsonData = getConfigString().data(using: .utf8) {
            do {
                // Decode the JSON into a dictionary
                let config = try JSONDecoder().decode([String: [String]].self, from: jsonData)
                return config
            } catch {
                print("Failed to decode JSON: \(error)")
            }
        }
        return [String: [String]]()
    }
    
    func unblock(name: String) {
        print("Unblocking " + name)
        executeCommand(arguments: ["temp_unblock", name])
    }
    
    private func executeCommand(arguments: [String] = []) -> String? {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        process.arguments = ["python3", "/Users/edwardpalmer/dev/vipsanius/core/block_sites.py"] + arguments
        
        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = pipe
        
        do {
            try process.run()
            process.waitUntilExit()
            
            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            return String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines)
        } catch {
            print("Error executing command: \(error)")
            return nil
        }
    }
}
