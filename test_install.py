#!/usr/bin/env python3
"""Test script to verify the package installed correctly."""

def test_import():
    """Test that the package can be imported."""
    try:
        import gambit_template
        print("✓ Package imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        return False

def test_extension():
    """Test that the C extension is accessible."""
    try:
        import gambit_template
        # Try to access something from your C extension
        # Adjust based on what your extension exports
        attrs = dir(gambit_template)
        print(f"✓ Extension loaded with {len(attrs)} attributes")
        print(f"  Available: {attrs}")
        return True
    except Exception as e:
        print(f"✗ Extension test failed: {e}")
        return False

def test_version():
    """Test that version is set correctly."""
    try:
        import gambit_template
        version = getattr(gambit_template, '__version__', None)
        if version:
            print(f"✓ Version: {version}")
        else:
            print("⚠ No version attribute found")
        return True
    except Exception as e:
        print(f"✗ Version test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing gambit-template installation...\n")
    
    results = [
        test_import(),
        test_extension(),
        test_version(),
    ]
    
    if all(results):
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed")
        exit(1)