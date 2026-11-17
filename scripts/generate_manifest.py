import json

def main():
    with open('ml/data/test_manifest.json', 'r') as f:
        tm = json.load(f)

    manifest = {
        'version': '2.0.0',
        'project': 'AI-Powered Road and Infrastructure Damage Detection and Severity Assessment',
        'total_records': len(tm.get('images', [])),
        'splits': tm.get('split_counts', {}),
        'countries': tm.get('country_counts', {}),
        'records': []
    }

    for img in tm.get('images', []):
        rec = {
            'file': img.get('filename'),
            'source': img.get('source'),
            'country': img.get('country'),
            'licence': img.get('license'),
            'sha256': img.get('sha256'),
            'labels': ['defect'] if img.get('has_defect') else ['clean_negative'],
            'tags': img.get('tags', []),
            'synthetic': False
        }
        manifest['records'].append(rec)

    with open('ml/data/manifest.json', 'w') as out:
        json.dump(manifest, out, indent=2)

    print(f"Successfully generated ml/data/manifest.json with {len(manifest['records'])} entries.")

if __name__ == '__main__':
    main()
