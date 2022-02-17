import argparse
from pathlib import Path
import sys

import numpy as np
import soundfile as sf
from scipy import signal
import matplotlib.pyplot as plt


def parse_ping(file: Path, offset: float = 0., duration: float = -1., visualize: bool = False,
               background_threshold: float = None, partition_threshold: float = None):
    print("Loading file...", file=sys.stderr)
    with sf.SoundFile(file, "r", ) as f:
        samplerate = f.samplerate

        # samplerate frames per second
        if offset > 0:
            f.seek(int(offset * samplerate))

        if duration >= 0:
            data = f.read(int(duration * samplerate))
        else:
            data = f.read()
        duration = data.size / samplerate

    print("Filtering...", file=sys.stderr)
    filtered_data = butter_filter(data, 1500, samplerate, btype="highpass")
    print("Normalizing...", file=sys.stderr)
    # normalize to -1 to 1, to more easily extract peaks
    scale_factor = 1. / max(abs(filtered_data.min()), filtered_data.max())
    normalized = filtered_data * scale_factor

    if background_threshold is None:
        background_threshold = butter_filter(normalized, 1500, samplerate, btype="lowpass").max()

    print("Detecting peaks...", file=sys.stderr)
    peaks, _ = signal.find_peaks(normalized,
                                 distance=samplerate * 2,
                                 threshold=(background_threshold, None))

    peak_values = normalized[peaks]

    if partition_threshold is None:
        partition_threshold = (peak_values.max() - peak_values.min()) / 2 + peak_values.min()

    partitioned = peak_values > partition_threshold
    # do a sanity check on the signals
    pings = peak_values[partitioned]
    ping_variance = pings.max() - pings.min()

    chimes = peak_values[~partitioned]
    chime_variance = chimes.max() - chimes.min()

    ping_chime_dist = np.average(pings) - np.average(chimes)

    if ping_variance > .15 or chime_variance > .15 or ping_chime_dist < .15:
        print("WARNING! The extraction may be unreliable. "
              "Could be a bad recording. Please double check with a visualization.",
              file=sys.stderr)
    print("Analysis metrics:",
          f"  Background threshold: {background_threshold:.3f}",
          f"   Partition threshold: {partition_threshold:.3f}",
          f"         Ping variance: {ping_variance:.3f}",
          f"        Chime variance: {chime_variance:.3f}",
          f"   Ping-chime distance: {ping_chime_dist:.3f}",
          sep="\n", file=sys.stderr)
    bitstream = partitioned * 1

    print("\nParsed output:", file=sys.stderr)
    print("".join(str(x) for x in bitstream), "\n")

    if visualize:
        print("Loading visualization. NOTE! This is CPU and memory intensive for big files.", file=sys.stderr)
        fig, (ax1, ax2) = plt.subplots(2, 1)
        second_indices = np.linspace(offset, offset + duration, data.size)
        ax1.plot(second_indices, data)
        ax1.set_ylabel("Raw Signal")

        ax2.plot(second_indices, normalized)
        ax2.plot(second_indices[peaks], peak_values, "x")
        ax2.hlines((partition_threshold, background_threshold),
                   second_indices[0], second_indices[-1], ("gray", "black"), "--")
        ax2.set_xlabel("Seconds")
        ax2.set_ylabel("Filtered Signal")

        plt.show()


def butter_filter(sig, cutoff, fs, order=5, btype="highpass"):
    sos = signal.butter(order, cutoff, fs=fs, btype=btype, output="sos")
    return signal.sosfilt(sos, sig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path, help="audio file of map ping to analyze")
    parser.add_argument("--visualize", action="store_true",
                        help="show the plot (WARNING! Slow for big files)")
    parser.add_argument("--offset", type=float, default=0.,
                        help="offset in seconds into the file to start parsing")
    parser.add_argument("--duration", type=float, default=-1.,
                        help="for how many seconds to parse")
    parser.add_argument("--background", type=float, default=None,
                        help="manually set the background threshold value above "
                             "where peaks should be found (DEFAULT: determined automatically)")
    parser.add_argument("--partition", type=float, default=None,
                        help="manually set the partition value threshold to "
                             "separate ping and chime peaks (DEFAULT: determined automatically)")

    args = parser.parse_args()
    if not args.file.exists():
        parser.error(f"file: {args.file} doesn't exist")

    parse_ping(args.file, args.offset, args.duration, args.visualize,
               background_threshold=args.background,
               partition_threshold=args.partition)


if __name__ == "__main__":
    main()
