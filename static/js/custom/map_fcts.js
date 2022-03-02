function init_map_base(map,options,mapBounds=null,add_basemaps=true,track_pk=-1){


    map_right_click(map,options,point_link,waypoint_link,track_pk );

    map.addControl(new L.Control.Fullscreen());
    if (add_basemaps){
        L.control.layers(baseMaps).addTo(map);
        //put the first map as selected, otherwise the radio button is empty for all
        $("input:radio[name=leaflet-base-layers]:first").prop('checked', true);
    }
    var ok_bounds=false
    if (mapBounds!=null && mapBounds!={}){
    //console.log("mapBounds", mapBounds)
        try{
            map.fitBounds(mapBounds);
            function locateBounds () {
                return L.latLngBounds(mapBounds);
               }
            (new L.Control.ResetView(locateBounds)).addTo(map);
            ok_bounds=true
        }catch(error){
            console.log(error)
        }
    }
    if (!ok_bounds){
        console.log("Map bounds not OK, hiding reset button")
        $(".leaflet-control-zoom-out.leaflet-bar-part").hide()
    }

}

function default_point_properties(type="point",reset="reset"){
    var a={}

    if (type=="point"){
        if (reset=="reset"){
            a["fill-opacity"]=1
            a["stroke-width"]=3
        }
        if (reset=="highlight"){
            a["fill-opacity"]=1
            a["stroke-width"]=30
        }
        if (reset=="highlight_small"){
            a["fill-opacity"]=1
            a["stroke-width"]=10
        }
    }

    if (type=="path"){
        if (reset=="reset"){
            a["weight"]=3     //sets the stroke-width with setstyle(weight:)
            a["stroke-width"]=a["weight"] //sets the stroke-width of the html path object
        }
        if (reset=="highlight"){
            a["weight"]=9
            a["stroke-width"]=a["weight"]
        }
    }
    return a
}

function reset_point_sizes(class_name="leaflet_track_point", how="reset"){
    console.log("reset_point_sizes", class_name )
    //get all points
    var a=document.getElementsByClassName(class_name)
    //leaflet_trackline_marker is class for path (track as line)
    type="point"

    if(a){
        if (a[0] && a[0].classList && a[0].classList.contains("leaflet_trackline_marker")){
            type="path"
        }
        console.log("lots", type,how)
        //get properties to apply
        default_properties = default_point_properties(type=type,reset=how)
        if (type=="point"){
            fill_opacity=default_properties["fill-opacity"]
            stroke_width=default_properties["stroke-width"]
            console.log("point", fill_opacity, stroke_width)
            //and paste them to all points
            for (j = 0; j < a.length; j++){
                a[j].setAttribute("fill-opacity",fill_opacity)
                a[j].setAttribute("stroke-width",stroke_width)
            }
        }
        if (type=="path"){
            weight=default_properties["weight"]
            stroke_width=default_properties["stroke-width"]
            console.log("path", weight)
            //and paste them to all points
            for (j = 0; j < a.length; j++){
                a[j].setAttribute("weight",weight)
                a[j].setAttribute("stroke-width",stroke_width)
            }
        }
    }
}

function delete_hand_markers(map) {
    for(i=0;i<hand_markers.length;i++) {
        map.removeLayer(hand_markers[i]);
    }  
}


function map_right_click (map, options, link,link2,track_pk=-1){
    map.on("contextmenu", function (event) {
    if (!event.originalEvent.ctrlKey){
        delete_hand_markers(map)
    }
    ll=event.latlng
    string=ll.toString()
    var lat= ll["lat"]
    var lng=ll["lng"]
    var dist=10
    //string0="("+lat+","+long+")<br>"
    string0="<b>"+string+"</b><br>"
    //string1="<a  target='_blank' href='"+link+"?lat="+lat+"&lng="+lng+"&dist="+1+"'>"+"Tracks within 1 km"+"</a><br>"
    //string2="<a  target='' href='"+link+"?lat="+lat+"&lng="+lng+"&dist="+10+"'>"+"Tracks within 10 km"+"</a><br>"
    //string3="<a  target='_blank' href='"+link+"?lat="+lat+"&lng="+lng+"&dist="+100+"'>"+"Tracks within 100 km"+"</a><br>"
    string3="Tracks within"+
                "<form style='display:inline;margin:0px;padding:0px;' target='_blank' action='"+link+"'>"+
                "<input type='hidden' name='lat' value="+lat+">"+
                "<input type='hidden' name='lng' value="+lng+">"+
                "<input name='dist' value=3 type='number' min='1' max='100'>km <br>"+
                '<input type="checkbox" name="with_waypoints" value=1 >Waypoints'+
                '<input type="checkbox" name="with_photos" value=1 >Photos<br>'+
                '<input type="hidden" name="exclude_excluded_groups" value=1 >'+
                "<input type='submit' value='OK'></form><br>"
    string4="<a  target='_blank' href='"+link2+"?lat="+lat+"&lng="+lng+"&track_pk="+track_pk+"'>"+"Create waypoint"+"</a><br>"
    string5="<a  target='_blank' href=https://www.google.it/maps/@"+lat+","+lng+",15z>"+"Google Maps"+"</a><br>"
    string6="<a  target='_blank' href=https://www.openstreetmap.org/?lat="+lat+"&lon="+lng+"&zoom=15&layers=M>"+"OpenStreetMap"+"</a> / "
    string7="<a  target='_blank' href=https://www.opentopomap.org/#map=15/"+lat+"/"+lng+">"+"OpenTopoMap"+"</a>"
    console.log("Coordinates: " + lat +", "+ lng );
    marker=L.marker(event.latlng,{icon: icon_objs["purple"]}).addTo(map).bindPopup(string0+string3+string4+string5+string6+string7);
    hand_markers.push(marker)
  // this is only needed in tracks_list.html
  try{
    document.getElementById("searchbox_lat").value = lat;
    document.getElementById("searchbox_long").value = lng;
    }catch(error){}

});
}

