"""
Build script for creating Tasky executable.
"""
import os
import sys
import subprocess
import shutil


def main():
    """Build the executable."""
    print("=" * 60)
    print("🔨 Building Tasky Executable")
    print("=" * 60)
    print()
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed")
    
    print()
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    print()
    
    # Run PyInstaller
    print("🔨 Building executable...")
    print()
    
    result = subprocess.run([
        sys.executable,
        "-m",
        "PyInstaller",
        "tasky.spec",
        "--clean"
    ])
    
    if result.returncode == 0:
        print()
        print("=" * 60)
        print("✅ Build successful!")
        print("=" * 60)
        print()
        print("📦 Executable location: dist/Tasky.exe" if sys.platform == "win32" else "dist/Tasky")
        print()
        print("📝 Next steps:")
        print("1. Copy the executable to your desired location")
        print("2. Make sure .env file is in the same directory")
        print("3. Run the executable")
        print()
        print("⚠️  Note: The executable includes all dependencies")
        print("   but you still need:")
        print("   - .env file with your tokens")
        print("   - ngrok (if not using custom webhook URL)")
        print()
    else:
        print()
        print("=" * 60)
        print("❌ Build failed!")
        print("=" * 60)
        print()
        print("Check the error messages above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()

