from guis.straw.leak.least_square_linear import get_fit
from guis.straw.leak.straw_leak_utilities import *
from guis.common.getresources import GetProjectPaths
import csv
from pathlib import Path


def refit(raw_data_filename, n_skips_start, n_skips_end):
    directory = GetProjectPaths()["network_leaktest_raw_data"]
    leak_rate = 0
    leak_rate_err = 0

    slope = []
    slope_err = []
    intercept = []
    intercept_err = []

    # Get data
    timestamp, ppm, ppm_err = get_data_from_file(directory / raw_data_filename)

    # Skip points at beginning and end
    def truncate(container, nstart, nend):
        return container[max(nstart - 1, 0) : len(container) - nend]

    timestamp = truncate(timestamp, n_skips_start, n_skips_end)
    ppm = truncate(ppm, n_skips_start, n_skips_end)
    ppm_err = truncate(ppm_err, n_skips_start, n_skips_end)

    # Calculate slopes, leak rates
    try:
        chamber = int(raw_data_filename[15:17])
    except:
        chamber = int(raw_data_filename[15:16])
    slope, slope_err, intercept, intrcept_err = get_fit(timestamp, ppm, ppm_err)

    leak_rate = calculate_leak_rate(slope, get_chamber_volume(chamber) - STRAW_VOLUME)

    leak_rate_err = calculate_leak_rate_err(
        leak_rate,
        slope,
        slope_err,
        get_chamber_volume(chamber),
        get_chamber_volume_err(chamber),
    )

    # pass, fail, or unknown
    leak_status = evaluate_leak_rate(len(ppm), leak_rate, leak_rate_err, timestamp[-1])

    print("\nStatus leak rate after refit:", leak_status)

    title = str(Path(raw_data_filename).with_suffix(""))
    title = title.split("_")[:-1]
    title = "_".join(title) + "_refit"
    outfile = directory / title
    outfile = outfile.with_suffix(".pdf")

    plot(
        title,
        timestamp,
        ppm,
        slope,
        slope_err,
        intercept,
        leak_rate,
        leak_rate_err,
        leak_status,
        outfile,
    )

    return leak_rate, leak_rate_err


def run():
    print(
        """
    \n
     _                _      _____       __ _ _   
    | |              | |    |  __ \     / _(_) |  
    | |     ___  __ _| | __ | |__) |___| |_ _| |_ 
    | |    / _ \/ _` | |/ / |  _  // _ \  _| | __|
    | |___|  __/ (_| |   <  | | \ \  __/ | | | |_ 
    |______\___|\__,_|_|\_\ |_|  \_\___|_| |_|\__|
    \n
    Re-measure the leak rate given a raw data file.
    Exclude points from the fit at the beginning or end of the data.
    """
    )
    raw_data_filename = input("\nEnter file name: ").strip()
    n_points_to_skip_start = int(
        input("Enter number of data points to skip from start: ").strip() or 0
    )
    n_points_to_skip_end = int(
        input("Enter number of data points to skip at end: ").strip() or 0
    )
    leak_rate, leak_rate_err = refit(
        raw_data_filename, n_points_to_skip_start, n_points_to_skip_end
    )
    print("\nLeak Rate and Error: ")
    print(round(leak_rate, 7), round(leak_rate_err, 8))
    input("\nPress enter to continue.")


if __name__ == "__main__":
    run()