function map_right_click_line (map, options, link,link2){
  map.on("contextmenu", function (event) {
  ll=event.latlng
  string=ll.toString()
  var lat= ll["lat"]
  var lng=ll["lng"]
  var dist=10
  //string0="("+lat+","+long+")<br>"
  string0=string+"<br>"
  string1="<a  target='_blank' href='"+link+"?lat="+lat+"&lng="+lng+"&dist="+dist+"'>"+"Nearby tracks"+"</a><br>"  
  string2="<a  target='_blank' href='"+link2+"?lat="+lat+"&lng="+lng+"'>"+"Create waypoint"+"</a>"  
  console.log("Coordinates: " + lat +", "+ lng );
  document.getElementById("id_lats_text").value += lat+",\n";
  document.getElementById("id_long_text").value += lng+",\n";
  document.getElementById("id_alts_text").value += "0"+",\n";
  console.log(string0);
  console.log(string1);
  console.log(string2);
L.marker(event.latlng).addTo(map).bindPopup(string0+string1+string2);
});
}

function map_right_click_null (map, options){
    map.on("contextmenu", function (event) {})  
}


function map_right_click_laps (map, options, link,link2,radius=10){
  map.on("contextmenu", function (event) {
    console.log("radius",radius)
  ll=event.latlng
  string=ll.toString()
  var lat= ll["lat"]
  var lng=ll["lng"]
  var dist=10
  //string0="("+lat+","+long+")<br>"
  string0=string+"<br>"
  string1="<a  target='_blank' href='"+link+"?lat="+lat+"&lng="+lng+"&dist="+dist+"'>"+"Nearby tracks"+"</a><br>"  
  string2="<a  target='_blank' href='"+link2+"?lat="+lat+"&lng="+lng+"'>"+"Create waypoint"+"</a>"  
  console.log("Coordinates: " + lat +", "+ lng );
  document.getElementById("id_starting_lat").value = lat;
  document.getElementById("id_starting_lon").value = lng;
  console.log(string0);
  console.log(string1);
  console.log(string2);
 L.circle(event.latlng,{radius:radius,color:"red"}).addTo(map).bindPopup(string0+string1+string2);
});
}

function point_popup(feature, full=true,show_subtrack_name=false){
            name=""
            if(feature.track_name && feature.color)
            name+="<b><font color="+feature.color+">"+ feature.track_name+"</font></b><br>"
            if(feature.ReducedNumber != undefined | feature.OriginalNumber != undefined )
               name+="Point: "+ parseInt(feature.ReducedNumber)+" ("+parseInt(feature.OriginalNumber)+")<br>"
            if(feature.TimeString)       name+="Time: "+ feature.TimeString +"<br>"
            if(feature.DeltaTimeString) name+="Duration: " + feature.DeltaTimeString +"<br>"
            if(feature.Distance !=undefined)       name+="Distance: "+ parseFloat(feature.Distance).toFixed(2)+"km<br>"
            if(feature.Altitude!=undefined)        name+="<font color="+feature.ColorAltitude+">Altitude: "+String(parseFloat(feature.Altitude).toFixed(0)) +"m<br></font>";
            if (full){
                if(feature.Slope!=undefined)      name+="<font color="+feature.ColorSlope+">Slope: "+String(parseFloat(feature.Slope).toFixed(1)) +"%<br></font>";
                if(feature.VerticalSpeed!=undefined)      name+="<font color="+feature.ColorVerticalSpeed+">Vertical speed: "+String(parseFloat(feature.VerticalSpeed).toFixed(2))+"m/s<br></font>";
                if(feature.Speed!=undefined)      name+="<font color="+feature.ColorSpeed+">Speed: "+String(parseFloat(feature.Speed).toFixed(1)) +"km/h<br></font>";
                if(feature.Pace!=undefined)      name+="Pace: "+feature.Pace +"<br>";
                if(feature.Frequency!=undefined)       name+="<font color="+feature.ColorFrequency+">Frequency: "+parseInt(feature.Frequency)+"</font><br>"
                if(feature.StepLength!=undefined)       name+="<font color="+"black"+">StepLength: "+parseFloat(feature.StepLength).toFixed(2)+"m</font><br>"
                if(feature.Heartrate!=undefined)         name+="<font color="+feature.ColorHeartrate+">Heartrate: "+parseInt(feature.Heartrate)+"</font><br>"
                if(feature.HeartrateGroup!=undefined)         name+="<font color="+feature.ColorHeartrateGroup+">Hr group: "+(feature.HeartrateGroup)+"</font><br>"
                if(feature.Split!=undefined)         name+="<font color="+feature.ColorSplit+">Split: "+parseInt(feature.Split)+"</font><br>"
                if(feature.LapName!=undefined)         name+="<font color="+feature.ColorLap+">"+feature.LapName+"</font><br>"
                if(feature.Segment!=undefined)         name+="<font color="+feature.ColorSegment+">Segment: "+feature.Segment+"</font><br>"
                if(feature.SubtrackName!=undefined)         name+="<font color="+feature.ColorSubtrack+">Subtrack: "+feature.Subtrack + " - " + feature.SubtrackName+"</font><br>"
            }
            if(show_subtrack_name && !full){
                if(feature.SubtrackName!=undefined)         name+="<font color="+feature.ColorSubtrack+">Subtrack: "+feature.Subtrack + " - " + feature.SubtrackName+"</font><br>"
            }
            return name
            }

