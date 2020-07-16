import re
from pathlib import Path

import click

class FramesDir:
    def __init__(self, directory, dose_per_image):
        self.directory = directory
        self.dose_per_image = dose_per_image
        Path('mdoc').mkdir(exist_ok=True)
        self.write()

    @property
    def movies(self):
        return Path(self.directory).glob('*_fractions.mrc')

    @property
    def mdoc_images(self):
        return (MdocImage(movie, self.dose_per_image) for movie in self.movies)

    @property
    def unique_basenames(self):
        basenames = [mdoc_image.basename for mdoc_image in self.mdoc_images]
        unique_basenames = set(basenames)
        return unique_basenames

    @property
    def mdocs(self):

        mdocs = []

        for basename in self.unique_basenames:
            mdoc_images = [mdoc_image for mdoc_image in self.mdoc_images if mdoc_image.basename == basename]
            mdocs.append(Mdoc(mdoc_images))

        return mdocs

    def write(self):
        for mdoc in self.mdocs:
            mdoc.write()


class Mdoc:
    def __init__(self, mdoc_images):
        self.mdoc_images = mdoc_images

    @property
    def basename(self):
        return self.mdoc_images[0].basename

    @property
    def filename(self):
        return Path('mdoc', f'{self.basename}.mrc.mdoc')

    @property
    def header(self):
        header = ["PixelSpacing = 1.000",
                  "Voltage = 300",
                  f"ImageFile = {self.basename}.mrc",
                  "ImageSize = 5760 4092",
                  "DataMode = 1",
                  "\n",
                  "[T = SpoofedSerialEM: mdocspoofer                               15-July-20  16:44:02    ]",
                  "\n",
                  "[T =     Tilt axis angle = 85.9, binning = 1  spot = 8  camera = 0]",
                  "\n"
                  ]
        return header

    @property
    def n_mdoc_images(self):
        return len(self.mdoc_images)

    @property
    def image_idx(self):
        return [mdoc_image.image_idx for mdoc_image in self.mdoc_images]

    @property
    def ordered_mdoc_images(self):
        s = sorted(zip(self.image_idx, self.mdoc_images), key=lambda x: x[0])
        ordered_mdoc_images = [tup[1] for tup in s]
        return ordered_mdoc_images

    def write(self):
        self.write_header()
        self.write_body()

    def write_header(self):
        with open(self.filename, 'w') as file:
            for line in self.header:
                file.write(f'{line}\n')

    def write_body(self):
        with open(self.filename, 'a') as file:
            for image in self.ordered_mdoc_images:
                for line in image.body:
                    file.write(f'{line}\n')


class MdocImage:
    def __init__(self, image_file, dose_per_image):
        self.image_file_full = Path(image_file)
        self.dose_per_image = dose_per_image

    @property
    def image_file(self):
        return self.image_file_full.name

    @property
    def regex(self):
        return re.search(r'(.*)_([0-9]{3})\[(.*?)\]', self.image_file)

    @property
    def tilt_angle(self):
        return float(self.regex.group(3))

    @property
    def image_idx(self):
        return int(self.regex.group(2)) - 1

    @property
    def dose(self):
        return self.dose_per_image

    @property
    def basename(self):
        return self.regex.group(1)

    @property
    def body(self):
        body = [f"[ZValue = {self.image_idx}]",
                f"TiltAngle = {self.tilt_angle}",
                f"StagePosition = 302.007 -82.443",
                "StageZ = -28.1985",
                "Magnification = 64000",
                "Intensity = 0.111751",
                f"ExposureDose = {self.dose}",
                "PixelSpacing = 1.000",
                "SpotSize = 8",
                "Defocus = 1.40864",
                "ImageShift = -0.124064 -0.00516909",
                "RotationAngle = 175.95",
                "ExposureTime = 3",
                "Binning = 1",
                "CameraIndex = 0",
                "DividedBy2 = 1",
                "MagIndex = 29",
                "CountsPerElectron = 16.82",
                "MinMaxMean = -1041 4987 86.6576",
                "TargetDefocus = -2",
                fr"SubFramePath = X:\spoof\frames\{self.image_file}",
                "NumSubFrames = 15",
                "FrameDosesAndNumber = 0 15",
                "DateTime = 24-Sep-18  16:47:20",
                "NavigatorLabel = 37",
                "\n"
                ]
        return body


@click.command()
@click.option('--input', '-i', 'directory',
              prompt='Directory containing frames',
              type=click.Path(),
              required=True,
              )
@click.option('--dose_per_image', '-d', 'dose_per_image',
              prompt='Dose per image (electrons per square angstrom)',
              type=float,
              required=True)
def cli(directory, dose_per_image):
    f = FramesDir(directory, dose_per_image)
    n_mdocs = len(f.mdocs)
    click.echo(f"Done! Wrote out {n_mdocs} mdoc files for frames in '{directory}' in the 'mdoc' folder")
    return
