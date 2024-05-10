#! /usr/bin/env python3
# Sony actioncam videoclip import

import shutil
import os
from tqdm import tqdm

source = 'D:/PRIVATE/M4ROOT/CLIP/C0003.MP4'
destination = 'c:/Data/Sony/X3000/C001.mp4'

size = os.stat(source).st_size

tqdm_params = {
    'desc': destination,
    'total': size,
    'miniters': 1,
    'unit': 'B',
    'unit_scale': True,
    'unit_divisor': 1024,
}
with tqdm(**tqdm_params) as pb:
    downloaded = r.num_bytes_downloaded
    async for chunk in r.aiter_bytes():
        pb.update(r.num_bytes_downloaded - downloaded)
        f.write(chunk)
        downloaded = r.num_bytes_downloaded