function track_layer_fromjson(data,geojsonMarkerOptions,options={}){

    var t0 = performance.now();

    color_feature=options.color_feature,
    filter_point_type=options.filter_point_type||"track",
    filter=options.filter===true //default false
    table=options.table
    track_name=options.track_name
    //external=options.external===true //def false,
    split=options.split,
    lap=options.lap,
    do_popup=options.do_popup!==false //default true
    var debug = options.debug===true;
    show_subtrack_name=options.show_subtrack_name===true;

    if(debug) console.log("track_layer_fromjson options", options, geojsonMarkerOptions)

    if(debug) console.log("track_layer_fromjson data", data)

    try{
        gj= L.geoJson(data,
            {
            //filter out points by right point_type
            filter: function(feature, layer) {
                if(filter){
                    if (split){
                        return feature.split===split
                    }else if (lap!=null){
                        return feature.lap===lap
                    }
                    else if(track_name==null){   //only filter by point type
                        return feature.point_type===filter_point_type
                    }else{ //filter by point type and track_name
                    return feature.point_type===filter_point_type & feature.track_name===track_name
                    }
                //}else if (external){ //probably not needed
                //    return  feature.point_type === undefined //all external geojson, which does not have point_type
                }else{
                    return true
                }
            },
            // this is only set for lines or geojson
            style:function(feature, layer){
                if (feature.point_type==="global_line"){
                    color=feature.properties.color
                    if (!color) color="black"
                    return {"color":color,
                        weight: 3,   opacity: 0.5,   smoothFactor: 1}
                }
                if (feature.point_type==="external_geojson"){
                    console.log(feature)
                    if (feature["properties"] && feature["properties"]["color"]){
                        color=feature["properties"]["color"]
                    }else{
                        color="blue"
                    }
                    return {"color":color}
                }
            },
            onEachFeature: function (feature, layer){
                //console.log(feature.type,feature.point_type)
                //global_line
                if (feature.type==="Feature" & feature.point_type==="global_line"){
                    layer.bindPopup(feature.properties.popupContent);
                // track as linestring
                } else if (feature.type==="Feature" & feature.point_type==="track_as_line"){

                    default_properties = default_point_properties(type="path",reset="reset")

                    if (feature.link != null && feature.link != undefined){
                        var name="<a href='"+feature.link+"'><b>"+feature.name+"</b></a>";
                    }else{
                        var name="<b>"+feature.name+"</b>";
                    }

                    // add groups if present
                    if (feature.Groups){
                        for (var i in  feature.Groups){
                            g=feature.Groups[i]
                            name+="<br><a href='"+g[1]+"'>"+g[0]+"</a>"
                        }
                    }
                    layer.setStyle({
                        'color': feature.color,
                        "weight" : default_properties["weight"],
                        // following properties seem to be ignored
    //                    "width":30, //default_properties["stroke-width"],
    //                    "stroke-width" : default_properties["stroke-width"]
                    });
                    layer.bindPopup(name);
    //                 layer.on('mouseover', function (e) {
    //                     this.openPopup();
    //                     this.setStyle({"weight": 10});
    //                     this.bringToFront();
    //                });
                    layer.on('click', function (e) {
                        console.log("------click on track as line ------")
                        this.openPopup();
                        this.setStyle({"weight": 10});
                        this.bringToFront();
                        //mark the corresponding row in the table, if a table is given
                        if (table) {
                            // if i ctrl-click, keep selected rows
                            //otherwise deselect_all
                            if (!e.originalEvent.ctrlKey){
                                console.log("deselecting all rows")
                                table.rows().deselect();
                            }
                            // // select corresponding row
                            // table.rows().every(function ( rowIdx, tableLoop, rowLoop ){
                            //     var data = this.data();
                            //     if (e.target.feature.pk == data.pk){
                            //         console.log("selecting row", rowIdx, "with pk", data.pk)
                            //         table.row(rowIdx).select()
                            //     }
                            // })
                        //copied from below
                            //find row_index
                            //and check if row was already selected
                            table.rows().every(function ( rowIdx, tableLoop, rowLoop ){
                                var data = this.data();
                                if (e.target.feature.pk == data.pk){
                                    row_index = rowIdx
                                    //TODO: check if row is already selected, this does not work
                                    //console.log( table.rows({ selected: true }))
                                    selected_rows = table.rows({ selected: true })[0]
                                    //console.log(selected_rows, "selected_row", table.rows({ selected: true }))
                                    was_already_selected = selected_rows.includes(row_index)
                                    //console.log("row_index", row_index, "pk", data.pk)
                                }
                            })

                            //console.log("was_already_selected",was_already_selected)

                            // if i ctrl-click, dont reset selected rows
                            if (e.originalEvent.ctrlKey){
                                //if it was already selected, deselect
                                if (was_already_selected){
                                    table.row(row_index).deselect()
                                //if it was not selected, select
                                }else{
                                    table.row(row_index).select()
                                }
                            //if not ctlr-click, deselect_all
                            }else{
                                console.log("deselecting all rows")
                                table.rows().deselect();
                                // then select row
                                table.row(row_index).select()
                            }
                        }

                        // keep track of selected tracks if no table (e.g. in emptymap)
                        if(!table && window.selected_tracks != undefined){
                            var was_already_selected = window.selected_tracks.includes(feature.pk)
                            if (!e.originalEvent.ctrlKey){
                                //select only this one
                                window.selected_tracks=[feature.pk]
                            }
                            else if (was_already_selected && e.originalEvent.ctrlKey){
                                //deselect this
                                window.selected_tracks.splice(window.selected_tracks.indexOf(feature.pk), 1);
                            }else if (!was_already_selected) {
                                window.selected_tracks.push(feature.pk)
                            }
                            highlight_leaflet_points(number=null,class_name="leaflet_track_marker", track_pks=window.selected_tracks)
                        }

                        //  //row( e.target.id ).nodes().to$().addClass( 'selected' )
                    });
                    //   layer.on('mouseout', function (e) {
                    //     //this.closePopup();
                    //     this.setStyle({"weight": 5});
                    //  });
                    layer.setStyle({'className': 'leaflet_track_marker leaflet_trackline_marker leaflet_track_'+feature.pk}) //I assign a class to find these markers
                } else if (feature.external_geojson_name){
                    // only works if geojson is a single feature
                    // if it is a feature collection, features are taken as children of the object that 
                    // has external_geojson_name property, so this part is skipped
                    popup_text=feature.external_geojson_name
                    layer.bindPopup(popup_text);
                    layer.on('click', function (e) {
                        console.log("------click on external_geojson  ------")
                        this.openPopup();
                        this.setStyle({"weight": 8});
                        this.bringToFront();
                    });
                    layer.on('mouseover', function (e) {
                        this.setStyle({"weight": 8});
                    });
                    layer.on('mouseout', function (e) {
                        this.setStyle({"weight": 3});
                    });
                } else if (feature.feature_for_name){
                    //this works for a featurecollection of external geojson
                    // in case of geojson with feature collection, I give feature_for_name
                    // to all children, see get_geojson
                    feature_for_name=feature.feature_for_name
                    if (feature_for_name && feature.properties[feature_for_name]){
                        popup_text=feature.properties[feature_for_name]
                        layer.bindPopup(popup_text);
                        layer.on('click', function (e) {
                            console.log("------click on external_geojson  ------")
                            this.openPopup();
                            this.setStyle({"weight": 8});
                            this.bringToFront();
                        });
                        layer.on('mouseover', function (e) {
                            this.setStyle({"weight": 8});
                        });
                        layer.on('mouseout', function (e) {
                            this.setStyle({"weight": 3});
                        });
                        }
                }
            },
            // all the rest are points, so I create marker and assign popup here
            pointToLayer: function (feature, latlng) {
                // point from the track
                if (feature.type==="Point"){
                    if(color_feature){
                        geojsonMarkerOptions.color=feature[color_feature]
                    }else{
                        geojsonMarkerOptions.color="blue"
                    }
                    var marker =L.circle(latlng, geojsonMarkerOptions);
                    if (do_popup){
                        marker.bindPopup(point_popup(feature, full=false,show_subtrack_name=show_subtrack_name))
                    }
                    marker.on('mouseover', function (e) {
                        this.openPopup();
                        this.setStyle({"weight": 10});
                        this.bringToFront();
                    });
                    marker.on('click', function (e) {
                        console.log("----------------click on track point-----------------")
                        //console.log(e);console.log(e.target.id);
                        highlight_c3_points(e.target.id)
                        this.openPopup();
                        this.setStyle({"weight": 10});
                        this.bringToFront();
                    });
                    marker.on('mouseout', function (e) {
                        this.closePopup();
                        this.setStyle({"weight": 5});
                    });
                    marker.id=feature.ReducedNumber
                    //many tracks
                    if (feature.is_from_many_tracks){
                        marker.setStyle({'className': 'leaflet_track_point leaflet_track_point_many_tracks leaflet_track_'+feature.track_pk})
                    }
                    else{
                        marker.setStyle({'className': 'leaflet_track_point leaflet_track_point_single_track leaflet_track_'+feature.track_pk})
                    }
                    return marker
                // waypoints
                }else if (feature.type==="Feature" & (feature.point_type==="waypoint"||feature.point_type==="global_waypoint" )){
                    if (feature.n_elements!== undefined){
                        var name=""
                        for (i=0;i<feature.n_elements;i++){
                            name+="<a href='"+feature.link[i]+"'><b>"+feature.name[i]+"</b></a><br>"+ feature.alt[i]+"m   "+feature.time[i]+"<br>"+feature.description[i]+"<br>";
                        }
                    }else{
                        var name="<a href='"+feature.link+"'><b>"+feature.name+"</b></a><br>"+ feature.alt+"m<br>"+feature.time+"<br>"+feature.description;
                    }
                    if (feature.point_type=="waypoint"){
                        var marker=L.marker(latlng).bindPopup(name)
                    }else{
                        var marker=L.marker(latlng,{icon: icon_objs["lightblue"]}).bindPopup(name)
                    }
                    return marker
                // photos
                }else if (feature.type==="Feature" & feature.point_type==="photo"){
                //console.log(feature)
                    //case of clustered photos
                    if (feature.n_elements!== undefined){
                        var name=""
                        for (i=0;i<feature.n_elements;i++){
                            //name+='<div style="width:40%;float:left; margin-left: 1%;margin-top: 1%">'
    //                        name+='<div style="width:19%;float:left; margin-left: 1%;margin-top: 1%">'
    //                        name+="<a href='"+feature.link[i]+"'><img src='"+feature.url_path[i]+"'  width=100%><br>"//+
    //                        name+="</div>"
                            name+="<a href='"+feature.link[i]+"'><img src='"+feature.thumbnail_url_path[i]+"'  width='200'></a>"//+
                            //feature.name[i]+" "
                            //+feature.time[i]+"</a><br>";
                            //name+="</div>"
                            switch(feature.n_elements) {
                                case 1: var marker=L.marker(latlng,{icon: icon_objs["red"]}).bindPopup(name);break;
                                case 2: var marker=L.marker(latlng,{icon: icon_objs["red2"]}).bindPopup(name,{className: 'popup_many_photos_width_2' });break;
                                case 3: var marker=L.marker(latlng,{icon: icon_objs["red3"]}).bindPopup(name,{className: 'popup_many_photos_width_3' });break;
                                case 4: var marker=L.marker(latlng,{icon: icon_objs["red4"]}).bindPopup(name,{className: 'popup_many_photos_width_2' });break;
                                case 5: var marker=L.marker(latlng,{icon: icon_objs["red5"]}).bindPopup(name,{className: 'popup_many_photos_width_3' });break;
                                case 6: var marker=L.marker(latlng,{icon: icon_objs["red5"]}).bindPopup(name,{className: 'popup_many_photos_width_3' });break;
                                case 7: var marker=L.marker(latlng,{icon: icon_objs["red5"]}).bindPopup(name,{className: 'popup_many_photos_width_3' });break;
                                case 8: var marker=L.marker(latlng,{icon: icon_objs["red5"]}).bindPopup(name,{className: 'popup_many_photos_width_4' });break;
                                case 9: var marker=L.marker(latlng,{icon: icon_objs["red5"]}).bindPopup(name,{className: 'popup_many_photos_width_3' });break;
                                default: var marker=L.marker(latlng,{icon: icon_objs["red5"]}).bindPopup(name,{className: 'popup_many_photos_width_4' });break;
                            }
                        }
                    //normal case
                    }else{
                        var name="<a href='"+feature.link+"'><img src='"+feature.thumbnail_url_path+"'  width='200'>"+ feature.name+" "+feature.time+"</a>";
                        var marker=L.marker(latlng,{icon: icon_objs["red"]}).bindPopup(name)
                    }
                    return marker
                // global photos
                }else if (feature.type==="Feature" & feature.point_type==="global_photo"){
                    var name="<a href='"+feature.link+"'><img src='"+feature.thumbnail_url_path+"'  width='200'>"+ feature.name+" "+feature.time+"</a>";
                    var marker=L.marker(latlng,{icon: icon_objs["yellow"]}).bindPopup(name)
                    return marker
                // track as a single point
                }
                // track as point
                else if (feature.type==="Feature" & feature.point_type==="track"){
                    var name="<a href='"+feature.link+"'><b>"+feature.name+"</b></a>";
                    //console.log(geojsonMarkerOptions,feature.color)
                    if (geojsonMarkerOptions!=null & feature.color!=null ){
                        geojsonMarkerOptions.color=feature.color
                        var marker =L.circleMarker(latlng, geojsonMarkerOptions).
                            bindPopup(name).
                            on('click', function(e){ 
                                console.log("--------------click on track as point -------------",e)
                                this.bringToFront();
                                //mark the corresponding row in the table, if a table is given
                                if (table) {
                                    //find row_index
                                    //and check if row was already selected
                                    table.rows().every(function ( rowIdx, tableLoop, rowLoop ){
                                        var data = this.data();
                                        if (e.target.feature.pk == data.pk){
                                            row_index = rowIdx
                                            //TODO: check if row is already selected, this does not work
                                            //console.log( table.rows({ selected: true }))
                                            selected_rows = table.rows({ selected: true })[0]
                                            //console.log(selected_rows, "selected_row", table.rows({ selected: true }))
                                            was_already_selected = selected_rows.includes(row_index)
                                            //console.log("row_index", row_index, "pk", data.pk)
                                        }
                                    })

                                    //console.log("was_already_selected",was_already_selected)

                                    // if i ctrl-click, dont reset selected rows
                                    if (e.originalEvent.ctrlKey){
                                        //if it was already selected, deselect
                                        if (was_already_selected){
                                            table.row(row_index).deselect()
                                        //if it was not selected, select
                                        }else{
                                            table.row(row_index).select()
                                        }
                                    //if not ctlr-click, deselect_all
                                    }else{
                                        console.log("deselecting all rows")
                                        table.rows().deselect();
                                        // then select row
                                        table.row(row_index).select()
                                    }
                                }
                            })
                            
                        marker.setStyle({'className': 'leaflet_track_marker leaflet_track_'+feature.pk}) //I assign a class to find these markers
                        marker.id=feature.number    //I assign an id to marker but it is not a global id
                        //console.log(marker.id)
                    }else{
                        var marker=L.marker(latlng).bindPopup(name)
                    }
                    return marker
                // group as a single point
                }else if (feature.type==="Feature" & feature.point_type==="group"){
                //console.log("a", feature)
                    var name="<a href='"+feature.link+"'><b>"+feature.name+"</b></a>"+ "<br>"+feature.size+" tracks";
                    geojsonMarkerOptions.color=feature.color
                    var marker =L.circleMarker(latlng, geojsonMarkerOptions).bindPopup(name)
                    return marker
                }
                }
            }
        )
    }catch(error){
        console.log("Cannot track_layer_fromjson", error)
        gj= L.geoJson()
    }
    var t1 = performance.now();
    console.log("----track_layer_fromjson took", (t1-t0)/1000, "seconds")
    return gj;
}

