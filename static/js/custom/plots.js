function highlight_c3_points (i){
    console.log("highlight_c3_points",i)
    //get all points and reset them
    name0="c3-shape"
    a=document.getElementsByClassName(name0)
    //using a single point as master
    if (a.length>1){
        if(i!=0) {example_j=0}
        else {example_j=1}
        r0=d3.select(a[example_j]).attr("r")
        console.log("r0",r0)
        for (j = 0; j < a.length; j++){
            d3.select(a[j]).attr("r", r0)
        }
    }
    //get points with the given number and highlight them
    name="c3-shape-"+parseInt(i)
    a=document.getElementsByClassName(name)
    for (j = 0; j < a.length; j++) {
          d3.select(a[j]).attr("r", 10) //.style("fill", "red");
    }
}


function highlight_leaflet_points (i=null,class_name="leaflet_track_point", track_pks=[]){
    //highlight points on the map according to class  provided
    try{
        console.log("highlight_leaflet_points, i",i, "track_pks",track_pks)

        // I assign this class name below only to points in the track
        if (i!= null){
            //if I want to highlight the i-th point with class class_name (for list of points in a track)
            //here I deselect all other points
            reset_point_sizes(class_name)
            a=document.getElementsByClassName(class_name)
            console.log("highlight i-th point",i)
            highlight_properties=default_point_properties(type="point",reset="highlight")    
            a[i].setAttribute("fill-opacity",highlight_properties["fill-opacity"])
            a[i].setAttribute("stroke-width",highlight_properties["stroke-width"])
        }else if (track_pks){
            // if I want the only point with class leaflet_track_+track_pk (for list of tracks)
            // it van be a point of 
            reset_point_sizes(class_name)
        
            for (j=0; j<track_pks.length; j++){
                track_pk = track_pks[j]
                class_name_track="leaflet_track_"+parseInt(track_pk)
                console.log("highlight",class_name_track)
                bs=document.getElementsByClassName(class_name_track)
                //there are more than one when track as list of points, otherwise just one line
                for (var i=0;i<bs.length;i++){
                    var b=bs[i]
                    type="point"
                    if (b && b.classList && b.classList.contains("leaflet_trackline_marker")){
                        type="path"
                        //TODO: bring to front when line
                    }
                    if (b && b.classList && b.classList.contains("leaflet_track_point_many_tracks")){
                        highlight_properties=default_point_properties(type=type,reset="highlight_small")   
                    }else{
                        highlight_properties=default_point_properties(type=type,reset="highlight")   
                    }
                    try{
                        b.setAttribute("fill-opacity",highlight_properties["fill-opacity"])
                        b.setAttribute("stroke-width",highlight_properties["stroke-width"])
                        b.setAttribute("weight",highlight_properties["weight"])
                    }catch(error){
                        console.log("cannot set attributs for ", b)
                    }
                }
            }
        }
    }catch(error){
        console.log(error)
    }
}

function c3data (names,x_data,y_data){
    xs0=Object()
    columns=[]

    for (var i = 0; i < names.length; i++) {
        xs0[names[i]]="x"+names[i]
        x_data[i].unshift("x"+names[i])
        y_data[i].unshift(names[i])
        columns.push(x_data[i])
        columns.push(y_data[i])
    }
    return xs0,columns;
}

