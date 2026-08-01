# Fixed Beamforming Module

[English](README.md) | [中文](README.zh-CN.md)

This directory ports the reference MATLAB fixed-beamforming algorithm to Python, while keeping the offline algorithm separate from real-time audio transport.

## Confirmed technical facts

- The reference input `mixture.wav` is 16 kHz, PCM16, and 4-channel.
- The analysis window is 32 ms (512 samples), with a 16 ms (256 samples) hop.
- Each input described as "four channels of 16 ms audio" means `256 samples x 4 channels`, not 64 channels.
- The robot USB device records 8 channels. The first 4 contain valid microphone signals, with a default mapping of `(0, 1, 2, 3)`.
- Before each deployment, inspect the levels of an 8-channel recording to confirm that the first 4 channels contain signals and the last 4 contain no usable speech. This guards against device or driver changes.
- The existing `stream_usb_mic.py` averages all channels first, so its current UDP output cannot be used for beamforming.

## Directory responsibilities

- `fixed_mini_beamformer.py`: core offline and stateful streaming algorithm.
- `filter_io.py`: loads the runtime `.npz` filter without requiring SciPy.
- `stream_adapter.py`: selects 4 channels from PCM16 audio with 8 input channels, performs beamforming in 16 ms hops, and repackages the result as 20 ms mono UDP payloads using the existing protocol.
- `channel_diagnostics.py`: analyzes channel levels, silence, clipping, duplication, and correlation.

## Command setup

Run the following commands from any directory within the repository. Execute subsequent examples in the same shell. To use a dedicated Python environment, set `VOICE_PYTHON` before running them:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
VOICE_PYTHON="${VOICE_PYTHON:-python3}"
```

## Offline verification

The assets under `research/beamforming/teacher_reference_20260630/` are included reference material used to verify that the Python implementation matches the fixed beamforming reference output.

```bash
REF="$REPO_ROOT/research/beamforming/teacher_reference_20260630"

"$VOICE_PYTHON" "$REPO_ROOT/tools/beamforming/verify_teacher_reference.py" "$REF"
"$VOICE_PYTHON" "$REPO_ROOT/tools/beamforming/apply_fixed_beamformer_wav.py" \
  "$REF/mixture.wav" \
  "$REF/DCF_Targ7_runtime.npz" \
  "$REF/python_out0.wav"
```

Current acceptance result: maximum error of 1 LSB, RMSE of approximately 0.00259 LSB, with only 6 samples differing from the reference output.

## Next on-device capture

First use `arecord -l` to identify the current ALSA number for the Bothlent UAC Dongle. Then, in the repository copy on the Jetson, set the variables described in [Command setup](#command-setup) and run the diagnostic script. Do not permanently hard-code the example device `hw:2,0`:

```bash
"$VOICE_PYTHON" "$REPO_ROOT/tools/beamforming/capture_multichannel_alsa.py" \
  /tmp/bothlent_raw8.wav \
  --device hw:2,0 \
  --channels 8 \
  --sample-rate 16000 \
  --duration 10
```

After transferring the WAV file back to the development computer, run:

```bash
"$VOICE_PYTHON" "$REPO_ROOT/tools/beamforming/analyze_multichannel_wav.py" /path/to/bothlent_raw8.wav
```

Speak close to, or lightly tap, each of the four physical microphones in turn. Confirm that all of the first 4 channels contain valid signals and record their physical order. The current default is `channel_indices=(0,1,2,3)`. If measurements show a different order, override it explicitly in machine-local configuration instead of modifying the algorithm core.

## Safe integration principles

1. Keep the current `mean4` mode as a rollback path.
2. `beamformer` mode must explicitly load the filter and four-channel mapping; missing configuration must produce an immediate error.
3. Process audio on the Jetson before UDP transmission. The WSL side continues to receive 16 kHz, PCM16, mono, 20 ms, 640-byte payloads, so downstream KWS/VAD/ASR components require no changes.
4. Do not initialize Unitree `AudioClient` directly in WSL. TTS, lighting, and actions continue to use the Jetson relay.
