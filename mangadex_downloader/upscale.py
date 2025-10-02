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
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
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


class Upscaler:
    def __init__(self, scale: int = 2, concurrency: int = 2):
        if not REALESRGAN_AVAILABLE:
            raise ImportError(
                "Real-ESRGAN dependencies not installed. "
                "Install with: pip install mangadex-downloader[optional]"
            )

        self.scale = scale
        self.concurrency = concurrency
        self.upsampler = None
        self._shutdown_event = threading.Event()

        self._init_model()

    def _init_model(self):
        if self.scale == 2:
            model_name = 'RealESRGAN_x2plus.pth'
            model_scale = 2
        else:
            model_name = 'realesr-general-x4v3.pth'
            model_scale = 4

        model = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,
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

        model_dir = os.path.dirname(model_path)
        os.makedirs(model_dir, exist_ok=True)

        model_name = os.path.basename(model_path)

        if model_name == 'RealESRGAN_x2plus.pth':
            url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth"
        else:
            url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth"

        log.info(f"Downloading Real-ESRGAN model from {url}...")
        urllib.request.urlretrieve(url, model_path)
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

    def _mark_as_upscaled(self, image_path: str):
        from .format.utils import create_file_hash_sha256

        img_hash = create_file_hash_sha256(image_path)
        marker = self._get_marker_path(image_path)
        with open(marker, 'w') as f:
            f.write(
                f"scale={self.scale}\nmodel={getattr(self, '_model_name', 'unknown')}\ndevice={getattr(self, '_device', 'unknown')}\nhash={img_hash}\n"
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

    def _upscale_single_image(self, input_path: str, retry: bool = False):
        if self._is_already_upscaled(input_path):
            filename = os.path.basename(input_path)
            log.info(f"Already upscaled: {filename}")
            return (input_path, True, False)

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
            self._mark_as_upscaled(input_path)

            filename = os.path.basename(input_path)
            if not retry:
                log.info(f"Upscaled: {filename}")
            else:
                log.info(f"Retry successful: {filename}")

            return (input_path, True, False)
        except Exception as e:
            is_mem_error = self._is_memory_error(e)
            error_type = "memory error" if is_mem_error else "error"
            log.error(f"Error upscaling {input_path} ({error_type}): {e}")
            return (input_path, False, is_mem_error)

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

        failed_memory = []
        failed_other = []

        try:
            with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
                futures = {
                    executor.submit(self._upscale_single_image, img): img
                    for img in valid_images
                }

                for future in as_completed(futures):
                    if self._shutdown_event.is_set():
                        log.info("Upscale cancelled by user")
                        executor.shutdown(wait=False, cancel_futures=True)
                        break

                    path, success, is_mem_error = future.result()
                    if not success:
                        if is_mem_error:
                            failed_memory.append(path)
                        else:
                            failed_other.append(path)
        except KeyboardInterrupt:
            log.info("Upscale interrupted, cancelling pending operations...")
            self._shutdown_event.set()
            raise

        if failed_memory and not self._shutdown_event.is_set():
            log.warning(
                f"Retrying {len(failed_memory)} images with concurrency=1 "
                "due to memory errors..."
            )

            if hasattr(torch, 'mps') and torch.backends.mps.is_available():
                torch.mps.empty_cache()
            elif torch.cuda.is_available():
                torch.cuda.empty_cache()

            with ThreadPoolExecutor(max_workers=1) as executor:
                futures = {
                    executor.submit(self._upscale_single_image, img, retry=True): img
                    for img in failed_memory
                }

                still_failed = []
                for future in as_completed(futures):
                    if self._shutdown_event.is_set():
                        executor.shutdown(wait=False, cancel_futures=True)
                        break

                    path, success, is_mem_error = future.result()
                    if not success and is_mem_error:
                        still_failed.append(path)

                if still_failed and not self._shutdown_event.is_set():
                    log.warning(
                        f"Moving {len(still_failed)} images to CPU "
                        "due to persistent memory errors..."
                    )

                    original_device = self.upsampler.device
                    self.upsampler.device = torch.device('cpu')
                    self.upsampler.model = self.upsampler.model.cpu()

                    for img in still_failed:
                        if self._shutdown_event.is_set():
                            break

                        path, success, _ = self._upscale_single_image(img, retry=True)
                        if not success:
                            failed_other.append(path)

                    self.upsampler.device = original_device
                    self.upsampler.model = self.upsampler.model.to(original_device)

    # No progress bar to reset

        total_failed = len(failed_other)
        total_success = len(valid_images) - total_failed

        if total_failed > 0:
            log.warning(
                f"Upscale completed: {total_success} successful, "
                f"{total_failed} failed"
            )
        else:
            log.info(f"Successfully upscaled {total_success} images with Real-ESRGAN")

        return image_paths