function read_data_leaflet_generic(data,geojsonMarkerOptions,map,options={})  {

    //  console.log("read_data_leaflet_generic")
    var t0 = performance.now();

    //tracks={}      //global_tracks now a global variable
    track_group={} //for single track
    features={}  // wps, photos, lines, (groups?)
    global_features={}  //global wps, photos, lines
    groups={} // groups
    geojson={} //all geojson
    var groupCheckboxes=false
    colors_tracks=null
    plot_track=true
    show_features=true
    legend_names=[] // color legends
    splits={}
    splits_name=""
    use_points=false


    for (element in data){
        console.log("Element", element)
        switch(element) {
            case "features":
//                has_alts=data[element]["has_alts"]
//                has_freq=data[element]["has_freq"]
//                has_hr=data[element]["has_hr"]
//                has_times=data[element]["has_times"]
                if ("plot_track" in data[element]) plot_track=data[element]["plot_track"]
                if ("show_features" in data[element]) show_features=data[element]["show_features"]
                if ("use_points" in data[element]) use_points=data[element]["use_points"]

                break;
            case "legend":
                try{
                    legend_data=data[element]
                    legends={}

                    for (legend_name in legend_data){
                        if (!legend_data[legend_name]["hide_in_map"]){
                            legend_names.push(legend_name)
                        }
                        div_id=legend_name+"_id"
                        //console.log("creating legend" , div_id)

                            legend_fct(map,legend_data[legend_name]["legend"], legend_data[legend_name]["grades"], div_id, legend_data[legend_name]["title"],decimals=legend_data[legend_name]["decimals"])
                            hide(div_id) //hide legend by default
                    }

                    map.on('overlayadd', onOverlayAdd);
                    function onOverlayAdd(e){
                        found=false
                        for (legend_name in legend_data){
                            if (e.name=="Color by "+legend_name) {
                                found=true
                                show(legend_name+"_id");
                                for (legend_name_2 in legend_data){
                                    if (legend_name_2!=legend_name){
                                        hide(legend_name_2+"_id");
                                    }
                                }
                            }
                        }
                        if (!found){
                            for (legend_name_2 in legend_data){
                                hide(legend_name_2+"_id");
                            }
                        }
                    }
                }catch(error){
                        console.log("Cannot add legend", error)
                }

                break;
            case "colors":
                colors_tracks=data[element]
                break;
            case "Track":
                if (plot_track){
                    data_track=data[element]["points"]
                    data_length=data_track.length
                    //add number of points
                    try{document.getElementById('n_points').innerHTML += "(showing " + parseInt(data_length)+")";}
                    catch(error){console.log("no div n_points, skipping")}
                    if(use_points){
                        track_group["Track"]=track_layer_fromjson(data_track,geojsonMarkerOptions,options).addTo(map)
                    }else{
                        track_group["Track"]=track_layer_fromjson(data[element]["details"],geojsonMarkerOptions,options).addTo(map)
                    }
                    for (i in legend_names){
                        legend_name=legend_names[i]
                        console.log("legend_name", legend_name)
                        options["color_feature"]="Color"+legend_name
                        track_group["Color by "+legend_name]=track_layer_fromjson(data_track,geojsonMarkerOptions,options)
                    }
                }
                break;
            case "Tracks":
                data_tracks=data[element]
              //  console.log("data_tracks",data_tracks)
                // tracks can be a list, or a dict track_name:properties, I treat both cases
                if (Array.isArray(data_tracks)){ n_tracks=data_tracks.length}
                else{n_tracks=Object.keys(data_tracks).length }
                //console.log(n_tracks)
                if (Array.isArray(data_tracks)){ //list of tracks --> transform to dict
                    tracks_dict={}
                    for (i in data_tracks){
                        data_track=data_tracks[i]
                        track_name=data_track["name"]
                        tracks_dict[track_name]=data_track
                    }
                }else{ //dict of tracks --> keep the dict
                    tracks_dict=data_tracks
                }
                // now loop over dict
                for (track_name in tracks_dict){
                    //keep track of plotted tracks to avoid double plotting (from emptymap)
                    if (window.plotted_tracks != undefined){
                        if (window.plotted_tracks.includes(track_name)){
                            continue
                        }else{
                            window.plotted_tracks.push(track_name)
                        }
                    }
                    data_track= tracks_dict[track_name]
                    //keep track of plotted tracks to avoid double plotting (from emptymap)
                    if (window.plotted_tracks_ids != undefined){
                        window.plotted_tracks_ids.push(data_track["pk"])
                    }
                    if (colors_tracks != null) {
                        color=colors_tracks[track_name]
                    }else if ("color" in data_track) {
                        color=data_track["color"]
                    }else{
                        color="black"
                    }
                    text="<font color='"+color+"'>"+track_name+"</font>"
                    options["color_feature"]="color"
                    options["track_name"]=track_name
                    //console.log("data_track", data_track)
                    global_tracks[text]=track_layer_fromjson(data_track,geojsonMarkerOptions,options).addTo(map)
                }
                groupCheckboxes = true
                break;
            case "Groups":
                data_groups=data[element]
                for (group_name in data_groups){
                    color=data[element][group_name]["color"]
                    if(!color)color="black"
                    text="<font color='"+color+"'>"+group_name+"</font>"
                    groups[text]=track_layer_fromjson(data[element][group_name],geojsonMarkerOptions,options).addTo(map)
                    //TODO: add color in text
                    //todo: limit to a certain number of tracks?
                }
                groupCheckboxes = true
                break;
            case "Waypoints":
            case "Photos":
            case "Lines":
                if (show_features){
                    try{
                        if (data[element].length>0){
                            features[element]=track_layer_fromjson(data[element],geojsonMarkerOptions,options)
                            features[element].addTo(map)
                        }
                    }catch(error){
                        console.log("Cannot do "+ element +": "+error)
                        console.log("data[element]", data[element])
                    }
                }
                break;
            case "Global Lines":
            case "Global Waypoints":
            case "Global Photos":
                if (data[element].length>0){
                    global_features[element]=track_layer_fromjson(data[element],geojsonMarkerOptions,options).addTo(map)
                }
                break;
            case "GeoJSON":
                groupCheckboxes=true
            case "Global GeoJSON":
                var element_length=data[element].length
                if (element_length){
                    // here I make a menu entry for each geojson object
                    // different from wps and photos, which get a single menu for all elements
                    for (i=0; i<element_length;i++ ){
                        single_element_data=data[element][i]
                        options["feature_for_name"]=single_element_data.feature_for_name
                        //set color
                        if (single_element_data["properties"] && single_element_data["properties"]["color"]){
                            color=single_element_data["properties"]["color"]
                        }else{
                            color="black"
                        }
                        name=single_element_data["external_geojson_name"]
                        text="<font color='"+color+"'>"+name+"</font>"
                        geojson[text]=track_layer_fromjson(single_element_data,geojsonMarkerOptions,options)
                        if (element=="GeoJSON"){
                            geojson[text].addTo(map)
                        }
                    }
                }
                break;
            case "minmaxlatlong": //used to give map bounds
                if (!options["nominmaxlatlong"]){
                    latslong = data[element]
                    // console.log(latslong)
                     min_lat=latslong[0];max_lat=latslong[1];min_long=latslong[2];max_long=latslong[3];
                     var mapBounds = L.latLngBounds([[min_lat, min_long],[max_lat,max_long]]);
                     if (min_lat>=-90 && min_lat<=90 && max_lat>=-90 && max_lat<=90 &&
                         min_long>=-180 && min_long<=180 && max_long>=-180 && max_long <=180){
                         try{
                             map.fitBounds(mapBounds);
                         }catch(error){
                             console.log(error)
                         }
                     }
                }
                break;
            case "Laps":
            case "Splits":
            case "Segments":
            case "Subtracks":
                data_splits=data[element]
                for (split in data_splits){
                    data_split=data_splits[split]
                    color=data_split["color"]
                    name=data_split["name"]
                    text="<font color='"+color+"'>"+name+"</font>"
                    if (options["use_points"]){
                        console.log("POINTS")
                        //points
                        options["color_feature"]="Color"+element.slice(0, -1)
                        splits[text]=track_layer_fromjson(data_split["points"],geojsonMarkerOptions,options).addTo(map)
                    }else{
                        //lines
                        console.log("LINES")
                        options["color_feature"]="color"
                        splits[text]=track_layer_fromjson(data_split["details"],geojsonMarkerOptions,options).addTo(map)
                        splits_name=element
                    }
                }
                groupCheckboxes= true
                break;
        }
    }

    var groupedOverlays = {}
    var exclusiveGroups= []

    if (track_group!={}){
        groupedOverlays["Track"]=track_group
        exclusiveGroups= ["Track"]
    }
    if (global_tracks!={}){
        groupedOverlays["Tracks"]=global_tracks
    }
    if (groups!={}){
        groupedOverlays["Groups"]=groups
    }
    if (splits!={}){
        groupedOverlays[splits_name]=splits
    }
    if (features!={}){
        groupedOverlays["Features"]=features
    }
    if (global_features!={}){
        groupedOverlays["Global Features"]=global_features
    }
    if (geojson!={}){
        groupedOverlays["Geojson"]=geojson
    }
    

    if (!options["nogroupedlayers"]){
        var options2 = {
            exclusiveGroups: exclusiveGroups,
            groupCheckboxes: groupCheckboxes
          };
      
          var layerControl = L.control.groupedLayers(baseMaps, groupedOverlays, options2);
          map.addControl(layerControl);
      
          // groups are btw all shown by default, but the checkbox remains unselected,
          // so i select it by hand
          if (groupCheckboxes){
              $(".leaflet-control-layers-group-selector").prop("checked",true)
          }
        //put the first map as selected, otherwise the radio button is empty for all
        $("input:radio[name=leaflet-base-layers]:first").prop('checked', true);

    }

    var t1 = performance.now();
    console.log("--read_data_leaflet_generic took", (t1-t0)/1000, "seconds")

}

