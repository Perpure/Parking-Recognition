import base64
import datetime
from os.path import isfile, join
from mimetypes import MimeTypes
from os import listdir
import wand.image
import hashlib
import json
import hmac
import copy
import sys
import os

class Video(object):

    defaultUploadOptions = {
        "fieldname": "file",
        "validation": {
            "allowedExts": ["mp4", "webm", "ogg"],
            "allowedMimeTypes": ["video/mp4", "video/webm", "video/ogg"]
        }
    }

    @staticmethod
    def upload(req, fileRoute, options=None):
        """
        Video upload to disk.
        Parameters:
            req: framework adapter to http request. See BaseAdapter.
            fileRoute: string
            options: dict optional, see defaultUploadOptions attribute
        Return:
            dict: {link: "linkPath"}
        """

        if options is None:
            options = Video.defaultUploadOptions
        else:
            options = Utils.merge_dicts(Video.defaultUploadOptions, options)

        return File.upload(req, fileRoute, options)

    @staticmethod
    def delete(src):

        return File.delete(src)

    @staticmethod
    def list(folderPath, thumbPath = None):
        """
        List videos from disk.
        Parameters:
            folderPath: string
            thumbPath: string
        Return:
            list: list of videos dicts. example: [{url: "url", thumb: "thumb", name: "name"}, ...]
        """

        if thumbPath == None:
            thumbPath = folderPath

        # Array of Video objects to return.
        response = []

        absoluteFolderPath = Utils.getServerPath() + folderPath

        # Video types.
        videoTypes = Video.defaultUploadOptions["validation"]["allowedMimeTypes"]

        # Filenames in the uploads folder.
        fnames = [f for f in listdir(absoluteFolderPath) if isfile(join(absoluteFolderPath, f))]

        for fname in fnames:
            mime = MimeTypes()
            mimeType = mime.guess_type(absoluteFolderPath + fname)[0]

            if mimeType in videoTypes:
                response.append({
                    "url": folderPath + fname,
                    "thumb": thumbPath + fname,
                    "name": fname
                })

        return response