# Copyright (c) 2016-2017, NVIDIA CORPORATION.  All rights reserved.
from __future__ import absolute_import

import os
import wtforms

from flask_wtf import Form
from wtforms import validators

from digits import utils
from digits.utils import subclass
from digits.utils.forms import validate_required_iff

@subclass
class DatasetForm(Form):
    """
    A form used to create a WIPP image processing dataset
    """
   
    def validate_folder_path(form, field):
        if not field.data:
            pass
        else:
            # make sure the filesystem path exists
            if not os.path.exists(field.data) or not os.path.isdir(field.data):
                raise validators.ValidationError(
					'Folder does not exist or is not reachable: ' +
					field.data)
            else:
                return True

    def validate_file_path(form, field):
        if not field.data:
            pass
        else:
            # make sure the filesystem path exists
            if not os.path.exists(field.data) and not os.path.isdir(field.data):
                raise validators.ValidationError(
                    'File does not exist or is not reachable')
            else:
                return True

	# feature collection select
	# autocomplete field to select WIPP collection
    feature_folder_select = utils.forms.StringField(
        u'Feature image collection',
        validators=[
            validators.DataRequired()
        ],
        tooltip="Indicate the feature image collection."
    )

	# feature folder path - hidden field
	# set by Javascript to the selected WIPP image collection path
    feature_folder = wtforms.HiddenField(
        'feature_folder',
        validators=[
            validators.DataRequired(),
            validate_folder_path
        ]
    )

	# label collection select
	# autocomplete field to select WIPP collection
    label_folder_select = utils.forms.StringField(
        u'Label image collection',
        validators=[
            validators.DataRequired()
        ],
        tooltip="Indicate the label image collection. For each image in the feature"
                " image collection there must be one corresponding image in the label"
                " image collection. The label image must have the same filename except"
                " for the extension, which may differ. Label images are expected"
                " to be single-channel images (grayscale)."
    )

    # label folder path - hidden field
    # set by Javascript to the selected WIPP image collection path
    label_folder = wtforms.HiddenField(
        'label_folder',
        validators=[
            validators.DataRequired(),
            validate_folder_path
        ]
    )

    folder_pct_val = utils.forms.IntegerField(
        u'% for validation',
        default=10,
        validators=[
            validators.NumberRange(min=0, max=100)
        ],
        tooltip="You can choose to set apart a certain percentage of images "
                "from the training images for the validation set."
    )

    has_val_folder = utils.forms.BooleanField('Separate validation images',
                                              default=False,
                                              )

