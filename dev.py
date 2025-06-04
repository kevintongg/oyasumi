#!/usr/bin/env python3
"""
Development script for Oyasumi Discord Bot
Automatically restarts the bot when Python files are modified
"""

import sys
import time
import subprocess
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set proper encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

class BotRestartHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.restart_timer = None
        self.start_bot()

    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return

        # Only restart on Python file changes
        if not event.src_path.endswith('.py'):
            return

        # Ignore temporary files and cache
        if any(ignore in event.src_path for ignore in ['__pycache__', '.pyc', '~', '#']):
            return

        try:
            print(f"\n📝 File changed: {event.src_path}")
        except UnicodeEncodeError:
            print(f"\nFile changed: {event.src_path}")
        self.schedule_restart()

    def schedule_restart(self):
        """Schedule a restart with debouncing to avoid multiple rapid restarts"""
        if self.restart_timer:
            self.restart_timer.cancel()

        self.restart_timer = threading.Timer(1.0, self.restart_bot)
        self.restart_timer.start()

    def start_bot(self):
        """Start the bot process"""
        try:
            print("🌙 Starting Oyasumi Discord Bot (Development Mode)...")
            print("📁 Watching for file changes in src/ directory")
            print("🔄 Bot will auto-restart when you modify Python files")
            print("❌ Press Ctrl+C to stop the development server")
        except UnicodeEncodeError:
            print("Starting Oyasumi Discord Bot (Development Mode)...")
            print("Watching for file changes in src/ directory")
            print("Bot will auto-restart when you modify Python files")
            print("Press Ctrl+C to stop the development server")
        print("-" * 60)

        try:
            self.process = subprocess.Popen(
                [sys.executable, "run.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )

            # Stream output in real-time
            def stream_output():
                if self.process and self.process.stdout:
                    for line in iter(self.process.stdout.readline, ''):
                        if line.strip():
                            try:
                                print(line.rstrip())
                            except UnicodeEncodeError:
                                print(line.encode('ascii', 'replace').decode('ascii').rstrip())

            threading.Thread(target=stream_output, daemon=True).start()

        except Exception as e:
            try:
                print(f"❌ Failed to start bot: {e}")
            except UnicodeEncodeError:
                print(f"Failed to start bot: {e}")

    def restart_bot(self):
        """Restart the bot process"""
        try:
            print("\n🔄 Restarting bot...")
        except UnicodeEncodeError:
            print("\nRestarting bot...")

        # Stop current process
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            except Exception as e:
                try:
                    print(f"⚠️ Error stopping bot: {e}")
                except UnicodeEncodeError:
                    print(f"Error stopping bot: {e}")

        # Start new process
        time.sleep(0.5)  # Brief pause
        self.start_bot()

    def stop(self):
        """Clean shutdown"""
        if self.restart_timer:
            self.restart_timer.cancel()

        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            except Exception:
                pass


def main():
    """Main development server"""
    # Watch the src directory for changes
    watch_path = Path('./src')

    if not watch_path.exists():
        try:
            print("❌ src/ directory not found!")
        except UnicodeEncodeError:
            print("src/ directory not found!")
        return

    # Set up file watcher
    event_handler = BotRestartHandler()
    observer = Observer()
    observer.schedule(event_handler, str(watch_path), recursive=True)
    observer.schedule(event_handler, '.', recursive=False)  # Watch root for run.py changes

    try:
        observer.start()

        # Keep the script running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        try:
            print("\n\n👋 Shutting down development server...")
        except UnicodeEncodeError:
            print("\n\nShutting down development server...")
        event_handler.stop()
        observer.stop()

    observer.join()
    try:
        print("✅ Development server stopped")
    except UnicodeEncodeError:
        print("Development server stopped")


if __name__ == "__main__":
    main()
