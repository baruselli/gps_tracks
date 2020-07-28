from django.db import models
from django.conf import settings
import logging
logger = logging.getLogger("gps_tracks")
# Create your models here.

class Blacklist(models.Model):
    METHOD_CHOICES=[
        ["Exact","Exact"],
        ["Contains","Contains"],
        ["Regex","Regex"],
    ]

    file_name=models.CharField(max_length=512, verbose_name="File name", null=False, blank=False, unique=False)
    comment=models.CharField(max_length=512, verbose_name="Comment", null=True, blank=True, unique=False)
    modified = models.DateTimeField(auto_now=True, verbose_name="Date of modification", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Date of creation", null=True, blank=True)
    files = models.TextField(verbose_name="Associated files", null=True, blank=True, unique=False)
    interpret_regex = models.BooleanField(blank=True, default=False)
    method = models.CharField(max_length=15, verbose_name="Method of comparison", null=False, blank=False, default="Exact",choices=METHOD_CHOICES)
    
    reserved_code_all_tracks = "/*track*/" # code for all names of existing tracks

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
        else: #contains
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

    def test_files(self,files=None):
        """given a list of files, returns those which pass the test of the blacklist object"""
        import os
        if files is None:
            from import_app.utils import find_files_in_dir
            files=find_files_in_dir()

        #extract names without path and extensions
        file_names = [os.path.splitext(os.path.split(f)[-1])[0] for f in files]

        # here I have to compare with all existing tracks in db, so it is a bit complicated
        if self.reserved_code_all_tracks in self.file_name:
            from tracks.models import Track
            existing_tracks= Track.all_objects.all().values_list("name_wo_path_wo_ext",flat=True)
            if self.method=="Regex":
                pass
            elif self.method=="Exact":
                print("Exact")
                filtered_file_names=[]
                #sostituisco al codice i nomi di tutte le track
                modified_names = [self.file_name.replace(self.reserved_code_all_tracks,existing_name) for existing_name in existing_tracks]
                for n in file_names:
                    # se il nome del file è contenuto nella lista ottenuta sostituendo a /*track*/ il nome di ogni track esistente
                    # per esempio ho trackabc in db, la regola è /*tracks*/_5678 e il file è trackabc_5678
                    if n in modified_names:
                        filtered_file_names.append(n)
            else: #contains
                print("Contains")
                filtered_file_names=[]
                #sostituisco al codice i nomi di tutte le track
                modified_names = [self.file_name.replace(self.reserved_code_all_tracks,existing_name) for existing_name in existing_tracks]
                for n in file_names:
                    # se il nome del file è contiene almeno una stringa della lista ottenuta sostituendo a /*track*/ il nome di ogni track esistente
                    # per esempio ho trackabc in db, la regola è /*tracks*/_5678 e il file è trackabc_567890
                    # il modified_name matching sarebbe trackabc_5678 perchè il nome del file trackabc_567890 
                    # contiene trackabc_5678
                    if any(modified_name in n for modified_name in modified_names):
                        filtered_file_names.append(n)
        else:
            if self.method=="Regex":
                import re
                r = re.compile(self.file_name)
                filtered_file_names = list(filter(r.match, file_names))
            elif self.method=="Exact":
                filtered_file_names = [n for n in file_names if self.file_name == n]
            else: # existing track name contains this object name
                filtered_file_names = [n for n in file_names if self.file_name in n]

        return filtered_file_names



    @classmethod
    def all_test_files(cls,files):
        blacklisted_files=[]
        blacklisted_files_wo_path=[]
        import os
        import re

        existing_files= Track.all_objects.all().values_list("name_wo_path_wo_ext")

        for file in files:

            name_simple = os.path.splitext(os.path.split(file)[-1])[0]
            extension = os.path.splitext(file)[1]

            ##Blacklist
            # first check non regex names
            non_regex_names=cls.objects.all().filter(interpret_regex=False).values_list("file_name",flat=True)
            file_is_blacklisted=name_simple in non_regex_names
            # then regex ones
            if not file_is_blacklisted:
                regex_names = Blacklist.objects.all().filter(interpret_regex=True).values_list("file_name", flat=True)
                for regex_name in regex_names:
                    if re.search(regex_name,name_simple):
                        file_is_blacklisted=True
                        break
            if file_is_blacklisted:
                blacklisted_files.append(file)
                blacklisted_files_wo_path.append(name_simple)

        return {
            "blacklisted_files":blacklisted_files,
            "blacklisted_files_wo_path":blacklisted_files_wo_path,
        }   
        