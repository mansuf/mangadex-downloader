# MIT License

# Copyright (c) 2022-present Rahman Yusuf

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import os
import platform
import threading
from pathlib import Path
from typing import List

try:
    import cv2
    import torch
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer
    REALESRGAN_AVAILABLE = True
except ImportError:
    REALESRGAN_AVAILABLE = False

log = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

MODEL_HASHES = {
    'RealESRGAN_x2plus.pth': '49fafd45f8fd7aa8d31ab2a22d14d91b536c34494a5cfe31eb5d89c2fa266abb',
    'RealESRGAN_x4plus_anime_6B.pth': 'f872d837d3c90ed2e05227bed711af5671a6fd1c9f7d7e91c911a61f155e99da'
}


class Upscaler:
    def __init__(self, scale: int = 4):
        if not REALESRGAN_AVAILABLE:
            raise ImportError(
                "Real-ESRGAN dependencies not installed. "
                "Install with: pip install mangadex-downloader[optional]"
            )

        self.scale = scale
        self.upsampler = None
        self._shutdown_event = threading.Event()

        self._init_model()

    def _init_model(self):
        if self.scale not in [2, 4]:
            raise ValueError(
                f"Unsupported scale factor: {self.scale}. "
                f"PyTorch upscaler supports: 2, 4"
            )

        if self.scale == 2:
            model_name = 'RealESRGAN_x2plus.pth'
            model_scale = 2
            num_block = 23
        else:
            model_name = 'RealESRGAN_x4plus_anime_6B.pth'
            model_scale = 4
            num_block = 6

        model = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=num_block,
            num_grow_ch=32,
            scale=model_scale
        )

        if torch.cuda.is_available():
            device = torch.device('cuda')
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = torch.device('mps')
        else:
            device = torch.device('cpu')

        model_path = os.path.join(
            os.path.dirname(__file__),
            'models',
            model_name
        )

        if not os.path.exists(model_path):
            log.warning(
                f"Model not found at {model_path}. "
                "Downloading from official repository..."
            )
            self._download_model(model_path)

        self.upsampler = RealESRGANer(
            scale=model_scale,
            model_path=model_path,
            model=model,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=True if device.type == 'cuda' else False,
            device=device,
            dni_weight=None
        )

        # Store metadata for marker
        self._model_name = model_name
        self._device = str(device)

        log.info(f"Real-ESRGAN initialized (scale={self.scale}x, device={device}, model={model_name})")

    def _download_model(self, model_path: str):
        import urllib.request
        from tqdm import tqdm

        model_dir = os.path.dirname(model_path)
        os.makedirs(model_dir, exist_ok=True)

        model_name = os.path.basename(model_path)

        if model_name == 'RealESRGAN_x2plus.pth':
            url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth"
        else:
            url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth"

        log.info(f"Downloading Real-ESRGAN model from {url}...")
        
        with tqdm(unit='B', unit_scale=True, unit_divisor=1024, 
                  miniters=1, desc=f"Downloading {model_name}") as pbar:
            def reporthook(block_num, block_size, total_size):
                if pbar.total is None and total_size > 0:
                    pbar.total = total_size
                downloaded = block_num * block_size
                if downloaded <= total_size:
                    pbar.update(block_size)
            
            urllib.request.urlretrieve(url, model_path, reporthook=reporthook)

        import hashlib

        expected_hash = MODEL_HASHES.get(model_name)
        if expected_hash:
            hasher = hashlib.sha256()
            with open(model_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            downloaded_hash = hasher.hexdigest()

            if downloaded_hash.lower() != expected_hash.lower():
                os.remove(model_path)
                raise RuntimeError(
                    f"Model integrity check failed for {model_name}. "
                    f"Expected SHA256: {expected_hash}, got: {downloaded_hash}"
                )

            log.debug(f"Model integrity check passed for {model_name}")

        log.info(f"Model downloaded to {model_path}")

    def _is_image(self, path: Path) -> bool:
        return path.suffix.lower() in IMAGE_EXTENSIONS

    def _is_memory_error(self, error: Exception) -> bool:
        error_msg = str(error).lower()
        return ("out of memory" in error_msg or
                "cuda out of memory" in error_msg or
                "mps backend out of memory" in error_msg)

    def _get_marker_path(self, image_path: str) -> str:
        return f"{image_path}.upscaled"

    def shutdown(self):
        """Signal upscaler to stop processing"""
        self._shutdown_event.set()

    def _mark_as_upscaled(self, image_path: str, source_hash: str):
        from .format.utils import create_file_hash_sha256

        img_hash = create_file_hash_sha256(image_path)
        marker = self._get_marker_path(image_path)
        with open(marker, 'w') as f:
            f.write(
                f"scale={self.scale}\nmodel={getattr(self, '_model_name', 'unknown')}\ndevice={getattr(self, '_device', 'unknown')}\nhash={img_hash}\nsource_hash={source_hash}\n"
            )

    def _is_already_upscaled(self, image_path: str) -> bool:
        from .format.utils import create_file_hash_sha256

        marker = self._get_marker_path(image_path)
        if not os.path.exists(marker):
            return False

        try:
            with open(marker, 'r') as f:
                content = f.read()

            # Check scale
            if f"scale={self.scale}" not in content:
                return False

            # Check hash
            stored_hash = None
            for line in content.splitlines():
                if line.startswith("hash="):
                    stored_hash = line.split("=", 1)[1]
                    break

            if not stored_hash:
                return False

            # Validate current hash
            current_hash = create_file_hash_sha256(image_path)
            if current_hash != stored_hash:
                log.debug(f"Hash mismatch for {image_path}, removing marker (stored={stored_hash[:8]}..., current={current_hash[:8]}...)")
                os.remove(marker)
                return False

            return True
        except Exception:
            return False

    def _upscale_single_image(self, input_path: str):
        if self._is_already_upscaled(input_path):
            filename = os.path.basename(input_path)
            log.info(f"Already upscaled: {filename}")
            return (input_path, True)

        from .format.utils import create_file_hash_sha256
        source_hash = create_file_hash_sha256(input_path)

        img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)

        if img is None:
            log.warning(f"Failed to read image: {input_path}")
            return (input_path, False, False)

        try:
            output, _ = self.upsampler.enhance(img, outscale=self.scale)

            # Improve JPEG quality slightly; keep defaults for PNG/WEBP
            ext = os.path.splitext(input_path)[1].lower()
            if ext in ('.jpg', '.jpeg'):
                cv2.imwrite(input_path, output, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            else:
                cv2.imwrite(input_path, output)
            self._mark_as_upscaled(input_path, source_hash)

            filename = os.path.basename(input_path)
            log.info(f"Upscaled: {filename}")

            return (input_path, True)
        except Exception as e:
            log.error(f"Error upscaling {input_path}: {e}")
            return (input_path, False)

    def process_images(self, image_paths: List[str]) -> List[str]:
        if not image_paths:
            return []

        valid_images = [
            img for img in image_paths
            if self._is_image(Path(img))
        ]

        if not valid_images:
            log.debug("No valid images to upscale")
            return image_paths

        log.info(f"Upscaling {len(valid_images)} images with Real-ESRGAN (scale={self.scale}x)...")

        failed = []

        try:
            for img in valid_images:
                if self._shutdown_event.is_set():
                    log.info("Upscale cancelled by user")
                    break

                path, success = self._upscale_single_image(img)
                if not success:
                    failed.append(path)

        except KeyboardInterrupt:
            log.info("Upscale interrupted, cancelling pending operations...")
            self._shutdown_event.set()
            raise

        total_failed = len(failed)
        total_success = len(valid_images) - total_failed

        if total_failed > 0:
            log.warning(
                f"Upscale completed: {total_success} successful, "
                f"{total_failed} failed"
            )
        else:
            log.info(f"Successfully upscaled {total_success} images with Real-ESRGAN")

        return image_paths


def create_upscaler(scale: int = 2):
    if platform.system() == 'Darwin':
        from .upscale_coreml import CoreMLUpscaler
        return CoreMLUpscaler(scale)
    else:
        return Upscaler(scale)
