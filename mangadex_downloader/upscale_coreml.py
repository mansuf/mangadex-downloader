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

import hashlib
import logging
import os
import threading
import zipfile
from pathlib import Path
import importlib.util
from typing import List

try:
    import coremltools as ct
    import numpy as np
    from PIL import Image
    COREML_AVAILABLE = True
except ImportError:
    COREML_AVAILABLE = False

log = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

MODELS = {
    2: {
        'name': 'RealESRGAN_x2plus',
        'urls': [
            'https://upscale.aidoku.app/models/RealESRGAN_x2plus.mlpackage.zip',
            'https://github.com/lucasliet/mangadex-downloader-upscaler/releases/download/models/RealESRGAN_x2plus.mlpackage.zip'
        ],
        'sha256': '66a473d1bd38f6f9df1d0ffb9851aad7c5bc1a41ae6be29c55dd48775744bfe7'
    },
    4: {
        'name': 'RealESRGAN_x4plus_anime_6B',
        'urls': [
            'https://github.com/lucasliet/mangadex-downloader-upscaler/releases/download/models/RealESRGAN_x4plus_anime_6B.mlpackage.zip'
        ],
        'sha256': '9465b28c875f12f1fff4e31f0d26a89d98df15a43ad1afdc8547eee5811c8500'
    }
}