function track_popup(feature, properties){
    // used in scatter plot for groups
    name=""
    color="black"
    if(feature.png_file)
    name+='<div align="center"><img src="'+feature.png_file+'" style="max-height:100px;max-width:150px;height:auto;width:auto;"><br></div>'

    if(feature.name && feature.color)
    name+="<b><font color="+feature.color+">"+ feature.name+"</font></b><br>"


    for (var p in properties){
        //console.log(p, properties[p]["feature_name"],properties[p]["feature_color"])
        p_title=p
        property_name=properties[p]["feature_name"]
        property_rank=properties[p]["feature_rank"]
        property_formatted=properties[p]["feature_formatted"]
        color=properties[p]["feature_color"]
        decimals=properties[p]["decimals"]
        unit=properties[p]["unit"]

        if (feature[property_name] != undefined | property_formatted!= undefined) {
            if (feature[color]!= undefined){
                color=feature[color]
            }else{
                color="black"
            }
            if (feature[property_formatted]!= undefined){
                value=feature[property_formatted]
            }else if (decimals !=null & feature[property_name]!= null)
            {
                value=feature[property_name].toFixed(decimals)
            }else if (feature[property_name]){
                value=feature[property_name]
            }
            else{
                continue
            }
            if (unit!=undefined){
                value=value+unit
            }

            if (feature[property_rank]!= undefined){
                value=value+" ("+feature[property_rank]+")"
            }

            name+=p_title+": <font color="+color+">"+ value + "</font><br>"
        }
    }
    return name
    }

