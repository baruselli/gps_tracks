from django.db import models
from django.conf import settings
import logging
logger = logging.getLogger("gps_tracks")
# Create your models here.

class Blacklist(models.Model):
    file_name=models.CharField(max_length=512, verbose_name="File name", null=False, blank=False, unique=True)
    comment=models.CharField(max_length=512, verbose_name="Comment", null=True, blank=True, unique=False)
    modified = models.DateTimeField(auto_now=True, verbose_name="Date of modification", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Date of creation", null=True, blank=True)
    files = models.TextField(verbose_name="Associated files", null=True, blank=True, unique=False)
    interpret_regex = models.BooleanField(blank=True, default=False)

    class Meta:
        verbose_name = "Blacklist"
        ordering = ["pk"]
        #app_label = "tracks"

    def __unicode__(self):
        return "Blacklist" + str(self.pk)

    def __repr__(self):
        return "Blacklist"

    def __str__(self):
        return str(self.file_name)

    def save(self, *args, **kwargs):
        ## find associated blacklisted files
        from import_app.utils import find_files_in_dir_by_prefix, find_allfiles_in_dir
        self.files = ""
        # without regex
        if not self.interpret_regex:
            for f in find_files_in_dir_by_prefix(settings.TRACKS_DIR, self.file_name):
                logger.info(f)
                self.files += str(f) + "\n"
        # with regex
        else:
            import re
            import os
            all_files = find_allfiles_in_dir(settings.TRACKS_DIR)
            all_files_plus_simple_name = {f: os.path.splitext(os.path.basename(f))[0] for f in all_files}

            r = re.compile(self.file_name)
            ok_files = [f for f, name_simple in all_files_plus_simple_name.items() if r.search(name_simple)]
            for f in ok_files:
                logger.info(f)
                self.files += str(f) + "\n"

        super(Blacklist, self).save(*args, **kwargs)
