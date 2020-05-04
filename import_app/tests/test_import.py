from django.test import TestCase
from django.conf import settings
import os
from tracks.models import Track
from options.models import OptionSet

# Create your tests here.

class ImportGpxTestCase(TestCase):

    def setUp(self):
        # deactivate geopy during tests
        OptionSet.set_option("USE_GEOPY",False)
        OptionSet.set_option("MAX_POINTS_TRACK",100)
        OptionSet.set_option("MAX_POINTS_TRACK_CALCULATION",300)


    def test_import(self):

        print("test_import")
        from import_app.utils import generate_tracks

        this_dir=os.path.join(settings.BASE_DIR, "import_app","tests","test_files")

        ## test GPX
        generate_tracks(this_dir, extensions=[".gpx"], update=False)
        test_gpx_mytracks = Track.objects.get(name_wo_path_wo_ext="test_gpx_mytracks")
        self.assertEqual(test_gpx_mytracks.log.errors,"")
        self.assertEqual(test_gpx_mytracks.log.warnings,"")
        test_gpx_tomtom = Track.objects.get(name_wo_path_wo_ext="test_gpx_tomtom")
        self.assertEqual(test_gpx_tomtom.log.errors,"")
        self.assertEqual(test_gpx_tomtom.log.warnings,"")

        # ## test KMZ
        # generate_tracks(this_dir, extensions=[".kmz"], update=False)
        # test_kmz_mytracks = Track.objects.get(name_wo_path_wo_ext="test_kmz_mytracks")
        # self.assertEqual(test_kmz_mytracks.log.errors,"")
        # self.assertEqual(test_kmz_mytracks.log.warnings,"")

        ## test KML
        # with gx
        generate_tracks(this_dir, extensions=[".kml"], update=False)
        test_kml_geotracker = Track.objects.get(name_wo_path_wo_ext="test_kml_geotracker")
        self.assertEqual(test_kml_geotracker.log.errors,"")
        self.assertEqual(test_kml_geotracker.log.warnings,"")

        # without gx tags, example from sygic
        # this will give a "Cannot find td_computed_speed_rolling" warning, 
        # because it has no times, that is ok
        # I check that there are no other warnings
        test_kml_sygic = Track.objects.get(name_wo_path_wo_ext="test_kml_sygic")
        self.assertEqual(test_kml_sygic.log.errors,"")
        warnings_list=test_kml_sygic.log.get_messages("warning")
        warnings_list_clean=[w for w in warnings_list if not "td_computed_speed_rolling" in w]
        self.assertEqual(warnings_list_clean,[])
        # same for tomtom
        test_kml_tomtom = Track.objects.get(name_wo_path_wo_ext="test_kml_tomtom")
        self.assertEqual(test_kml_tomtom.log.errors,"")
        warnings_list=test_kml_tomtom.log.get_messages("warning")
        warnings_list_clean=[w for w in warnings_list if not "td_computed_speed_rolling" in w]
        self.assertEqual(warnings_list_clean,[])

        ## test TCX
        generate_tracks(this_dir, extensions=[".tcx"], update=False)
        test_tcx_tomtom = Track.objects.get(name_wo_path_wo_ext="test_tcx_tomtom")
        self.assertEqual(test_tcx_tomtom.log.errors,"")
        self.assertEqual(test_tcx_tomtom.log.warnings,"")

        ## test csv
        generate_tracks(this_dir, extensions=[".csv"], update=False)
        test_csv_tomtom = Track.objects.get(name_wo_path_wo_ext="testcsvtomtom_2018-11-15_18-15-22")
        self.assertEqual(test_csv_tomtom.log.errors,"")
        self.assertEqual(test_csv_tomtom.log.warnings,"")

      
        ## compare the 4 tracks from tomtom, which are the same track!

        # exact checks
        fields_to_check=[
            "n_points","beginning","end","duration",
            "has_times" 
            ,"has_alts",
            ]
        for field in fields_to_check:
            print(field)
            self.assertEqual(getattr(test_gpx_tomtom,field),getattr(test_tcx_tomtom,field) )
            self.assertEqual(getattr(test_gpx_tomtom,field),getattr(test_csv_tomtom,field) )

        fields_to_check=[
            "n_points",
            ]
        for field in fields_to_check:
            print(field)
            self.assertEqual(getattr(test_gpx_tomtom,field),getattr(test_kml_tomtom,field) )

        ## checks for floats
        fields_to_check=[
            "min_lat","max_lat","min_long","max_long","avg_lat","avg_long",
            "initial_lat", "final_lat","initial_lon","final_lon",
            ]
        for field in fields_to_check:
            print(field)
            self.assertAlmostEqual(getattr(test_gpx_tomtom,field),getattr(test_kml_tomtom,field),3 )
            self.assertAlmostEqual(getattr(test_gpx_tomtom,field),getattr(test_tcx_tomtom,field),3 )
            self.assertAlmostEqual(getattr(test_gpx_tomtom,field),getattr(test_csv_tomtom,field),3 )
        # not for kml
        fields_to_check=[
            "avg_alt","min_alt","max_alt",
            ]
        for field in fields_to_check:
            print(field)
            self.assertAlmostEqual(getattr(test_gpx_tomtom,field),getattr(test_tcx_tomtom,field),3 )
            self.assertAlmostEqual(getattr(test_gpx_tomtom,field),getattr(test_csv_tomtom,field),3 )
        ## checks for floats, 0 decimal places (precision up to 10 m)
        fields_to_check=[
            "length_2d",
            ]
        for field in fields_to_check:
            print(field)
            self.assertAlmostEqual(getattr(test_gpx_tomtom,field)/10,getattr(test_kml_tomtom,field)/10,0 )
            self.assertAlmostEqual(getattr(test_gpx_tomtom,field)/10,getattr(test_tcx_tomtom,field)/10,0 )
            self.assertAlmostEqual(getattr(test_gpx_tomtom,field)/10,getattr(test_csv_tomtom,field)/10,0 )
        
        # heartrate, both csv and tcx
        fields_to_check=[
            "max_cardio","min_cardio","has_hr"#,"total_heartbeat"
            ]
        for field in fields_to_check:
            print(field)
            self.assertEqual(getattr(test_csv_tomtom,field),getattr(test_tcx_tomtom,field) )