function legend_fct(map,colors,grades, id, name="Legend", decimals=1, father_id="map_block", ) {
//        console.log("colors",colors)
//        console.log("grades",grades)
//        console.log("id",id)
//        console.log("name",name)
//        console.log("decimals",decimals)
   var div = document.createElement('div');
   div.setAttribute("id", id);
   div.innerHTML +="<div><div style='float:right'><b>"+name+"</b></div>"
   div.innerHTML +="<div style = 'clear:both;'></div><div style='float:right'>"
   if (grades){
       for (var i = 0; i < grades.length; i++) {
            if(i<100 | i>grades.length-101){ //avoid legends if too large!
                if (decimals>-1){
                div.innerHTML +=
                    '<div style="float:right;width:50px;background:' + colors[grades.length-i-1] + '">' + grades[grades.length-i-1].toFixed(decimals)+' </div>';
                    }else{
                div.innerHTML +=
                    '<div style="float:right;width:50px;background:' + colors[grades.length-i-1] + '">' + grades[grades.length-i-1]+' </div>';
                    }
            }
        }
        div.innerHTML +="</div></div>"
        }
   try{
    document.getElementById(father_id).appendChild(div);
    }catch(error){
        console.log("Cannot append legend")}
   //console.log(div);
    return div;
    };

