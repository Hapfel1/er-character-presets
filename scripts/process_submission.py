#!/usr/bin/env python3
"""Process a preset submission from GitHub issue."""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


def process_submission(name, author, description, tags, json_file, screenshot_file):
    """
    Process a new preset submission.
    
    Args:
        name: Preset name
        author: GitHub username
        description: Preset description
        tags: Comma-separated tags
        json_file: Path to exported JSON
        screenshot_file: Path to screenshot
        
    Returns:
        True if successful
    """
    print(f"Processing submission: {name} by {author}")
    
    # Load user's exported JSON
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            user_export = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load JSON: {e}")
        return False
    
    # Validate it has appearance data
    if 'appearance' not in user_export:
        print("ERROR: JSON missing 'appearance' field")
        print("Expected format: { 'appearance': { ... }, ... }")
        return False
    
    print("✓ JSON valid")
    
    # Load current index
    if not Path('index.json').exists():
        print("ERROR: index.json not found. Run from repo root!")
        return False
        
    with open('index.json', 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    # Generate new ID
    existing_ids = []
    for p in index['presets']:
        try:
            num = int(p['id'].split('_')[1])
            existing_ids.append(num)
        except:
            pass
    
    next_id = max(existing_ids) + 1 if existing_ids else 1
    preset_id = f"preset_{next_id:03d}"
    
    print(f"✓ Generated ID: {preset_id}")
    
    # Create preset JSON
    preset_data = {
        'id': preset_id,
        'name': name,
        'author': author,
        'description': description,
        'tags': [t.strip() for t in tags.split(',')],
        'appearance': user_export['appearance'],  # Copy appearance data
        'screenshot_url': f'presets/{preset_id}.png',
        'downloads': 0,
        'created': datetime.now().strftime('%Y-%m-%d')
    }
    
    # Save preset JSON
    presets_dir = Path('presets')
    presets_dir.mkdir(exist_ok=True)
    
    preset_path = presets_dir / f'{preset_id}.json'
    with open(preset_path, 'w', encoding='utf-8') as f:
        json.dump(preset_data, f, indent=2)
    
    print(f"✓ Created {preset_path}")
    
    # Copy screenshot
    screenshot_dest = presets_dir / f'{preset_id}.png'
    shutil.copy(screenshot_file, screenshot_dest)
    print(f"✓ Copied screenshot to {screenshot_dest}")
    
    # Update index
    index_entry = {
        'id': preset_id,
        'name': name,
        'author': author,
        'description': description,
        'tags': preset_data['tags'],
        'data_url': f'presets/{preset_id}.json',
        'screenshot_url': f'presets/{preset_id}.png',
        'downloads': 0,
        'created': preset_data['created']
    }
    
    index['presets'].append(index_entry)
    index['last_updated'] = datetime.now().isoformat()
    
    with open('index.json', 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)
    
    print(f"✓ Updated index.json")
    
    print("\n" + "="*60)
    print(f"SUCCESS! Added preset {preset_id}: {name}")
    print("="*60)
    print("\nNext steps:")
    print(f"  git add index.json presets/{preset_id}.*")
    print(f"  git commit -m 'Add preset: {name} by {author}'")
    print(f"  git push")
    print("\nPreset will be live immediately after push!")
    
    return True


def main():
    if len(sys.argv) != 7:
        print("Elden Ring Character Preset Submission Processor")
        print("="*60)
        print("\nUsage:")
        print("  python process_submission.py <name> <author> <desc> <tags> <json> <screenshot>")
        print("\nExample:")
        print("  python process_submission.py \\")
        print("    'Malenia Cosplay' \\")
        print("    'github_username' \\")
        print("    'Accurate Malenia recreation' \\")
        print("    'cosplay,female,redhead' \\")
        print("    ~/Downloads/character.json \\")
        print("    ~/Downloads/screenshot.png")
        print("\nArguments:")
        print("  name:       Display name for the preset")
        print("  author:     GitHub username of submitter")
        print("  desc:       Description of the character")
        print("  tags:       Comma-separated tags (cosplay,male,female,etc)")
        print("  json:       Path to exported JSON from tool")
        print("  screenshot: Path to screenshot PNG")
        sys.exit(1)
    
    success = process_submission(
        sys.argv[1],  # name
        sys.argv[2],  # author
        sys.argv[3],  # description
        sys.argv[4],  # tags
        sys.argv[5],  # json file
        sys.argv[6],  # screenshot
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