function c3plot (xs0,columns,colors_,x_label,y_label,bind_to,type="line",
                 mean_line=true,show_points=false,show_y2=false,axes={},y2_label="",show_legend=true,debug=false){
    //c3RectZoom.patchC3(c3) non funziona
    if(mean_line){
        means=[];
        for (i=1; i<columns.length;i+=2){
            c=columns[i].slice(1) //tolgo la stringa iniziale
            try{
            var mean=c.reduce(function(a, b) { return a + b; })/c.length;
            }
            catch(err){
            var mean=0;
            }
            means.push(mean);
        }
        if (means.length>1){
            var mean=means.reduce(function(a, b) { return a + b; })/means.length;
        }
    }
    else{
        mean=-100
    }
    if(debug){
        console.log("columns",columns)
        console.log("xs0",xs0)
        console.log("colors",colors_)
        console.log("x_label",x_label)
        console.log("y_label",y_label)
    }

    var chart = c3.generate({
        bindto: bind_to,
        zoom: {
            enabled: true
        },
        c3RectZoom: {
            enabled: true,
            // ...c3RectZoom.Settings
        },
        c3RectZoom: {
            enabled: true,
            // ...c3RectZoom.Settings
        },
        data: {
            xs: xs0,
            columns:columns,
            type: type,
            colors: colors_,
        //    function (color, d) {
        //        if (colors_.length>0){
        //            return colors_[d.index];
        //        }else{
        //            return undefined
        //        }
       //     },
        //colors_,
            axes: axes,
            //onclick: function (d, i) { console.log("onclick", d, i); },
            onclick: function (d, i) {
                console.log("-----------click on c3 point ------------")
                highlight_leaflet_points(d.index);
                highlight_c3_points(d.index) 
            },
            //onmouseover: function (d, i) { console.log("onmouseover", d, i); },
            //onmouseout: function (d, i) { console.log("onmouseout", d, i); }
        },
        axis: {
            y2: {
                show: show_y2,
                label: y2_label,
            },
            x: {
                label: x_label,
                tick: {
                    count: 5,
                    format: d3.format('.2f'),
                 //   culling: {
                 //       max: 4 // the number of tick texts will be adjusted to less than this value
                 //   }
                }
                //type: 'timeseries',
                // tick: {
                //     format: '%H-%M-%S'
                // }
                },
            y: {
                label: y_label,
            }
            },
        point: {
            show: show_points
        },
        grid: {
            // x: {
            //     lines: [{value: 2}, {value: 4, class: 'grid4', text: 'LABEL 4'}]
            // },
            y: {
                lines: [{value: mean,text:mean.toFixed(1)}
                    // , {value: 800, class: 'grid800', text: 'LABEL 800'}
                ]
            }
        },
        bar: {
            width: {
                //ratio: 0.1 // this makes bar width 50% of length between ticks
                width:10
            }
            // or
            //width: 100 // this makes bar width 100px
        },
        legend: {
            show: show_legend
        }
        // tooltip: {
        //     grouped: false // Default true
        // }
        }
    );



    return chart
}


