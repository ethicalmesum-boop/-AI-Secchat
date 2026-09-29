# ============================================
# Voice Deepfake Detector - MAX AGGRESSIVE
# Multi-signal boost for high confidence
# ============================================

import wave
import struct
import subprocess
import tempfile
import os
import numpy as np


class VoiceDeepfakeDetector:
    
    def __init__(self):
        pass
    
    def _convert_to_wav(self, input_path):
        ext = os.path.splitext(input_path)[1].lower()
        if ext == ".wav":
            try:
                with wave.open(input_path, "rb") as w:
                    if w.getsampwidth() == 2 and w.getframerate() == 16000:
                        return input_path, None
            except:
                pass
        
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        try:
            result = subprocess.run(
                ["ffmpeg", "-y", "-i", input_path,
                 "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", temp_wav],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                return None, f"ffmpeg error: {result.stderr[-200:]}"
            return temp_wav, None
        except FileNotFoundError:
            return None, "ffmpeg not found"
        except Exception as e:
            return None, f"Conversion failed: {str(e)}"
    
    def analyze(self, audio_path):
        temp_wav = None
        try:
            wav_path, error = self._convert_to_wav(audio_path)
            if error:
                return {"success": False, "error": error}
            if wav_path != audio_path:
                temp_wav = wav_path
            
            with wave.open(wav_path, 'rb') as wav:
                n_channels = wav.getnchannels()
                sample_width = wav.getsampwidth()
                framerate = wav.getframerate()
                n_frames = wav.getnframes()
                frames = wav.readframes(n_frames)
            
            duration = n_frames / framerate
            if duration < 1:
                return {"success": False, "error": "Audio too short (need 1+ sec)"}
            
            if sample_width != 2:
                return {"success": False, "error": "Only 16-bit audio supported"}
            
            samples = np.array(
                struct.unpack(f"<{n_frames * n_channels}h", frames),
                dtype=np.float32
            )
            if n_channels == 2:
                samples = samples.reshape(-1, 2).mean(axis=1)
            samples = samples / 32768.0
            
            # ============================================
            # FEATURE EXTRACTION
            # ============================================
            
            # 1. Amplitude stats
            amplitude = np.abs(samples)
            amp_mean = float(np.mean(amplitude))
            amp_std = float(np.std(amplitude))
            amp_cv = amp_std / amp_mean if amp_mean > 0 else 0
            
            # 2. ZCR
            zero_crossings = np.sum(np.abs(np.diff(np.sign(samples))) > 0)
            zcr = zero_crossings / len(samples)
            
            # 3. Silence
            silence_threshold = max(amp_mean * 0.05, 0.005)
            silent = np.sum(amplitude < silence_threshold)
            silence_ratio = float(silent / len(amplitude))
            
            # 4. RMS
            window_size = max(framerate // 20, 512)
            n_windows = len(samples) // window_size
            rms_values = []
            for i in range(n_windows):
                chunk = samples[i * window_size:(i + 1) * window_size]
                rms_values.append(np.sqrt(np.mean(chunk ** 2)))
            rms_std = float(np.std(rms_values)) if rms_values else 0
            rms_mean = float(np.mean(rms_values)) if rms_values else 0
            rms_cv = rms_std / rms_mean if rms_mean > 0 else 0
            
            # 5. FFT
            fft = np.fft.rfft(samples)
            magnitude = np.abs(fft)
            
            mag_nz = magnitude[magnitude > 1e-10]
            if len(mag_nz) > 0:
                geo = np.exp(np.mean(np.log(mag_nz)))
                arith = np.mean(mag_nz)
                spectral_flatness = float(geo / arith)
            else:
                spectral_flatness = 0
            
            # 6. HF/LF ratio
            freqs = np.fft.rfftfreq(len(samples), 1.0 / framerate)
            hf_mask = freqs > 4000
            lf_mask = (freqs > 300) & (freqs < 3000)
            hf_energy = np.sum(magnitude[hf_mask] ** 2)
            lf_energy = np.sum(magnitude[lf_mask] ** 2)
            hf_lf_ratio = hf_energy / lf_energy if lf_energy > 0 else 0
            
            # 7. Noise floor
            sorted_amp = np.sort(amplitude)
            noise_floor = float(np.mean(sorted_amp[:len(sorted_amp)//10]))
            signal_level = float(np.mean(sorted_amp[len(sorted_amp)//2:]))
            noise_ratio = noise_floor / signal_level if signal_level > 0 else 0
            
            # 8. Spectral entropy (AI = LOW entropy = simple spectrum)
            mag_norm = magnitude / (np.sum(magnitude) + 1e-10)
            spectral_entropy = -np.sum(mag_norm * np.log2(mag_norm + 1e-10))
            spectral_entropy_norm = spectral_entropy / np.log2(len(magnitude))
            
            # 9. RMS uniformity (AI = very uniform)
            if rms_values:
                rms_arr = np.array(rms_values)
                uniform_frames = np.sum(np.abs(rms_arr - rms_mean) < rms_mean * 0.2)
                uniformity = uniform_frames / len(rms_arr)
            else:
                uniformity = 0
            
            # ============================================
            # STRONG AI SIGNAL COUNTER
            # ============================================
            strong_signals = 0
            score = 0
            reasons = []
            
            # ---- SIGNAL 1: Flat spectrum (STRONG AI) ----
            if spectral_flatness > 0.01:
                score += 25
                strong_signals += 1
                reasons.append("[STRONG] Very flat spectrum (AI clean audio)")
            elif spectral_flatness > 0.005:
                score += 12
                reasons.append("Somewhat flat spectrum")
            else:
                reasons.append("Natural spectral variation")
            
            # ---- SIGNAL 2: Zero background noise (STRONG AI) ----
            if noise_ratio < 0.05:
                score += 25
                strong_signals += 1
                reasons.append("[STRONG] Zero background noise (AI studio-like)")
            elif noise_ratio < 0.1:
                score += 12
                reasons.append("Very low background noise")
            else:
                reasons.append("Natural background noise")
            
            # ---- SIGNAL 3: Missing high-frequency texture (STRONG AI) ----
            if hf_lf_ratio < 0.08:
                score += 20
                strong_signals += 1
                reasons.append("[STRONG] Missing HF texture (AI-like)")
            elif hf_lf_ratio < 0.15:
                score += 10
                reasons.append("Low HF content")
            else:
                reasons.append("Natural HF content")
            
            # ---- SIGNAL 4: Low spectral entropy (STRONG AI) ----
            if spectral_entropy_norm < 0.5:
                score += 15
                strong_signals += 1
                reasons.append("[STRONG] Low spectral complexity (AI-like)")
            elif spectral_entropy_norm < 0.7:
                score += 8
                reasons.append("Moderate spectral complexity")
            else:
                reasons.append("High spectral complexity (human-like)")
            
            # ---- SIGNAL 5: High frame uniformity (STRONG AI) ----
            if uniformity > 0.85:
                score += 20
                strong_signals += 1
                reasons.append(f"[STRONG] Highly uniform frames ({int(uniformity*100)}%)")
            elif uniformity > 0.7:
                score += 10
                reasons.append(f"Uniform frames ({int(uniformity*100)}%)")
            else:
                reasons.append("Natural frame variation")
            
            # ---- SIGNAL 6: Low amplitude variation ----
            if amp_cv < 0.5:
                score += 12
                reasons.append("Low amplitude variation")
            elif amp_cv < 0.7:
                score += 6
                reasons.append("Moderate amplitude dynamics")
            else:
                reasons.append("Natural amplitude dynamics")
            
            # ---- SIGNAL 7: Low RMS variation ----
            if rms_cv < 0.6:
                score += 12
                reasons.append("Uniform energy")
            elif rms_cv < 0.9:
                score += 6
                reasons.append("Moderate energy variation")
            else:
                reasons.append("Natural energy variation")
            
            # ---- SIGNAL 8: Missing pauses ----
            if silence_ratio < 0.08:
                score += 10
                reasons.append("Missing pauses")
            elif silence_ratio < 0.2:
                score += 5
                reasons.append("Few pauses")
            else:
                reasons.append("Natural pauses")
            
            # ---- SIGNAL 9: Short duration ----
            if duration < 5:
                score += 8
                reasons.append("Short clip (typical AI sample)")
            
            # ============================================
            # MULTI-SIGNAL BOOST (KEY!)
            # If 3+ strong AI signals → massive boost
            # ============================================
            boost = 0
            if strong_signals >= 4:
                boost = 30
                reasons.append(f"⚡ {strong_signals} STRONG AI signals detected!")
            elif strong_signals == 3:
                boost = 20
                reasons.append(f"⚡ {strong_signals} strong AI signals detected")
            elif strong_signals == 2:
                boost = 10
                reasons.append(f"{strong_signals} AI signals detected")
            
            score += boost
            confidence = min(score, 100)
            
            # ============================================
            # 3-LEVEL VERDICT
            # ============================================
            if confidence >= 70:
                is_fake = True
                verdict = "AI-GENERATED VOICE"
                emoji = "🔴"
                level = "HIGH"
            elif confidence >= 40:
                is_fake = True
                verdict = "SUSPICIOUS - LIKELY AI"
                emoji = "🟠"
                level = "MEDIUM"
            else:
                is_fake = False
                verdict = "HUMAN VOICE"
                emoji = "🟢"
                level = "LOW"
            
            return {
                "success": True,
                "is_fake": is_fake,
                "verdict": verdict,
                "emoji": emoji,
                "level": level,
                "confidence": round(confidence, 2),
                "duration": round(duration, 2),
                "strong_signals": strong_signals,
                "reasons": reasons,
                "features": {
                    "spectral_flatness": round(spectral_flatness, 5),
                    "noise_ratio": round(noise_ratio, 4),
                    "hf_lf_ratio": round(hf_lf_ratio, 4),
                    "spectral_entropy": round(spectral_entropy_norm, 3),
                    "uniformity": round(uniformity, 3),
                    "amplitude_cv": round(amp_cv, 3),
                    "rms_cv": round(rms_cv, 3),
                    "silence_ratio": round(silence_ratio, 3),
                }
            }
        except Exception as e:
            return {"success": False, "error": f"{str(e)}"}
        finally:
            if temp_wav and os.path.exists(temp_wav):
                try:
                    os.remove(temp_wav)
                except:
                    pass