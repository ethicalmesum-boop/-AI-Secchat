# ============================================
# Voice Deepfake Detector
# Uses only numpy + Python stdlib (no librosa!)
# Supports WAV files
# ============================================

import wave
import struct
import numpy as np


class VoiceDeepfakeDetector:
    """
    Detects AI-generated voice using audio characteristics.
    Lightweight - only needs numpy + wave (stdlib).
    """
    
    def __init__(self):
        pass
    
    def analyze(self, audio_path):
        """Analyze WAV audio file and predict if AI-generated."""
        try:
            with wave.open(audio_path, 'rb') as wav:
                n_channels = wav.getnchannels()
                sample_width = wav.getsampwidth()
                framerate = wav.getframerate()
                n_frames = wav.getnframes()
                frames = wav.readframes(n_frames)
            
            duration = n_frames / framerate
            if duration < 1:
                return {
                    "success": False,
                    "error": "Audio too short (need at least 1 second)"
                }
            
            if sample_width != 2:
                return {
                    "success": False,
                    "error": "Only 16-bit WAV supported."
                }
            
            samples = np.array(
                struct.unpack(f"<{n_frames * n_channels}h", frames),
                dtype=np.float32
            )
            
            if n_channels == 2:
                samples = samples.reshape(-1, 2).mean(axis=1)
            
            samples = samples / 32768.0
            
            amplitude = np.abs(samples)
            amp_std = float(np.std(amplitude))
            amp_mean = float(np.mean(amplitude))
            
            zero_crossings = np.sum(np.abs(np.diff(np.sign(samples))) > 0)
            zcr = zero_crossings / len(samples)
            
            silence_threshold = amp_mean * 0.1
            silent_samples = np.sum(amplitude < silence_threshold)
            silence_ratio = float(silent_samples / len(amplitude))
            
            window_size = framerate // 10
            n_windows = len(samples) // window_size
            rms_values = []
            for i in range(n_windows):
                chunk = samples[i * window_size:(i + 1) * window_size]
                rms_values.append(np.sqrt(np.mean(chunk ** 2)))
            rms_std = float(np.std(rms_values)) if rms_values else 0
            
            fft = np.fft.rfft(samples)
            magnitude = np.abs(fft)
            freqs = np.fft.rfftfreq(len(samples), 1.0 / framerate)
            if np.sum(magnitude) > 0:
                spectral_centroid = float(np.sum(freqs * magnitude) / np.sum(magnitude))
            else:
                spectral_centroid = 0
            
            mag_nonzero = magnitude[magnitude > 0]
            if len(mag_nonzero) > 0:
                geo_mean = np.exp(np.mean(np.log(mag_nonzero + 1e-10)))
                arith_mean = np.mean(mag_nonzero)
                spectral_flatness = float(geo_mean / (arith_mean + 1e-10))
            else:
                spectral_flatness = 0
            
            score = 0
            reasons = []
            
            if amp_std < 0.05:
                score += 20
                reasons.append("Low amplitude variability (AI-like)")
            else:
                reasons.append("Natural amplitude dynamics")
            
            if rms_std < 0.03:
                score += 20
                reasons.append("Consistent energy (unnatural)")
            else:
                reasons.append("Natural energy variation")
            
            if silence_ratio < 0.1:
                score += 20
                reasons.append("Missing natural pauses")
            else:
                reasons.append("Natural speech pauses")
            
            if zcr < 0.05:
                score += 15
                reasons.append("Low zero-crossing (smooth AI-like)")
            else:
                reasons.append("Natural speech texture")
            
            if spectral_flatness > 0.01:
                score += 15
                reasons.append("Flat spectrum (AI-like)")
            else:
                reasons.append("Natural spectral variation")
            
            if framerate >= 44100:
                score += 10
                reasons.append("High uniform sample rate")
            
            confidence = min(score, 100)
            is_fake = confidence > 50
            
            return {
                "success": True,
                "is_fake": is_fake,
                "verdict": "AI-GENERATED VOICE" if is_fake else "HUMAN VOICE",
                "confidence": round(confidence, 2),
                "duration": round(duration, 2),
                "reasons": reasons,
                "features": {
                    "amplitude_std": round(amp_std, 4),
                    "rms_std": round(rms_std, 4),
                    "silence_ratio": round(silence_ratio, 3),
                    "zcr": round(zcr, 4),
                    "spectral_flatness": round(spectral_flatness, 5),
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"{str(e)} - Note: Only WAV files supported"
            }