class CoreMLUpscaler:
    """
    Real-ESRGAN upscaler using Apple Core ML with Neural Engine acceleration.

    This upscaler leverages Apple's Neural Engine on macOS for hardware-accelerated
    image upscaling. It supports 2x upscaling with RealESRGAN_x2plus and 4x upscaling
    with RealESRGAN_x4plus_anime_6B. Models are automatically downloaded on first use
    and images are processed using a tile-based approach for handling arbitrary sizes.

    Requirements:
        - macOS 12+ (Monterey or newer)
        - coremltools>=7.0
        - Apple Silicon (M1/M2/M3/M4) recommended for Neural Engine
        - Intel Macs supported (uses CPU/GPU fallback)

    Features:
        - Supports 2x and 4x upscaling with different models
        - Automatic model download with fallback URLs and SHA256 validation
        - Neural Engine acceleration (zero CPU/GPU usage during inference)
        - Tile-based processing for large images (256x256 tiles with overlap)
        - SHA256-based marker system to skip already upscaled images
        - Graceful shutdown on interruption

    Args:
        scale: Upscaling factor (supports 2x and 4x)
    """
    def __init__(self, scale: int = 2):
        if not COREML_AVAILABLE:
            raise ImportError(
                "Core ML dependencies not installed. "
                "Install with: pip install mangadex-downloader[optional]"
            )

        if scale not in MODELS:
            raise ValueError(
                f"Unsupported scale factor: {scale}. "
                f"Core ML upscaler supports: {list(MODELS.keys())}"
            )

        self.requested_scale = scale
        self._shutdown_event = threading.Event()
        self._model_name = MODELS[scale]['name']
        self.model_scale = scale

        self.models_dir = self._get_package_models_dir()
        self.model_path = self.models_dir / f"{self._model_name}.mlpackage"

        self._ensure_model()
        self._load_model()

        log.info(
            f"Real-ESRGAN Core ML initialized (scale={self.requested_scale}x, "
            f"device=Neural Engine, model={self._model_name})"
        )

    def _get_package_models_dir(self) -> Path:
        try:
            spec = importlib.util.find_spec('mangadex_downloader')
            if spec is not None and spec.origin is not None:
                package_path = Path(spec.origin).parent
                log.debug(f"Using package directory: {package_path}")
                return package_path / "models"
        except Exception as e:
            log.debug(f"Could not determine package location: {e}")

        fallback_path = Path(__file__).parent / "models"
        log.debug(f"Using fallback directory: {fallback_path}")
        return fallback_path

    def _ensure_model(self):
        if self.model_path.exists():
            return

        log.info(f"Core ML model '{self._model_name}' not found. Downloading...")

        self.models_dir.mkdir(parents=True, exist_ok=True)

        import urllib.request
        from tqdm import tqdm

        model_config = MODELS[self.requested_scale]
        zip_path = self.models_dir / f"{self._model_name}.mlpackage.zip"
        expected_hash = model_config['sha256']

        last_error = None

        for url_index, url in enumerate(model_config['urls']):
            try:
                log.info(f"Trying download URL {url_index + 1}/{len(model_config['urls'])}: {url}")

                with tqdm(unit='B', unit_scale=True, unit_divisor=1024,
                          miniters=1, desc=f"Downloading {self._model_name}") as pbar:
                    def reporthook(block_num, block_size, total_size):
                        if pbar.total is None and total_size > 0:
                            pbar.total = total_size
                        downloaded = block_num * block_size
                        if downloaded <= total_size:
                            pbar.update(block_size)

                    urllib.request.urlretrieve(url, zip_path, reporthook=reporthook)

                hasher = hashlib.sha256()
                with open(zip_path, 'rb') as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)
                downloaded_hash = hasher.hexdigest()

                if downloaded_hash.lower() != expected_hash.lower():
                    if zip_path.exists():
                        zip_path.unlink()
                    raise RuntimeError(
                        f"Model integrity check failed. "
                        f"Expected SHA256: {expected_hash}, got: {downloaded_hash}"
                    )

                log.debug("Model integrity check passed.")

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    members = zip_ref.namelist()
                    log.debug(f"ZIP contains {len(members)} files")

                    for member in members:
                        if '..' in member or member.startswith('/'):
                            raise ValueError(f"Unsafe zip member detected: {member}")

                    self.model_path.mkdir(parents=True, exist_ok=True)
                    zip_ref.extractall(self.model_path)

                if not self.model_path.exists():
                    contents = list(self.models_dir.iterdir())
                    raise RuntimeError(
                        f"Model extraction failed. Expected path does not exist.\n"
                        f"Expected: {self.model_path}\n"
                        f"Models directory contents: {contents}"
                    )

                log.info(f"Core ML model downloaded to {self.model_path}")

                if zip_path.exists():
                    zip_path.unlink()

                return

            except Exception as e:
                last_error = e
                log.warning(f"Failed to download from {url}: {e}")
                if zip_path.exists():
                    zip_path.unlink()
                continue

        raise RuntimeError(
            f"Failed to download model '{self._model_name}' from all available URLs. "
            f"Last error: {last_error}"
        )

    def _load_model(self):
        try:
            self.model = ct.models.MLModel(
                str(self.model_path),
                compute_units=ct.ComputeUnit.ALL
            )
            log.debug(f"Core ML model loaded with Neural Engine support")
        except Exception as e:
            log.error(f"Failed to load Core ML model: {e}")
            raise

    def _is_image(self, path: Path) -> bool:
        return path.suffix.lower() in IMAGE_EXTENSIONS

    def _get_marker_path(self, image_path: str) -> str:
        return f"{image_path}.upscaled"

    def shutdown(self):
        self._shutdown_event.set()

    def _mark_as_upscaled(self, image_path: str, source_hash: str):
        from .format.utils import create_file_hash_sha256

        img_hash = create_file_hash_sha256(image_path)
        marker = self._get_marker_path(image_path)
        with open(marker, 'w') as f:
            f.write(
                f"scale={self.requested_scale}\nmodel={self._model_name}\n"
                f"device=coreml-ane\nhash={img_hash}\nsource_hash={source_hash}\n"
            )

    def _is_already_upscaled(self, image_path: str) -> bool:
        from .format.utils import create_file_hash_sha256

        marker = self._get_marker_path(image_path)
        if not os.path.exists(marker):
            return False

        try:
            with open(marker, 'r') as f:
                content = f.read()

            if f"scale={self.requested_scale}" not in content:
                return False

            stored_hash = None
            for line in content.splitlines():
                if line.startswith("hash="):
                    stored_hash = line.split("=", 1)[1]
                    break

            if not stored_hash:
                return False

            current_hash = create_file_hash_sha256(image_path)
            if current_hash != stored_hash:
                log.debug(
                    f"Hash mismatch for {image_path}, removing marker "
                    f"(stored={stored_hash[:8]}..., current={current_hash[:8]}...)"
                )
                os.remove(marker)
                return False

            return True
        except Exception:
            return False

    def _tile_upscale(self, img_array: 'np.ndarray') -> 'np.ndarray':
        """
        Upscale large images using tile-based processing with overlap and feathering.

        The Core ML model accepts fixed 256x256 input, so large images are split into
        overlapping tiles, processed individually, and blended seamlessly using weighted
        averaging with edge feathering to prevent visible seams.

        Args:
            img_array: Input image in CHW format (Channels, Height, Width), float32 [0, 1]

        Returns:
            Upscaled image in CHW format, float32 [0, 1], dimensions scaled by self.requested_scale
        """
        C, H, W = img_array.shape
        tile_size = 256
        overlap = 32
        scale = self.requested_scale

        output_h = H * scale
        output_w = W * scale
        output = np.zeros((C, output_h, output_w), dtype=np.float32)
        weight_map = np.zeros((output_h, output_w), dtype=np.float32)

        y_positions = list(range(0, H, tile_size - overlap))
        x_positions = list(range(0, W, tile_size - overlap))

        if y_positions[-1] + tile_size < H:
            y_positions.append(H - tile_size)
        if x_positions[-1] + tile_size < W:
            x_positions.append(W - tile_size)

        for y in y_positions:
            for x in x_positions:
                y_end = min(y + tile_size, H)
                x_end = min(x + tile_size, W)

                tile = np.zeros((C, tile_size, tile_size), dtype=np.float32)
                tile_h = y_end - y
                tile_w = x_end - x
                tile[:, :tile_h, :tile_w] = img_array[:, y:y_end, x:x_end]

                tile_batch = np.expand_dims(tile, axis=0)
                predictions = self.model.predict({'input': tile_batch})
                upscaled_tile = next(iter(predictions.values()))[0]

                out_y = y * scale
                out_x = x * scale
                out_h = tile_h * scale
                out_w = tile_w * scale

                weight = np.ones((out_h, out_w), dtype=np.float32)

                if overlap > 0:
                    feather = min(16, overlap // 2)
                    for i in range(feather):
                        alpha = (i + 1) / feather
                        if y > 0 and i < out_h:
                            weight[i, :] *= alpha
                        if y_end < H and (out_h - i - 1) >= 0:
                            weight[out_h - i - 1, :] *= alpha
                        if x > 0 and i < out_w:
                            weight[:, i] *= alpha
                        if x_end < W and (out_w - i - 1) >= 0:
                            weight[:, out_w - i - 1] *= alpha

                output[:, out_y:out_y+out_h, out_x:out_x+out_w] += upscaled_tile[:, :out_h, :out_w] * weight
                weight_map[out_y:out_y+out_h, out_x:out_x+out_w] += weight

        output = output / np.maximum(weight_map, 1e-8)

        return output

    def _upscale_single_image(self, input_path: str) -> tuple[str, bool]:
        if self._is_already_upscaled(input_path):
            filename = os.path.basename(input_path)
            log.info(f"Already upscaled: {filename}")
            return (input_path, True)

        from .format.utils import create_file_hash_sha256
        source_hash = create_file_hash_sha256(input_path)

        try:
            img = Image.open(input_path)
            original_mode = img.mode
            has_alpha = original_mode in ('RGBA', 'LA') or (original_mode == 'P' and 'transparency' in img.info)
            alpha = None

            if has_alpha:
                log.debug(f"Image has alpha channel, separating for upscale.")
                alpha = img.getchannel('A')
                img = img.convert('RGB')

            elif original_mode not in ('RGB', 'L'):
                img = img.convert('RGB')

            img_array = np.array(img).astype(np.float32) / 255.0
            if img_array.ndim == 2: # Grayscale
                img_array = np.stack([img_array] * 3, axis=-1)
            
            img_array = np.transpose(img_array, (2, 0, 1))

            _, H, W = img_array.shape

            if H > 256 or W > 256:
                output_array = self._tile_upscale(img_array)
            else:
                img_batch = np.expand_dims(img_array, axis=0)
                predictions = self.model.predict({'input': img_batch})
                output_array = next(iter(predictions.values()))[0]

            output_array = np.transpose(output_array, (1, 2, 0))
            output_array = (output_array * 255.0).clip(0, 255).astype(np.uint8)

            output_img = Image.fromarray(output_array, 'RGB')

            if has_alpha and alpha:
                log.debug("Re-applying alpha channel.")
                new_size = output_img.size
                alpha_resized = alpha.resize(new_size, Image.Resampling.BICUBIC)
                output_img.putalpha(alpha_resized)

            ext = Path(input_path).suffix.lower()
            if ext in ('.jpg', '.jpeg'):
                output_img.save(input_path, quality=95, optimize=True)
            elif ext == '.png':
                output_img.save(input_path, optimize=True)
            else:
                output_img.save(input_path)

            self._mark_as_upscaled(input_path, source_hash)
            filename = os.path.basename(input_path)
            log.info(f"Upscaled: {filename}")

            return (input_path, True)

        except Exception as e:
            log.error(f"Core ML upscale failed for {input_path}: {e}")
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

        log.info(
            f"Upscaling {len(valid_images)} images with Real-ESRGAN Core ML "
            f"(scale={self.requested_scale}x)..."
        )

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
            log.info(
                f"Successfully upscaled {total_success} images with Real-ESRGAN Core ML"
            )

        return image_paths