function c3plotjsondata (data,x,y,options={}){
    //parameters
    var t0 = performance.now();

    if (debug) console.log("options",options)
    var colors_ = options.colors_;
    var x_label = options.x_label;
    var y_label = options.y_label;
    var bind_to = options.bind_to;
    var type = options.type||"line";
    var mean_line = options.mean_line=== true; //default false
    var show_points = options.show_points===true; //default false
    var show_y2 = options.show_y2===true;
    var axes = options.axes||{};
    var y2_label = options.y2_label||"";
    var show_legend = options.show_legend!==false;//default true
    var height = options.height||200;
    var width = options.width||550;
    var pointcolor = options.pointcolor===true;//default false
    var radius = options.radius||3;
    var popup_fct = options.popup_fct||point_popup;
    var on_click = options.on_click||"find_c3_leaflet";
    var x_type = options.x_type||"number";
    var y_type = options.y_type||"number";
    var debug = options.debug===true;
    var highlight = options.highlight||undefined;
    var popup_fct_options = options.popup_fct_options;
    var filter_and_sort = options.filter_and_sort===true;//default false
    var adjust_x = options.adjust_x===true;//default false
    var adjust_y = options.adjust_y===true;//default false
    var adjust_t = options.adjust_t===true;//default false
    var grid_x = options.grid_x===true;//default false
    var grid_y = options.grid_y===true;//default false
    var zoom_rescale = options.zoom_rescale===true;//default false
    var invert_axis = options.invert_axis===true;//default false
    // here trick does not work bcz it can be zero
    if (options.x_decimals!=undefined){
        x_decimals=options.x_decimals
    }else{
        x_decimals=2
    }

    if( options.x_tick_count=="auto"){
        var x_tick_count=undefined 
    }else{
        var x_tick_count = options.x_tick_count || 5
    }

    y_tick_count=undefined

    if (debug) console.log("data c3plotjsondata ", data)
    if (debug) console.log("options c3plotjsondata ", options)
    if (debug) console.log("x ", x)
    if (debug) console.log("y ", y)

    //needed because othewise c3 screws up the order of points
    if (filter_and_sort){
        if (typeof y === 'string' || y instanceof String){
            data=data.filter(a => a[x]!=null).filter(a => a[y]!=null).sort((a, b) => (a[x] > b[x]) ? 1 : (a[x] === b[x]) ? ((a[y] >= b[y]) ? 1 : -1) : -1 )  // must order because c3 orders by x, otherwise cannot use index
        }else{
            if  (x=="Heartrate Group"){
                x_order="Heartrate"
            }else if  (x=="total_heartrate_group"){
                x_order="total_heartrate"
            }else{
                x_order=x
            }
            data=data.filter(a => a[x_order]!=null).sort((a, b) => (a[x_order] > b[x_order]) ? 1 : -1 )
        }
    }
//    console.log("data filtered without null and sorted by "+x,data)

    x_format_parse=undefined
    x_padding={}
    x_min=undefined
    x_format=undefined

    //console.log("x_type",x_type,x_type=="time_min")

    if (x_label==="Pace") {
        add_km=true
    }else{
        add_km=false
    }

   // x axis parameters
    if(x_type==="ts"){
        x_type="timeseries"
        x_format='%Y-%m-%d'
        if (x_label===undefined) x_label="Date"
    }else if(x_type==="time" ){
        x_format_parse="%H:%M:%S"
        x_format='%H:%M'
        if (x_label===undefined) x_label="Time (hours)"
        x_type="timeseries"
        if (adjust_t){
            data.sort(function(a, b){
                return a[x] > b[x];
            });
            max_time=data[data.length-1][x]
            if (debug) console.log("max_time",max_time)
            if (max_time.substring(0,2)==="00"| max_time.substring(0,2)==="0:"){  //if the largest time has 0 hours
                x_format='%M:%S'
                if (x_label===undefined) x_label="Time (minutes)"
            }
        }
    }else if (x_type=="time_min"){
        //minutes for duration and pace converted to time
        //for some reason the timeseries type does not work well, so keep a normal axis ("indexed")
        max_x=Math.max.apply(Math, data.filter(a => a[x]!=null).map(function(o) { return o[x]; }))
        x_format_label=format_m(max_x,add_km)
        x_format=x_format_label["format"]
            if (x_label===undefined) x_label="Time (minutes)"
        x_label+=x_format_label["label"]
        x_type="indexed"
    }else if (x_type==="category"){
        x_type="category"
        x_tick_count=undefined
    }else{
        x_type="indexed"
        x_format=d3.format('.'+x_decimals+'f')
        if (adjust_x){
            min_x=Math.min.apply(Math, data.filter(a => a[x]!=null & a[x]!=0).map(function(o) { return o[x]; }))
            max_x=Math.max.apply(Math, data.filter(a => a[x]!=null & a[x]!=0).map(function(o) { return o[x]; }))
            if (debug) console.log("min_x","max_x",min_x,max_x)
            if(min_x/max_x<0.3){
                x_min=0
                x_padding={left:0}
            }
        }
    }

    // y axis parameters
    if (y_label==="Pace") {
        add_km=true
    }else{
        add_km=false
    }

    //"ts does not work well on y axis, avoid using this"
    if(y_type==="ts"){
        max_y=Math.max.apply(Math, data.filter(a => a[y]!=null).map(function(o) { return o[y]; }))
        y_type="timeseries"
        y_format_label=format_m(max_y,add_km)
        y_format=y_format_label["format"]
        if (y_label===undefined) y_label="Date"
        y_label+=y_format_label["label"]    
    }else if(y_type==="time"){
        y_format_label=format_m(max_y,add_km)
        y_format=y_format_label["format"]
        if (y_label===undefined) y_label="Time (hours)"
        y_label+=y_format_label["label"]
    }else if (y_type=="time_min"){
        //minutes for duration and pace converted to time
        // this works, just pass number of minutes
        max_y=Math.max.apply(Math, data.filter(a => a[y]!=null).map(function(o) { return o[y]; }))
        y_format_label=format_m(max_y,add_km)
        y_format=y_format_label["format"]
        if (y_label===undefined) y_label="Time (minutes)"
        y_label+=y_format_label["label"]
        y_type="timeseries"
    }else if (y_type==="category"){
        y_type="category"
        y_tick_count=undefined
    }else{
        y_type="indexed"
        //y_format=d3.format('.2f')
        y_format=undefined
    }

    if (adjust_t & (y_type=="timeseries")){
        data.sort(function(a, b){
            return a[y] > b[y];
        });
        max_time=data[data.length-1][y]
        if (debug) console.log("max_time",max_time)
        if (max_time.substring(0,2)==="00"| max_time.substring(0,2)==="0:"){  //if the largest time has 0 hours
            y_format=d3.timeFormat('%M:%S',)
            if (y_label===undefined) y_label="Time (minutes)"
        }
    }



    y_min=undefined
    y_padding={}
    if (adjust_y &  y_type=="indexed" ){
        min_y=Math.min.apply(Math, data.filter(a => a[y]!=null).map(function(o) { return o[y]; }))
        max_y=Math.max.apply(Math, data.filter(a => a[y]!=null).map(function(o) { return o[y]; }))
        if (debug) console.log("min_y, max_y", min_y,max_y)
        if(min_y/max_y<0.3){
            y_min=Math.min(0, min_y)
            y_padding={bottom:0}
       }
    }


    if (on_click==="find_c3_leaflet"){
        function onclick_fct(d,i) {
            console.log("-----------click on c3 point ------------")
            highlight_leaflet_points(d.index);
            highlight_c3_points(d.index)
        };
    }else if (on_click==="link"){
        function onclick_fct(d,i) {
            console.log("-----------click on c3 point ------------")
            window.open(data[d.index]["link"])
        }
    }
    if(pointcolor){
        color={}
        colors=data.map(a=>a[colors_]) //in this case colors is the name of the feature to take as colors
        datacolor=function (color, d) {
                return colors[d.index]
                }
    }else{
        color={
                    pattern: colors_
            }
        datacolor={}
    }

    // specify radius as a number or as a point-dependent quantity
     if (highlight==="Last"){
        radius_ok = function(d) {
            last_date=Math.max.apply(Math, data.map(function(o) { return o["time_number"]; }))
            if (data[d.index]["time_number"]===last_date){
                return 25
            }else{
                return 10
            }
        }
    }else if (highlight!=undefined && highlight!="None"){
        radius_ok = function(d) {
            if (data[d.index]["name"]===highlight){
                return 25
            }else{
                return 10
                }
            }
    }
    else if (highlight===undefined || highlight==="None"){
        //console.log(radius)
        if (!isNaN(radius)){  //if a number
            radius_ok=radius
        }else{
            radius_ok = function(d) { //if a string
               return data[d.index][radius]
            }
        }
    }else{
        radius_ok=10
    }

    //console.log("data_x_y",data.map(a=>[a[x],a[y]]))
    if(debug){
        console.log("data_x_y",data.map(a=>[a[x],a[y]]))
        console.log(url)
        console.log("colors",colors_)
        console.log("x_label",x_label)
        console.log("y_label",y_label)
    }

    conf={
        bindto: bind_to,
        size: {
            height: height,
            width: width
        },
        zoom: {
            enabled: true,
            rescale: zoom_rescale,
        },
        c3RectZoom: {
            enabled: true,
            // ...c3RectZoom.Settings
        },
        data: {
            json: data,
            mimeType: 'json',
            keys: {
                value:y,
                x:    x,
                },
            type: type,
            color:datacolor,
            xFormat:x_format_parse,
            //yFormat:y_format_parse, does not exist!
        //colors_,
            axes: axes,
            selection: {
                enabled: true
            },
            //onclick: function (d, i) { console.log("onclick", d, i); },
            onclick: function (d, i) {onclick_fct(d,i)},
      //      onmouseover: function (d, i) { console.log("onmouseover", d, i); },
      //      onmouseout: function (d, i) { console.log("onmouseout", d, i); }
        },
        tooltip: {
             contents: function (d, defaultTitleFormat, defaultValueFormat, color) {
                return "<div  style='background-color: rgba(169, 169, 169, .7)'>"+popup_fct(data[d[0].index], popup_fct_options)+"</div>"
            },
        },
        color: color,
        axis: {
            rotated:invert_axis,
            y2: {
                show: show_y2,
                label: y2_label,
            },
            x: {
 //               inverted:true,
                label: x_label,
                type: x_type,
                min: x_min,
                padding: x_padding,
                 tick: {
                     count: x_tick_count,
                     format: x_format,
//                     culling: {
//                        max: 10 // the number of tick texts will be adjusted to less than this value
//                    }
                 },
                },
            y: {
//                inverted:true,
                label: y_label,
                type: y_type,
                min:y_min,
                padding: y_padding,
                tick: {
                    count: y_tick_count,
                    format: y_format,
                },
           }
            },
        point: {
            show: show_points,
            r:radius_ok,
        },
        grid: {
             x: {
                show: grid_x
            //     lines: [{value: 2}, {value: 4, class: 'grid4', text: 'LABEL 4'}]
             },
            y: {
                show: grid_y
                //lines: [{value: mean,text:mean.toFixed(1)}
                    // , {value: 800, class: 'grid800', text: 'LABEL 800'}
              //  ]
            }
        },
        bar: {
            width: {
                //ratio: 0.1 // this makes bar width 50% of length between ticks
                width:10
            }
            // or
            //width: 100 // this makes bar width 100px
        },
        legend: {
            show: show_legend
        }
        // tooltip: {
        //     grouped: false // Default true
        // }
        }

    //console.log(conf)
    try{
        var chart = c3.generate(conf);
    }catch(error){
        console.log("error in c3.generate", error)
    }


    var t1 = performance.now();
    console.log("-----c3plotjsondata call took " + (t1 - t0) + " milliseconds, x: "+x+", y: "+y)

    return chart
}

