"""
Patch browser-use for OpenRouter compatibility
Based on: https://github.com/browser-use/browser-use/issues/567#issuecomment-2710518976
"""
import os
import re

def patch_message_manager_utils():
    """Patch agent/message_manager/utils.py to detect Gemini/OpenRouter models"""

    # Find browser_use installation
    import browser_use
    browser_use_path = os.path.dirname(browser_use.__file__)
    utils_path = os.path.join(browser_use_path, 'agent', 'message_manager', 'utils.py')

    if not os.path.exists(utils_path):
        print(f"Warning: {utils_path} not found, skipping patch")
        return False

    with open(utils_path, 'r') as f:
        content = f.read()

    # Check if already patched
    if 'OPENROUTER_GEMINI_PATCH' in content:
        print("message_manager/utils.py already patched")
        return True

    # Add detection for Gemini models via OpenRouter
    patch = '''
# OPENROUTER_GEMINI_PATCH: Detect OpenRouter Gemini models
def is_openrouter_gemini(model_name: str) -> bool:
    """Check if model is Gemini via OpenRouter"""
    if isinstance(model_name, str):
        return 'google/gemini' in model_name.lower() or 'gemini-' in model_name.lower()
    return False

'''

    # Insert patch before the first function or class definition
    content = patch + content

    with open(utils_path, 'w') as f:
        f.write(content)

    print(f"✅ Patched {utils_path}")
    return True


def patch_agent_service():
    """Patch agent/service.py to use raw mode for OpenRouter models"""

    import browser_use
    browser_use_path = os.path.dirname(browser_use.__file__)
    service_path = os.path.join(browser_use_path, 'agent', 'service.py')

    if not os.path.exists(service_path):
        print(f"Warning: {service_path} not found, skipping patch")
        return False

    with open(service_path, 'r') as f:
        content = f.read()

    # Check if already patched
    if 'OPENROUTER_PATCH_APPLIED' in content:
        print("agent/service.py already patched")
        return True

    # Find the __init__ method and add detection
    init_patch = '''
        # OPENROUTER_PATCH_APPLIED
        # Detect if using OpenRouter with Gemini
        self._use_raw_mode = False
        if hasattr(llm, 'model'):
            model_name = getattr(llm, 'model', '')
            if isinstance(model_name, str) and 'google/gemini' in model_name.lower():
                print(f"⚠️  Detected OpenRouter Gemini model: {model_name} - using raw response mode")
                self._use_raw_mode = True
'''

    # Insert after self.llm = llm line in __init__
    content = re.sub(
        r'(self\.llm = llm)',
        r'\1' + init_patch,
        content,
        count=1
    )

    with open(service_path, 'w') as f:
        f.write(content)

    print(f"✅ Patched {service_path}")
    return True


if __name__ == '__main__':
    print("Patching browser-use for OpenRouter compatibility...")

    success = True
    success &= patch_message_manager_utils()
    success &= patch_agent_service()

    if success:
        print("\n✅ All patches applied successfully!")
        print("browser-use is now compatible with OpenRouter Gemini models")
    else:
        print("\n⚠️  Some patches failed - check warnings above")
        exit(1)
