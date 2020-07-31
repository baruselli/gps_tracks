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
    comment=models.TextField(max_length=512, verbose_name="Comment", null=True, blank=True, unique=False)
    modified = models.DateTimeField(auto_now=True, verbose_name="Date of modification", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Date of creation", null=True, blank=True)
    files = models.TextField(verbose_name="Associated files", null=True, blank=True, unique=False)
    method = models.CharField(max_length=15, verbose_name="Method of comparison", null=False, blank=False, default="Exact",choices=METHOD_CHOICES)
    number_matched_files = models.IntegerField(blank=True, default=0)
    active = models.BooleanField(blank=True, default=True)
    
    reserved_code_all_tracks = "/*track*/" # code for all names of existing tracks

    class Meta:
        verbose_name = "Blacklist"
        ordering = ["pk"]
        #app_label = "tracks"

    def __unicode__(self):
        return "Blacklist" + str(self.pk)

    def __repr__(self):
        return "Blacklist %s - %s" %(file_name,method)

    def __str__(self):
        return str(self.file_name)

    def save(self, cascade=True, *args, **kwargs):
        ## find associated blacklisted files
        # from import_app.utils import find_files_in_dir_by_prefix, find_allfiles_in_dir
        # self.files = ""
        # # without regex
        # if not self.interpret_regex:
        #     for f in find_files_in_dir_by_prefix(settings.TRACKS_DIR, self.file_name):
        #         logger.info(f)
        #         self.files += str(f) + "\n"
        # # with regex
        # else: #contains
        #     import re
        #     import os
        #     all_files = find_allfiles_in_dir(settings.TRACKS_DIR)
        #     all_files_plus_simple_name = {f: os.path.splitext(os.path.basename(f))[0] for f in all_files}

        #     r = re.compile(self.file_name)
        #     ok_files = [f for f, name_simple in all_files_plus_simple_name.items() if r.search(name_simple)]
        #     for f in ok_files:
        #         logger.info(f)

        if cascade:
            self.test_files()

        super(Blacklist, self).save(*args, **kwargs)

    def test_files(self,files=None, save_cache=False):
        """given a list of files, returns those which pass the test of the blacklist object"""
        import os
        if files is None:
            from import_app.utils import find_files_in_dir
            save_cache=True
            files=find_files_in_dir()
        

        logger.info("%s test_files" %self)

        #extract names without path and extensions
        file_names = [os.path.splitext(os.path.split(f)[-1])[0] for f in files]

        if self.active:
            # here I have to compare with all existing tracks in db, so it is a bit complicated
            if self.reserved_code_all_tracks in self.file_name:
                from tracks.models import Track
                existing_tracks= Track.all_objects.all().values_list("name_wo_path_wo_ext",flat=True)
                if self.method=="Regex":
                    import time
                    start=time.time()
                    # se il nome del file corrisponde ad almeno una regex della lista ottenuta sostituendo a /*track*/ il nome di ogni track esistente
                    # per esempio ho trackabc in db, la regola è /*tracks*/_[0-9]+$ e il file è trackabc_567890
                    # la regex matching sarebbe trackabc_[0-9]+ perchè il nome del file trackabc_567890 
                    # soddisfa la regex trackabc_[0-9]+
                    filtered_file_names=[]
                    all_tracks_string="("+"|".join(existing_tracks)+")"

                    regex=self.file_name.replace(self.reserved_code_all_tracks,all_tracks_string)
                    import re
                    r = re.compile(regex)
                    filtered_file_names=list(filter(r.search, file_names))
                    end=time.time()
                    logger.info("Regex time: %s" %(end-start))
                elif self.method=="Exact":
                    filtered_file_names=[]
                    #sostituisco al codice i nomi di tutte le track
                    modified_names = [self.file_name.replace(self.reserved_code_all_tracks,existing_name) for existing_name in existing_tracks]
                    for n in file_names:
                        # se il nome del file è contenuto nella lista ottenuta sostituendo a /*track*/ il nome di ogni track esistente
                        # per esempio ho trackabc in db, la regola è /*tracks*/_5678 e il file è trackabc_5678
                        if n in modified_names:
                            filtered_file_names.append(n)
                else: #contains
                    filtered_file_names=[]
                    #sostituisco al codice i nomi di tutte le track
                    modified_names = [self.file_name.replace(self.reserved_code_all_tracks,existing_name) for existing_name in existing_tracks]
                    for n in file_names:
                        # se il nome del file contiene almeno una stringa della lista ottenuta sostituendo a /*track*/ il nome di ogni track esistente
                        # per esempio ho trackabc in db, la regola è /*tracks*/_5678 e il file è trackabc_567890
                        # il modified_name matching sarebbe trackabc_5678 perchè il nome del file trackabc_567890 
                        # contiene trackabc_5678
                        if any(modified_name in n for modified_name in modified_names):
                            filtered_file_names.append(n)
            else:
                if self.method=="Regex":
                    import re
                    r = re.compile(self.file_name)
                    filtered_file_names = list(filter(r.search, file_names))
                elif self.method=="Exact":
                    filtered_file_names = [n for n in file_names if self.file_name == n]
                else: # existing track name contains this object name
                    filtered_file_names = [n for n in file_names if self.file_name in n]
        else:
            filtered_file_names=[]

        paths=[f for f in files if os.path.splitext(os.path.split(f)[-1])[0] in filtered_file_names]

        # caches results (only when tested on all files)
        if save_cache:
            self.files = ""
            self.number_matched_files=0
            for f in paths:
                self.number_matched_files+=1
                self.files += str(f) + "\n"
            self.save(cascade=False) #otherwise it relaunches this method

        # returns the full path, if the name wo path wo ext is in the filtered list
        return {
            "paths":paths,
            "names":filtered_file_names
        }

        #return filtered_file_names



    @classmethod
    def all_test_files(cls,files=None,full_report=False):
        logger.info("Blacklist all_test_files")

        save_cache=False
        if files is None:
            from import_app.utils import find_files_in_dir
            save_cache=True
            files=find_files_in_dir()


        all_paths=[]
        all_names=[]

        # per ogni file (con o senza path) in blacklist, dà lista degli oggetti che lo bloccano
        dict_names_objs={}
        dict_paths_objs={}

        for obj in cls.objects.filter(active=True):
            result=obj.test_files(files,save_cache=save_cache) # I can save in cache if i am passing all files
            paths=result["paths"]
            names=result["names"]
            all_paths.extend(paths)
            all_names.extend(names)
            if full_report:
                for name in names:
                    if name in dict_names_objs:
                        dict_names_objs[name].append(obj)
                    else:
                        dict_names_objs[name]=[obj]
                for path in paths:
                    if path in dict_paths_objs:
                        dict_paths_objs[path].append(obj)
                    else:
                        dict_paths_objs[path]=[obj]

        logger.info("End Blacklist all_test_files")

        return{
            "paths":all_paths,
            "names":all_names,
            "dict_names_objs":dict_names_objs,
            "dict_paths_objs":dict_paths_objs
        }
        