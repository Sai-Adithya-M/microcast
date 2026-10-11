import io
from PIL import Image, ImageStat, ImageFilter
from typing import Dict, Any

class SkyVisionAnalyzer:
    """
    Offline open-source sky & cloud morphology analyzer.
    Analyzes sky hue, cloud optical density, vertical contrast gradient,
    and convective edge texture to classify horizon clouds.
    """
    def __init__(self):
        self.classes = {
            0: {"name": "Cirrus (High & Wispy)", "risk_factor": 0.05, "desc": "High altitude ice crystals. Stable atmosphere."},
            1: {"name": "Cumulus (Fair Weather)", "risk_factor": 0.15, "desc": "Scattered low-altitude convection. Mild thermal uplift."},
            2: {"name": "Altocumulus / Lenticular", "risk_factor": 0.55, "desc": "Strong ridge wave activity. High-altitude wind shear present."},
            3: {"name": "Towering Cumulus (Congestus)", "risk_factor": 0.75, "desc": "Severe vertical updrafts forming. Storm building rapidly."},
            4: {"name": "Cumulonimbus / Anvil Supercell", "risk_factor": 0.95, "desc": "Full storm development with anvil cap. Squall imminent."}
        }

    def analyze_image_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Takes raw image bytes, runs computer vision analysis, and returns
        the detected cloud morphology code and details.
        """
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_small = img.resize((256, 256))

        # 1. Measure color channels & sky saturation
        stat = ImageStat.Stat(img_small)
        mean_r, mean_g, mean_b = stat.mean[:3]
        total_lum = (mean_r + mean_g + mean_b) / 3.0

        # Blue sky fraction (pixels where blue dominates red and green significantly)
        pixels = img_small.getdata()
        blue_pixels = sum(1 for p in pixels if (p[2] > p[0] + 15 and p[2] > p[1] + 10))
        blue_ratio = blue_pixels / len(pixels)

        # 2. Vertical gradient (split into top half and bottom half)
        # Cumulonimbus clouds feature dark bases and bright anvil crowns
        top_half = img_small.crop((0, 0, 256, 128))
        bottom_half = img_small.crop((0, 128, 256, 256))
        
        top_lum = sum(ImageStat.Stat(top_half).mean[:3]) / 3.0
        bottom_lum = sum(ImageStat.Stat(bottom_half).mean[:3]) / 3.0
        vertical_contrast = abs(top_lum - bottom_lum)

        # 3. High-frequency texture / edge density (cloud puffiness vs smooth haze)
        edges = img_small.filter(ImageFilter.FIND_EDGES)
        edge_energy = sum(ImageStat.Stat(edges).mean[:3]) / 3.0

        # Classification heuristics based on physical atmospheric optics
        if blue_ratio > 0.55 and edge_energy < 18:
            cloud_code = 0  # Clear / High Cirrus
            confidence = 88
        elif blue_ratio > 0.35 and edge_energy >= 18:
            cloud_code = 1  # Scattered Cumulus
            confidence = 84
        elif bottom_lum < 95 and (top_lum > 130 or vertical_contrast > 40):
            # Very dark base with bright top = severe storm anvil
            cloud_code = 4  # Cumulonimbus / Anvil
            confidence = 94
        elif edge_energy > 28 and blue_ratio < 0.30:
            # High convective turbulence & cloud cover
            cloud_code = 3  # Towering Congestus
            confidence = 89
        elif vertical_contrast > 25 and edge_energy < 25:
            # Smooth wave-like laminar pattern
            cloud_code = 2  # Lenticular / Wave
            confidence = 82
        else:
            # Default moderate cloudy
            cloud_code = 2 if total_lum < 130 else 1
            confidence = 78

        cls_info = self.classes[cloud_code]
        return {
            "cloud_type_code": cloud_code,
            "cloud_name": cls_info["name"],
            "description": cls_info["desc"],
            "confidence_percent": confidence,
            "metrics": {
                "blue_sky_ratio": round(blue_ratio, 2),
                "edge_density": round(edge_energy, 1),
                "vertical_contrast": round(vertical_contrast, 1),
                "mean_luminance": round(total_lum, 1)
            }
        }
