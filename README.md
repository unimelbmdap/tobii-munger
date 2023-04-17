# tobii-munger

<!-- [![PyPI - Version](https://img.shields.io/pypi/v/tobii-munger.svg)](https://pypi.org/project/tobii-munger) -->
<!-- [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tobii-munger.svg)](https://pypi.org/project/tobii-munger) -->

-----

**Table of Contents**

- [Dependencies](#dependencies)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Dependencies

Tobii-munger has a small number of non-python dependencies, used to convert the raw Tobii data into a more usable format. These are:

- [ffmpeg](https://ffmpeg.org/)
- [jq](https://stedolan.github.io/jq/)

Please ensure these are installed before trying `tobii-munger`.

## Installation

As a user:

```console
pip install git+https://github.com/unimelbmdap/tobii-munger.git
```

As a developer, first ensure you have [Hatch](https://github.com/pypa/hatch) installed, then run:

```console
git clone git@github.com/unimelbmdap/tobii-munger.git
cd tobii-munger
hatch shell
```

This will drop you into a virtual environment with all the dependencies installed.

Lints can be run with:

```console
hatch run lint:all
```

## Usage

To convert a Tobii recording, use the `tobii_munger.convert` cli. Run the following for details:

```console
python -m tobii_munger.convert --help
```

Once you have a unified file, you can read it into a [Polars](https://pola-rs.github.io/polars-book/) DataFrame using the `tobii_munger.read_unified` function. For example:

```python
import tobii_munger.io
data = tobii_munger.read_unified("unified_data.parquet", "gaze2d"); print(data.head())
```

## License

`tobii-munger` is distributed under the terms of the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