function add_photos_ajax(data_tot,links=false,request=""){
    // for showing list of photos
    var base_div_text='<div style="width:19%;float:left; margin-left: 1%;margin-top: 1%">'
    // for slideshow
    var base_div_text_ss='<div class="mySlides" style="max-height:100%;width:auto; text-align: center;">'
    // for thumbnails of slideshow
    var base_div_text_tn='<div class="column_slideshow">'
    var total_photos = data_tot["Photos"].length
    function img_text(thumbnail_url,url_path){
        return '<img \
        onmouseover="this.src='+"'"+url_path+"'"+'" \
        onmouseout="this.src='+"'"+thumbnail_url+"'"+'" \
        class="img_photo" src="'+thumbnail_url+'" alt="img" width="100%">'
    }    
    function img_text_ss(url_path,n){
        return '<div class="numbertext"><span>'+n+ '</span> / <span class="total_photos_slideshow"></span></div>'+
         '<img src='+url_path+' style=" display: inline-block;height:100%;width:auto;max-width:100%" >'
    }
    function img_text_tn(thumbnail_url,n){
        return '<img class="demo cursor" src='+thumbnail_url+ ' style="width:100%" onclick="currentSlide('+n+')">'
    }    
    function a_text(link){
        return '<a href="'+link+'?'+request+'">'
    }

    var counter = 1
    if (total_photos>0){
        for (p in data_tot["Photos"]){
            photo=data_tot["Photos"][p]
            var text=""
            var text_ss = ""
            var text_tn = ""
            var text_a= ""
            var text_ss_a= ""
            if (Array.isArray(photo.thumbnail_url_path)){ //case of clustering
                for (i in  photo.thumbnail_url_path){
                    text+=base_div_text
                    text_a=img_text(photo.thumbnail_url_path[i],photo.url_path[i]);
                    text_ss+=base_div_text_ss
                    text_tn+=base_div_text_tn
                    text_tn+=img_text_tn(photo.thumbnail_url_path[i],counter)
                    var text_ss_a=img_text_ss(photo.url_path[i],counter);
                    if (links){
                        text_a=a_text(photo.link[i])+text_a+"</a>";
                        text_ss_a=a_text(photo.link[i])+text_ss_a+"</a>";
                    }
                    text+=text_a+"</div>"
                    text_ss+=text_ss_a+"</div>"
                    text_tn+="</div>"
                    counter++;
                }
            }else{  //normal case
                text+=base_div_text
                text_a=img_text(photo.thumbnail_url_path, photo.url_path)
                text_ss+=base_div_text_ss
                text_ss_a=img_text_ss(photo.url_path, counter)
                text_tn+=base_div_text_tn
                text_tn+=img_text_tn(photo.thumbnail_url_path,counter)                
                if(links){
                    text_a=a_text(photo.link)+text_a+"</a>";
                    text_ss_a=a_text(photo.link)+text_ss_a+"</a>";
                }
                text+=text_a+"</div>"
                text_ss+=text_ss_a+"</div>"                
                text_tn+="</div>"
                counter++;
            }
            $( "#photos_div" ).append(text)
            $( "#slideshow_container .photo_container" ).append(text_ss)
            $( "#slideshow_container .thumbnail_container .row_slideshow" ).append(text_tn)
        }
        $(".total_photos_slideshow").html(counter-1)
        showSlides(1);
    }else{
        $( "#photos_div" ).append("<p><b>No Photos available</b></p>")
    }
}

