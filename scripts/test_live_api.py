import urllib.request
import urllib.error
import json
import os

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'

def upload_file(path, conf=0.40):
    with open(path, 'rb') as f:
        file_bytes = f.read()
    filename = os.path.basename(path)
    
    body = bytearray()
    body.extend(f'--{boundary}\r\n'.encode())
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode())
    body.extend(b'Content-Type: image/jpeg\r\n\r\n')
    body.extend(file_bytes)
    body.extend(b'\r\n')
    body.extend(f'--{boundary}--\r\n'.encode())
    
    url = f'http://localhost:8000/api/v1/infer?conf_thresh={conf}'
    req = urllib.request.Request(
        url,
        data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return resp.status, data
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

cases = [
    'eval_failures/case_01_pothole_nh44.jpg',
    'eval_failures/case_02_civil_distress_diagram.jpg',
    'eval_failures/case_03_alligator_cracks.jpg',
    'eval_failures/case_04_bengaluru_potholes.jpg',
    'eval_failures/case_05_asphalt_crater.jpg'
]

for c in cases:
    status, res = upload_file(c)
    print(f'=== Case: {c} ===')
    print(f'Status: {status}')
    if status == 200:
        dets = res.get('detections', [])
        print(f'Total defects: {res.get("total_defects")}, Potholes: {res.get("pothole_count")}, Cracks: {res.get("crack_count")}')
        for d in dets:
            box = d.get('box') # [x%, y%, w%, h%]
            label = d.get('label')
            conf = d.get('confidence')
            sev = d.get('severity')
            print(f'  - {label} (conf={conf:.3f}, box=[x={box[0]}%, y={box[1]}%, w={box[2]}%, h={box[3]}%], sev={sev})')
    else:
        print(f'Response: {res[:250]}')