// add the field  track_name with value given by y, to show the track name in the legend
function convert_data_many_tracks(data,y="Speed"){
    //data_ok=data.filter(a => a.point_type==="track")
    data_out=data.map(function(a){
            a[a["track_name"]]=a[y]
            return a
            })
    return data_out
}


function convert_data_c3(data,y="Speed", feature="Split", feature_name="Split"){
    console.log(data)
    data_ok=data.filter(a => a[feature])
    data_out=data_ok.map(function(a){
        split_name=a[feature+"Name"]
        a[split_name]=a[y]
            return a
            })
    return data_out
}

function hide_absent_data(data,document){
    has_times=data["features"]["has_times"]
    has_alts=data["features"]["has_alts"]
    has_freq=data["features"]["has_freq"]
    has_hr=data["features"]["has_hr"]
    if (!has_times){
        //speed
        document.getElementById('c3_11').style.display = 'none';
        document.getElementById('c3_21').style.display = 'none';
        // all with times on x axis
        document.getElementById('c3_12').style.display = 'none';
        document.getElementById('c3_13').style.display = 'none';
        document.getElementById('c3_14').style.display = 'none';
        document.getElementById('c3_15').style.display = 'none';
        document.getElementById('c3_16').style.display = 'none';
    }
    if (!has_freq){
        document.getElementById('c3_12').style.display = 'none';
        document.getElementById('c3_22').style.display = 'none';
    }
    if (!has_hr){
        document.getElementById('c3_16').style.display = 'none';
        document.getElementById('c3_26').style.display = 'none';
    }
    if (!has_alts){
        //alt
        document.getElementById('c3_14').style.display = 'none';
        document.getElementById('c3_24').style.display = 'none';
        //slope
        document.getElementById('c3_13').style.display = 'none';
        document.getElementById('c3_23').style.display = 'none';
    }
}