//removes all pltted tracks on the map
function clear_tracks(map){
    window.plotted_tracks=[]
    window.plotted_tracks_ids=[]
    window.selected_tracks = []
    $.each(window.global_tracks,function(name,layer){
        map.removeLayer(layer)
    })
    refresh_plotted_tracks_number()
}

// search all tracks according to map bounds and further params
// used for live serach on emptymap
function refresh_tracks(map, base_url, search_params){

    var bounds = [map.getBounds().getSouthWest(),
                    map.getBounds().getNorthEast(),]

    var query_string=
        "min_lat="+bounds[0]["lat"]+
        "&max_lat="+bounds[1]["lat"]+
        "&min_lng="+bounds[0]["lng"]+
        "&max_lng="+bounds[1]["lng"]+
        //"&how_many=10"+
        "&use_color=1"

    if (window.plotted_tracks_ids.length>0){
        query_string+="&exclude_tracks_ids="+window.plotted_tracks_ids.join(",")
    }

    if (search_params){
        $.each(search_params,function(name,value){
            query_string+="&"+name+"="+value
        })
    }

    var url=base_url+"?"+query_string
    console.log(url)

    if ($("#auto_clear_tracks").is(':checked')){
        clear_tracks(map)
    }

    $.getJSON(url,function(data){
        options={
            "nogroupedlayers":1,
            "nominmaxlatlong":1,
        }
        geojsonMarkerOptions=[]
        read_data_leaflet_generic(data,geojsonMarkerOptions,map,options)
        refresh_plotted_tracks_number()
    })
}

function refresh_plotted_tracks_number(){
    $("#n_tracks").text(window.plotted_tracks_ids.length +" tracks")
}
