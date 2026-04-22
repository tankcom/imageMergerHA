"""Custom component: crop_merge
Service: crop_merge.crop_and_merge
Service data (optional):
  source1: '1.jpg'         # relative to config/www or absolute path
  source2: '2.jpg'
  crop1: '600x400+0+0'     # format WxH+X+Y
  crop2: '600x400+0+0'
  output: '3.jpg'          # saved to config/www/output
  mode: 'horizontal'       # or 'vertical'
  quality: 85
"""
import logging
import os
import re

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN
SERVICE_CROP_AND_MERGE = "crop_and_merge"

def _parse_crop(crop_str):
    if not crop_str:
        return None
    m = re.match(r"(?P<w>\d+)x(?P<h>\d+)\+(?P<x>-?\d+)\+(?P<y>-?\d+)$", crop_str)
    if not m:
        raise ValueError("Invalid crop format. Use WxH+X+Y")
    x = int(m.group("x")); y = int(m.group("y"))
    w = int(m.group("w")); h = int(m.group("h"))
    return (x, y, x + w, y + h)

def _resolve_path(hass, p):
    if os.path.isabs(p):
        return p
    p = p.lstrip("/")
    return os.path.join(hass.config.path(), "www", p)

def _process_images(hass, data):
    from PIL import Image
    try:
        src1 = _resolve_path(hass, data.get("source1", "1.jpg"))
        src2 = _resolve_path(hass, data.get("source2", "2.jpg"))
        out = _resolve_path(hass, data.get("output", "3.jpg"))
        mode = data.get("mode", "horizontal")
        quality = int(data.get("quality", 85))

        if not os.path.isfile(src1):
            _LOGGER.error("Source1 not found: %s", src1); return
        if not os.path.isfile(src2):
            _LOGGER.error("Source2 not found: %s", src2); return

        img1 = Image.open(src1).convert("RGB")
        img2 = Image.open(src2).convert("RGB")

        if data.get("crop1"):
            img1 = img1.crop(_parse_crop(data["crop1"]))
        if data.get("crop2"):
            img2 = img2.crop(_parse_crop(data["crop2"]))

        if mode == "vertical":
            new_w = max(img1.width, img2.width)
            new_h = img1.height + img2.height
            canvas = Image.new("RGB", (new_w, new_h), (255,255,255))
            canvas.paste(img1, (0,0))
            canvas.paste(img2, (0, img1.height))
        else:
            new_w = img1.width + img2.width
            new_h = max(img1.height, img2.height)
            canvas = Image.new("RGB", (new_w, new_h), (255,255,255))
            canvas.paste(img1, (0,0))
            canvas.paste(img2, (img1.width, 0))

        os.makedirs(os.path.dirname(out), exist_ok=True)
        canvas.save(out, format="JPEG", quality=quality)
        _LOGGER.info("Saved merged image to %s", out)
    except Exception:
        _LOGGER.exception("crop_merge: Fehler beim Verarbeiten der Bilder")


def _handle_service(call: ServiceCall, hass: HomeAssistant) -> None:
    hass.async_add_executor_job(_process_images, hass, call.data)


def _register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_CROP_AND_MERGE):
        return
    hass.services.async_register(
        DOMAIN,
        SERVICE_CROP_AND_MERGE,
        lambda call: _handle_service(call, hass),
    )


async def async_setup(hass: HomeAssistant, config):
    _register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Crop Merge from a config entry (UI)."""
    _register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Service is global; keep it available while Home Assistant is running.
    return True