function hide_absent_data_laps(data,document){
    has_times=data["features"]["has_times"]
    has_alts=data["features"]["has_alts"]
    has_freq=data["features"]["has_freq"]
    has_hr=data["features"]["has_hr"]

    //slope
    document.getElementById('c3_13').style.display = 'none';
    document.getElementById('c3_23').style.display = 'none';

    if (!has_times){
        //speed
        document.getElementById('c3_11').style.display = 'none';
        document.getElementById('c3_21').style.display = 'none';
    }
    if (!has_freq){
        document.getElementById('c3_12').style.display = 'none';
        document.getElementById('c3_22').style.display = 'none';
    }
    if (!has_hr){
        document.getElementById('c3_16').style.display = 'none';
        document.getElementById('c3_26').style.display = 'none';
    }
    if (!has_alts){
        //alt
        document.getElementById('c3_14').style.display = 'none';
        document.getElementById('c3_24').style.display = 'none';
    }
}

function hide_absent_data_splits(data,document){
    has_times=data["features"]["has_times"]
    has_alts=data["features"]["has_alts"]
    has_freq=data["features"]["has_freq"]
    has_hr=data["features"]["has_hr"]

    //slope
    document.getElementById('c3_13').style.display = 'none';
    document.getElementById('c3_23').style.display = 'none';

    if (!has_times){
        //speed
        document.getElementById('c3_11').style.display = 'none';
        document.getElementById('c3_21').style.display = 'none';
        // all with times on x axis
        document.getElementById('c3_24').style.display = 'none';
        document.getElementById('c3_26').style.display = 'none';
        document.getElementById('c3_22').style.display = 'none';
    }
    if (!has_freq){
        document.getElementById('c3_12').style.display = 'none';
        document.getElementById('c3_22').style.display = 'none';
    }
    if (!has_hr){
        document.getElementById('c3_16').style.display = 'none';
        document.getElementById('c3_26').style.display = 'none';
    }
    if (!has_alts){
        //alt
        document.getElementById('c3_14').style.display = 'none';
        document.getElementById('c3_24').style.display = 'none';
    }
}

