import os
import pandas as pd
from typing import Dict, Any

class MountainWeatherPredictor:
    """
    Offline Mountain Squall & Microclimate Predictor powered by TabPFN.
    Zero-shot tabular in-context learning with no custom training required.
    """
    def __init__(self, data_path: str = "data/mountain_weather_history.csv"):
        self.data_path = data_path
        self.feature_cols = [
            'pressure_drop_hpa_hr', 
            'altitude_m', 
            'temp_c', 
            'humidity_pct', 
            'wind_speed_kmh', 
            'cloud_type_code'
        ]
        self.target_col = 'squall_occurred'
        self.model = None
        self._init_model()

    def _init_model(self):
        # Load local reference training set
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Weather history file not found: {self.data_path}")
            
        df = pd.read_csv(self.data_path)
        X_train = df[self.feature_cols]
        y_train = df[self.target_col]

        try:
            from tabpfn import TabPFNClassifier
            print("⚡ Initializing TabPFN foundation model...")
            self.model = TabPFNClassifier(device='cpu')
            self.model.fit(X_train, y_train)
            print("✅ TabPFN ready for zero-shot in-context inference!")
        except Exception as e:
            print(f"⚠️ Warning loading TabPFN: {e}. Fallback mode active.")
            self.model = None

    def predict(self, 
                pressure_drop_hpa_hr: float,
                altitude_m: float,
                temp_c: float,
                humidity_pct: float,
                wind_speed_kmh: float,
                cloud_type_code: int) -> Dict[str, Any]:
        """
        Runs zero-shot tabular inference on current trail telemetry.
        """
        input_data = [[
            pressure_drop_hpa_hr,
            altitude_m,
            temp_c,
            humidity_pct,
            wind_speed_kmh,
            cloud_type_code
        ]]

        if self.model is not None:
            try:
                # TabPFN probability estimate
                probs = self.model.predict_proba(input_data)[0]
                # Probability of squall class (1)
                risk_score = float(probs[1]) if len(probs) > 1 else float(probs[0])
            except Exception as ex:
                print(f"TabPFN inference fallback: {ex}")
                risk_score = self._heuristic_fallback(pressure_drop_hpa_hr, humidity_pct, wind_speed_kmh)
        else:
            risk_score = self._heuristic_fallback(pressure_drop_hpa_hr, humidity_pct, wind_speed_kmh)

        risk_percent = int(round(risk_score * 100))

        # Determine severity & trail action
        if risk_percent >= 75:
            severity = "CRITICAL SQUALL WARNING"
            color = "#ef4444"
            action = "Severe mountain squall imminent within 45-90 minutes. Do NOT attempt ridge summits. Descend below tree line immediately."
            estimated_window = "30 - 60 mins"
        elif risk_percent >= 45:
            severity = "MICROCLIMATE STORM WATCH"
            color = "#f59e0b"
            action = "Rapid pressure decrease detected. Keep descent path visible and secure rain gear. Avoid exposed ridgelines."
            estimated_window = "2 - 3 hours"
        else:
            severity = "STABLE TRAIL CONDITIONS"
            color = "#10b981"
            action = "Atmospheric pressure and humidity are stable. Favorable hiking conditions across current elevation."
            estimated_window = "Stable"

        cloud_names = {
            0: "Clear / Cirrus (High)",
            1: "Cumulus (Scattered / Fair)",
            2: "Altocumulus / Lenticular (Wave Clouds)",
            3: "Towering Cumulus (Vertical Congestus)",
            4: "Cumulonimbus / Anvil (Severe Squall)"
        }

        return {
            "risk_percent": risk_percent,
            "severity": severity,
            "color": color,
            "action": action,
            "estimated_window": estimated_window,
            "cloud_name": cloud_names.get(cloud_type_code, "Unclassified"),
            "telemetry": {
                "pressure_drop": pressure_drop_hpa_hr,
                "altitude": altitude_m,
                "temp": temp_c,
                "humidity": humidity_pct,
                "wind": wind_speed_kmh
            }
        }

    def _heuristic_fallback(self, pressure_drop: float, humidity: float, wind: float) -> float:
        # Standard meteorology rule: pressure drop > 1.5 hPa/hr + high humidity + high wind
        score = 0.05
        if pressure_drop >= 2.0:
            score += 0.50
        elif pressure_drop >= 1.0:
            score += 0.25
        if humidity >= 80:
            score += 0.25
        elif humidity >= 60:
            score += 0.10
        if wind >= 40:
            score += 0.20
        return min(max(score, 0.05), 0.98)
