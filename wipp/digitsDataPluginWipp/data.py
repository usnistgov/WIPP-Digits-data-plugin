import math
import os
import random

import numpy as np
import tifffile.tifffile as tifffile

from digits.utils import subclass, override, constants
from digits.utils.constants import COLOR_PALETTE_ATTRIBUTE
from digits.extensions.data.interface import DataIngestionInterface
from .forms import DatasetForm

DATASET_TEMPLATE = "templates/dataset_template.html"

# WIPP API URL from evironment variable
WIPP_API_URL = os.environ.get('WIPP_API_URL') 

def load_image(full_path):
    img2D = tifffile.imread(full_path)
    img3D = img2D[np.newaxis, :, :]
    return img3D

@subclass
class DataIngestion(DataIngestionInterface):
    """
    A data ingestion extension for an image segmentation dataset
    """

    def __init__(self, **kwargs):
        """
        the parent __init__ method automatically populates this
        instance with attributes from the form
        """
        super(DataIngestion, self).__init__(**kwargs)

        self.random_indices = None

        if 'seed' not in self.userdata:
            # choose random seed and add to userdata so it gets persisted
            self.userdata['seed'] = random.randint(0, 1000)

        # if 'colormap_method' not in self.userdata:
        #     self.userdata['colormap_method'] = 'label'

        random.seed(self.userdata['seed'])

        # label palette (0->black (background), 1->white (foreground), others->black)
        palette = [0, 0, 0, 255, 255, 255] + [0] * (254 * 3)
        self.userdata[COLOR_PALETTE_ATTRIBUTE] = palette

    @override
    def encode_entry(self, entry):
        """
        Return numpy.ndarray
        """
        feature_image_file = entry[0]
        label_image_file = entry[1]

        # feature image
        feature_image = load_image(feature_image_file)

        # label image
        label_image = load_image(label_image_file)
        # if label_image.getpalette() != self.userdata[COLOR_PALETTE_ATTRIBUTE]:
        #     raise ValueError("All label images must use the same palette")
        # label_image = self.encode_PIL_Image(label_image)

        return feature_image, label_image

    # def encode_PIL_Image(self, image, channel_conversion='none'):
    #     if channel_conversion != 'none':
    #         if image.mode != channel_conversion:
    #             # convert to different image mode if necessary
    #             image = image.convert(channel_conversion)
    #     # convert to numpy array
    #     image = np.array(image)
    #     # add channel axis if input is grayscale image
    #     if image.ndim == 2:
    #         image = image[..., np.newaxis]
    #     elif image.ndim != 3:
    #         raise ValueError("Unhandled number of channels: %d" % image.ndim)
    #     # transpose to CHW
    #     image = image.transpose(2, 0, 1)
    #     return image

    @staticmethod
    @override
    def get_category():
        return "Images"

    @staticmethod
    @override
    def get_dataset_form():
        return DatasetForm()

    @staticmethod
    @override
    def get_dataset_template(form):
        """
        parameters:
        - form: form returned by get_dataset_form(). This may be populated
        with values if the job was cloned
        returns:
        - (template, context) tuple
          - template is a Jinja template to use for rendering dataset creation
          options
          - context is a dictionary of context variables to use for rendering
          the form
        """
        extension_dir = os.path.dirname(os.path.abspath(__file__))
        template = open(os.path.join(extension_dir, DATASET_TEMPLATE), "r").read()
        context = {'form': form, 'wipp_api_url': WIPP_API_URL}
        return (template, context)

    @staticmethod
    @override
    def get_id():
        return "image-wipp"

    @staticmethod
    @override
    def get_title():
        return "WIPP Segmentation"

    @override
    def itemize_entries(self, stage):
        if stage == constants.TEST_DB:
            # don't retun anything for the test stage
            return []

        if stage == constants.TRAIN_DB or (not self.has_val_folder):
            feature_image_list = self.make_image_list(self.feature_folder)
            label_image_list = self.make_image_list(self.label_folder)
        else:
            # separate validation images
            feature_image_list = self.make_image_list(self.validation_feature_folder)
            label_image_list = self.make_image_list(self.validation_label_folder)

        # make sure filenames match
        if len(feature_image_list) != len(label_image_list):
            raise ValueError(
                "Expect same number of images in feature and label folders (%d!=%d)"
                % (len(feature_image_list), len(label_image_list)))

        for idx in range(len(feature_image_list)):
            feature_name = os.path.splitext(
                os.path.split(feature_image_list[idx])[1])[0]
            label_name = os.path.splitext(
                os.path.split(label_image_list[idx])[1])[0]
            if feature_name != label_name:
                raise ValueError("No corresponding feature/label pair found for (%s,%s)"
                                 % (feature_name, label_name))

        # split lists if there is no val folder
        if not self.has_val_folder:
            feature_image_list = self.split_image_list(feature_image_list, stage)
            label_image_list = self.split_image_list(label_image_list, stage)

        return zip(
            feature_image_list,
            label_image_list)

    def make_image_list(self, folder):
        image_files = []
        for dirpath, dirnames, filenames in os.walk(folder, followlinks=True):
            for filename in filenames:
                if filename.lower().endswith(".ome.tif"):
                    image_files.append('%s' % os.path.join(dirpath, filename))
        if len(image_files) == 0:
            raise ValueError("Unable to find supported images in %s" % folder)
        return sorted(image_files)

    def split_image_list(self, filelist, stage):
        if self.random_indices is None:
            self.random_indices = range(len(filelist))
            random.shuffle(self.random_indices)
        elif len(filelist) != len(self.random_indices):
            raise ValueError(
                "Expect same number of images in folders (%d!=%d)"
                % (len(filelist), len(self.random_indices)))
        filelist = [filelist[idx] for idx in self.random_indices]
        pct_val = int(self.folder_pct_val)
        n_val_entries = int(math.floor(len(filelist) * pct_val / 100))
        if stage == constants.VAL_DB:
            return filelist[:n_val_entries]
        elif stage == constants.TRAIN_DB:
            return filelist[n_val_entries:]
        else:
            raise ValueError("Unknown stage: %s" % stage)