function axis_params(data,type,label,adjust_t,adjust,tick_count){
    
    format_parse=undefined
    padding={}
    min=undefined
    format=undefined
    
    if(type==="ts"){
        type="timeseries"
        format='%Y-%m-%d'
        if (label===undefined) label="Date"
    }else if(type==="time"|type=="time_min" ){
        if (type=="time"){
            format_parse="%H:%M:%S"
            format='%H:%M'
            if (label===undefined) label="Time (hours)"
        }else if (type=="time_min"){
            format_parse="%M:%S"
            format='%M:%S'
            if (label===undefined) label="Time (minutes)"
        }
        type="timeseries"
        console.log("format_parse",format_parse)
        if (adjust_t){
            data.sort(function(a, b){
                return a[x] > b[x];
            });
            max_time=data[data.length-1][x]
            //if (debug) console.log("max_time",max_time)
            if (max_time.substring(0,2)==="00"| max_time.substring(0,2)==="0:"){  //if the largest time has 0 hours
                format='%M:%S'
                if (label===undefined) label="Time (minutes)"
            }
        }
    }else if (type==="category"){
        type="category"
        tick_count=undefined
    }else{
        type="indexed"
        format=d3.format('.2f')
        if (adjust){
            min_x=Math.min.apply(Math, data.filter(a => a[x]!=null & a[x]!=0).map(function(o) { return o[x]; }))
            max_x=Math.max.apply(Math, data.filter(a => a[x]!=null & a[x]!=0).map(function(o) { return o[x]; }))
            //if (debug) console.log("min_x","max_x",min_x,max_x)
            if(min_x/max_x<0.3){
                min=0
                padding={left:0}
            }
        }
    }
    return type, format,format_parse, label,tick_count,min,padding
}


// function format_ms(max_ms,add_km=False){
//     //below one hour: min/sec
//     if (max_ms < 1000*60*60){
//         if (add_km){
//             label="(min/km)"
//         }else{
//             label="(min)"
//         }
//         return {"format":d3.timeFormat("%M:%S",),"label":label }
//     //below 24 hour: hour/min
//     }else if (max_ms < 1000*60*60*24){
//         if (add_km){
//             label="(h/km)"
//         }else{
//             label="(h)"
//         }
//         return {"format":d3.timeFormat("%H:%M",) ,"label":label}
//     //above 24 gours:date
//     }else{
//         return {"format":d3.timeFormat("%Y-%m-%d",) ,"label":""}
//     }
// }

function format_m(max_m,add_km=False){
    //in input I have minutes
    //below one hour: min/sec
    if (max_m < 60){
        if (add_km){
            label="(min/km)"
        }else{
            label="(min)"
        }
        return {"format":minutes_to_ms,"label":label }
    //below 24 hour: hour/min
    }else if (max_m < 60*24){
        if (add_km){
            label="(h/km)"
        }else{
            label="(h)"
        }
        return {"format":minutes_to_hm ,"label":label}
    //above 24 hours:date
    // TODO: this will not work
    }else{
        return {"format":d3.timeFormat("%Y-%m-%d",) ,"label":""}
    }
}

//https://stackoverflow.com/questions/37096367/how-to-convert-seconds-to-minutes-and-hours-in-javascript
function minutes_to_ms(m) {
    d=m*60

    var m = Math.floor(d % 3600 / 60);
    var s = Math.floor(d % 3600 % 60);

    return m + ":" + s.toString().padStart(2, "0")
}

function minutes_to_hm(m) {
    d=m*60

    var h = Math.floor(d / 3600);
    var m = Math.floor(d % 3600 / 60);

    return h + ":" + m.toString().padStart(2, "0")
}