import requests, os

samples = [
    ('bengaluru_potholes.jpg', 'balanced', 'web/public/samples/bengaluru_potholes.jpg'),
    ('asphalt_crater.jpg', 'balanced', 'web/public/samples/asphalt_crater.jpg'),
    ('alligator_cracks.jpg', 'balanced', 'web/public/samples/alligator_cracks.jpg'),
    ('mumbai_potholes.avif (Balanced)', 'balanced', 'web/public/samples/mumbai_potholes.avif'),
    ('mumbai_potholes.avif (High Recall)', 'high_recall', 'web/public/samples/mumbai_potholes.avif'),
    ('mumbai_potholes.avif (High Precision)', 'high_precision', 'web/public/samples/mumbai_potholes.avif'),
    ('pothole_nh44.jpg', 'balanced', 'web/public/samples/pothole_nh44.jpg'),
    ('clean_road.jpg', 'balanced', 'web/public/samples/clean_road.jpg'),
    ('civil_distress_diagram.jpg', 'balanced', 'web/public/samples/civil_distress_diagram.jpg'),
    ('user_tested_potholes.jpg', 'balanced', 'eval_failures/case_07_user_tested_potholes.jpg'),
]

print('=== TESTING ALL LIVE SAMPLES VIA VITE PROXY (PORT 3000) ===')
for name, preset, path in samples:
    if not os.path.exists(path):
        print('MISSING:', path)
        continue
    with open(path, 'rb') as f:
        conf = 0.15 if preset == 'high_recall' else (0.40 if preset == 'high_precision' else 0.25)
        url = f'http://localhost:3000/api/v1/infer?conf_thresh={conf}&preset={preset}'
        res = requests.post(url, files={'file': (os.path.basename(path), f, 'image/jpeg')})
        if res.status_code == 200:
            d = res.json()
            tot = d.get('total_defects')
            p = d.get('pothole_count')
            c = d.get('crack_count')
            print(f'PASS: {name:<35} -> 200 OK | defects={tot} (potholes={p}, cracks={c})')
        elif res.status_code == 422:
            detail = res.json().get('detail')
            print(f'PASS (REJECTED): {name:<24} -> 422 Rejection | {detail}')
        else:
            print(f'FAIL: {name:<35} -> {res.status_code}: {res.text}')