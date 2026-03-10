import numpy as np
from scripts.tracking import VehicleTracker

tracker = VehicleTracker()
frame = np.full((480, 640, 3), 128, dtype=np.uint8)
dets = [{'bbox': (100, 120, 220, 260), 'confidence': 0.9, 'class': 'car'}]

tracks1 = tracker.update(dets, frame)
tracks2 = tracker.update([], frame)
tracks3 = tracker.update(dets, frame)

print('tracks1_len', len(tracks1))
print('tracks1_confirmed', [t.get('is_confirmed') for t in tracks1])
print('tracks2_len', len(tracks2))
print('tracks2_confirmed', [t.get('is_confirmed') for t in tracks2])
print('tracks3_len', len(tracks3))
print('tracks3_confirmed', [t.get('is_confirmed') for t in tracks3])
