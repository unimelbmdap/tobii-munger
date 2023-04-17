import gzip
from pathlib import Path
from subprocess import PIPE, Popen
from tempfile import TemporaryDirectory

import numpy as np
import polars as pl
import typer


def main(data_dir: Path, out_path: Path):
    if out_path.suffix != ".parquet":
        _err = "Output path must have a .parquet suffix"
        raise typer.BadParameter(_err)

    typer.echo(f"Processing {data_dir.name}")

    out_path.parent.mkdir(exist_ok=True, parents=True)

    with TemporaryDirectory() as _tmpdir:
        tmpdir = Path(_tmpdir)

        typer.secho("Processing gaze data", fg=typer.colors.YELLOW)
        with gzip.open(data_dir / "gazedata.gz", "rb") as fin:
            with (tmpdir / "gazedata").open("wb") as fout:
                fout.write(fin.read())

        with (tmpdir / "gazedata.json").open("wb") as fout:
            _jq1 = Popen(
                [
                    "jq",
                    "-c",
                    '(.vals = .data.gaze2d | .type = "gaze2d"),'
                    '(.vals = .data.gaze3d | .type = "gaze3d"),'
                    '(.vals = .data.eyeleft.gazeorigin | .type = "eyeleft|gazeorigin"),'
                    '(.vals = .data.eyeleft.gazedirection | .type = "eyeleft|gazedirection"),'
                    '(.vals = [.data.eyeleft.pupildiameter] | .type = "eyeleft|pupildiameter"),'
                    '(.vals = .data.eyeright.gazeorigin | .type = "eyeright|gazeorigin"),'
                    '(.vals = .data.eyeright.gazedirection | .type = "eyeright|gazedirection"),'
                    '(.vals = [.data.eyeright.pupildiameter] | .type = "eyeright|pupildiameter")|'
                    "del(.data) | select (.vals != null)",
                    tmpdir / "gazedata",
                ],
                stdout=PIPE,
            )
            if not _jq1.stdout:
                _err = "Failed to open stdout"
                raise RuntimeError(_err)
            _jq2 = Popen(["jq", "-s"], stdin=_jq1.stdout, stdout=fout)
            _jq1.stdout.close()
            _jq2.communicate()

        typer.secho("Processing IMU data", fg=typer.colors.YELLOW)
        with gzip.open(data_dir / "imudata.gz", "rb") as fin:
            with (tmpdir / "imudata").open("wb") as fout:
                fout.write(fin.read())

        with (tmpdir / "imudata.json").open("wb") as fout:
            _jq1 = Popen(
                [
                    "jq",
                    "-c",
                    '(.vals = .data.accelerometer | .type = "accelerometer"), '
                    '(.vals = .data.gyroscope | .type = "gyroscope"), '
                    '(.vals = .data.magnetometer | .type = "magnetometer") | '
                    "del(.data) | select(.vals != null)",
                    tmpdir / "imudata",
                ],
                stdout=PIPE,
            )
            if not _jq1.stdout:
                _err = "Failed to open stdout"
                raise RuntimeError(_err)
            _jq2 = Popen(["jq", "-s"], stdin=_jq1.stdout, stdout=fout)
            _jq1.stdout.close()
            _jq2.communicate()

        result = pl.concat([pl.read_json(tmpdir / "gazedata.json"), pl.read_json(tmpdir / "imudata.json")]).sort(
            "timestamp"
        )

        typer.secho("Processing frame data", fg=typer.colors.YELLOW)

        timestamps_path = tmpdir / "timestamps.txt"
        with timestamps_path.open("w") as fout:
            _ffmpeg = Popen(
                [
                    "ffprobe",
                    "-show_frames",
                    "-show_entries",
                    "frame=best_effort_timestamp_time",
                    "-select_streams",
                    "v:0",
                    "-of",
                    "csv=print_section=0",
                    str(data_dir / "scenevideo.mp4"),
                ],
                stdout=fout,
            )
            _ffmpeg.communicate()
        frame_timestamps = np.loadtxt(timestamps_path)

        nearest_frame = np.argmin(np.abs(result["timestamp"].to_numpy()[:, np.newaxis] - frame_timestamps), axis=1) + 1

        typer.secho(f"Writing result to {out_path}", fg=typer.colors.GREEN)
        result = result.with_columns([pl.lit(nearest_frame).alias("frame")])
        result.write_parquet(out_path)


if __name__ == "__main__":
    typer.run(main)
