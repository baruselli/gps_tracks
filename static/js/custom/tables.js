function create_table(
        table_id,
        data,
        url_many_tracks,
        url_many_tracks_group,
        url_many_tracks_delete,
        url_many_tracks_merge=null,
        url_many_tracks_plot=null,
        options={},
        url_many_tracks_source=null,
    ){
    var columns=[
        { "data": "id" ,
          "render": function ( data, type, row, meta ) {
            return '<font color='+row.color+'>'+row.id+'</font>';
        }},
        { "data": "png_file" ,
          "render": function ( data, type, row, meta ) {
            return '<a href='+row.link+'>'+
                        '<img src="'+data+'" style="max-height:40px;max-width:60px;height:auto;width:auto;"> </a>'
        }},
       { "data": "name",
         "render": function ( data, type, row, meta ) {
         name=data.length > 40 ?  data.substr( 0, 40 ) +'…' :  data;
            return '<a href='+row.link+'>'+name+'</a>';
        }},
       { "data": "time" },
       { "data": "end_country" },
       { "data": "end_city" },
//       { "data": "n_waypoints" },
       { "data": "n_photos" ,
        "render": function ( data, type, row, meta ) {
            if (data===0){ return data}
            else{return '<a href='+row.photos_link+'>'+data+'</a>';}
        }},
       { "data": "duration",
         "render":{
               display: 'duration_string2',
               _: 'duration'}
        },
       { "data": "length" ,
         "render":{
               display: 'length_string',
               _: 'length'},
        },
       { "data": "speed",
         "render":{
               display: 'speed_string',
               _: 'speed'},
        },]

    if (options["has_freq"]){
            columns.push(
            { "data": "pace" ,
            "render":{
                   display: 'pace_string',
                   _: 'pace',},
            },
            { "data": "frequency",
             "render":{
                   display: 'frequency_string',
                   _: 'frequency'},
           },
                      )
    }else{
        $( ".freq_field" ).remove();
        $( ".pace_field" ).remove();
    }

    if (options["has_hr"]){
            columns.push(
           { "data": "total_heartrate",
             "render":  function ( data, type, row, meta ) {
                    if (data) return data.toFixed(0)
                    else return ""
                }
            },)
    }else{
        $( ".hr_field" ).remove();
    }


    columns =columns.concat([
        { "data": "similarity",
            "render": function ( data, type, row, meta ) {
                return data.toFixed(3)
        }},
        { "data": "duplicated_group",
            "render": function ( data, type, row, meta ) {
                return data
        }},
        { "data": "distance",
         "render":{
               display: 'distance_string',
               _: 'distance'},
        }
        ])



    console.log("create_table")
    console.log("data", data)

    //console.log( Object.keys(data))
    if (Object.keys(data).includes("Tracks")){
        data=data["Tracks"]
    }else{
    }

    //remove png from columns and from table if too much data
    if (data.length>30){
        png_index = columns.findIndex(x => x.data ==="png_file");
        columns.splice(png_index,1);
        $( ".png_field" ).remove();
    }

    //date column to order and summarize
    date_col = columns.findIndex(x => x.data ==="time");
    city_col = columns.findIndex(x => x.data ==="end_city");
    coun_col = columns.findIndex(x => x.data ==="end_country");
    order_asc="desc"

    //order by similarity or distance if present in data
    if(data[0]){
       // console.log(data[0])
        if ("similarity" in data[0]){
            ok_similarity=true
        }else{
            ok_similarity=false
        }
        if ("duplicated_group" in data[0]){
            ok_duplicated=true
        }else{
            ok_duplicated=false
        }
        if ("distance" in data[0]){
            ok_distance=true
        }else{
            ok_distance=false
        }}
    else{
        ok_similarity=false
        ok_distance=false
        ok_duplicated=false
    }
    if(ok_similarity){
        dist_col = columns.findIndex(x => x.data ==="distance");
        columns.splice(dist_col,1);
        dup_col = columns.findIndex(x => x.data ==="duplicated_group");
        columns.splice(dup_col,1);
        $( ".distance_field" ).remove();
        $( ".duplicated_field" ).remove();
        order_col = columns.findIndex(x => x.data ==="similarity")
    //order by distance if present in data
    }else if(ok_distance){
        sim_col = columns.findIndex(x => x.data ==="similarity");
        columns.splice(sim_col,1);
        dup_col = columns.findIndex(x => x.data ==="duplicated_group");
        columns.splice(dup_col,1);
        $( ".similarity_field" ).remove();
        $( ".duplicated_field" ).remove();
        order_col = columns.findIndex(x => x.data ==="distance")
        order_asc="asc"
    }else if(ok_duplicated){
        sim_col = columns.findIndex(x => x.data ==="similarity");
        columns.splice(sim_col,1);
        dist_col = columns.findIndex(x => x.data ==="distance");
        columns.splice(dist_col,1);
        $( ".similarity_field" ).remove();
        $( ".distance_field" ).remove();
        order_col = columns.findIndex(x => x.data ==="duplicated_group")
        order_asc="asc"
    //remove similarity from column and html if not present in data
    //remove similarity from column and html if not present in data
    }else{
        sim_col = columns.findIndex(x => x.data ==="similarity");
        columns.splice(sim_col,1);
        $( ".similarity_field" ).remove();
        dist_col = columns.findIndex(x => x.data ==="distance");
        columns.splice(dist_col,1);
        $( ".distance_field" ).remove();
        dup_col = columns.findIndex(x => x.data ==="duplicated_group");
        columns.splice(dup_col,1);
        $( ".duplicated_field" ).remove();
        order_col=date_col
    }

    //console.log("options",options)
    if ("order_col" in options) order_col=options["order_col"]
    if ("order_asc" in options) order_asc=options["order_asc"]

    //console.log(ok_distance, order_col, columns)
    //buttons
    var buttons=[
        {
         text: 'Select all',
         action: function ( e, dt, node, config) {
             select_all(e, dt, node, config)
             reset_point_sizes(class_name="leaflet_track_marker", how="highlight") //track as line
             reset_point_sizes(class_name="leaflet_track_point", how="highlight") //track as points
         }},
         {text: 'Reset selection',
         action: function ( e, dt, node, config) {
             deselect_all(e, dt, node, config)
             //make all track points the default size
             reset_point_sizes("leaflet_track_marker")
             reset_point_sizes("leaflet_track_point")
         }},
        {text: 'Map tracks',
        action:function ( e, dt, node, config) {
            ids=get_track_ids(e, dt, node, config)
            if(ids){window.location=url_many_tracks+ids+"&use_points=0&reduce_points=every&every=0&do_plots=0"}
        }},
        {text: 'Map & Plot tracks',
        action:function ( e, dt, node, config) {
            ids=get_track_ids(e, dt, node, config)
            if(ids){window.location=url_many_tracks+ids+"&use_points=0&reduce_points=every&every=0&do_plots=1"}
        }},
        { text: 'Create Group',
        action:function ( e, dt, node, config) {
        ids=get_track_ids(e, dt, node, config)
        console.log(ids);
        if (ids) {window.location=url_many_tracks_group+ids}
        }},
         { text: 'Merge Tracks',
        action:function ( e, dt, node, config) {
        ids=get_track_ids(e, dt, node, config)
        console.log(ids);
        if (ids) {window.location=url_many_tracks_merge+ids}
        }},
        { text: 'Zip',
        action:function ( e, dt, node, config) {
        ids=get_track_ids(e, dt, node, config)
        console.log(ids);
        if (ids) {window.location=url_many_tracks_source+ids}
        }},
         { text: 'Plot',
        action:function ( e, dt, node, config) {
        ids=get_track_ids(e, dt, node, config)
        console.log(ids);
        if (ids) {window.location=url_many_tracks_plot+ids}
        }},
        "excel",
        { text: 'Delete tracks',
        action:function ( e, dt, node, config) {
            ids=get_track_ids(e, dt, node, config)
            if (ids) {
                var r=confirm("Really delete tracks?");
                if (r == true) {
                window.location=url_many_tracks_delete+ids;
            }}}}
        ]
    var table = $(table_id).DataTable( {
        "data": data,
        "columns":columns,
        //'columnDefs': [{'max-width': '20px', 'targets': 4}],
        paging: false,
        //keys: true,
        "order": [[ order_col, order_asc ]],
        dom: 'BrtipBf',
        select: true,
        searching: true,
        info: true,
        buttons: buttons,
        initComplete: function () {
         this.api().columns([date_col,city_col,coun_col]).every( function () {
                var column = this;
                //console.log(this)
                var select = $('<select><option value=""></option></select>')
                    .appendTo( $(column.footer()).empty() )
                    .on( 'change', function () {
                        var val = $.fn.dataTable.util.escapeRegex(
                            $(this).val()
                        );

                        column
                            .search( val ? '^'+val+'$' : '', true, false )
                            .draw();
                    } );
                column.data().unique().sort().each( function ( d, j ) {
                if(d){substr_d=d.substr(0,30)}
                else{substr_d=""}
                    select.append( '<option value="'+d+'">'+substr_d+'</option>' )
                } );
            } );
        }
    } );
    return table
}


function select_all( e, dt, node, config) {
    dt.rows().select();
}

function deselect_all( e, dt, node, config) {
    dt.rows().deselect();
}

function get_object_ids(e, dt, node, config,how) {
    var id_list=[];

    if (how==="filtered") dict={ search: 'applied'}
    if (how==="selected") dict={ selected: true }

    var track_list = dt  .rows( dict )
                            .every( function ( rowIdx, tableLoop, rowLoop ) {
                            var data = this.data();
                            id_list.push(data["id"]);
                            });
    console.log(id_list);
    var ids="";
    for (var id in id_list){
        console.log(id_list[id]);
    ids+=String(id_list[id])+"_"  ;
    }
    ids=ids.slice(0,-1)  //toglie l'ultimo ,
    console.log(ids);
    return ids
}


function get_track_ids(e, dt, node, config) {
    var id_list=[];
    var track_list = dt  .rows( { selected: true } )
                            .every( function ( rowIdx, tableLoop, rowLoop ) {
                            var data = this.data();
                            if(data["pk"]){
                                id_list.push(data["pk"]);
                            }else{
                                id_list.push(data[0]);
                            }
                            });
    console.log(id_list);
    var ids="";
    for (var id in id_list){
        console.log(id_list[id]);
    ids+=String(id_list[id])+"_"  ;
    //ids+="tracks="+String(id_list[id])+"&"  ;
    }
    ids=ids.slice(0,-1)  //toglie l'ultimo _ o &
    console.log(ids);
    return ids
}

function simple_table(table_id,options={}){
    var order_opt = options.order_opt|| [ 0, "asc" ];
    var export_btn = options.export_btn===true; //dft false
    var ordering = options.ordering!==false; //dft true

    if (export_btn){
        buttons=['excel',"copy","csv"]
    }else{
        buttons=[]
    }

    $(document).ready( function () {
        var events = $('#events');
        var table =    $(table_id)
        .DataTable({
         "paging": false,
         "searching": false,
         "ordering": ordering,
         "info":false,
         "order": order_opt,
         "select": false,
         "dom": 'Bfrtip',
         "buttons": buttons,
      //   "bSortable": true,
        } );
    } );
}


function create_table_waypoints(table_id,data,url_many_wps){
    console.log("create_table_waypoints data", data)
    var columns=[
        { "data": "id" ,
//          "render": function ( data, type, row, meta ) {
//            return '<font color='+row.color+'>'+row.id+'</font>';
//        }
        },
       { "data": "name",
         "render": function ( data, type, row, meta ) {
            return '<a href='+row.link+'>'+data+'</a>';
        }},
       { "data": "time",
          "render": function ( data, type, row, meta ) {
         if(data){
            return data;
            }else{
            return ""}
        }},
       { "data": "alt",
         "render": function ( data, type, row, meta ) {
         if(data){
            return data;
            }else{
            return ""}
        }},
       { "data": "related_track_name",
         "render": function ( data, type, row, meta ) {
         if(data){
            return '<a href='+row.track_link+'>'+data+'</a>';
            }else{
            return ""}
        }},
       { "data": "country" },
       { "data": "region" },
       { "data": "city" },
    ]

    date_col = columns.findIndex(x => x.data ==="time");
    city_col = columns.findIndex(x => x.data ==="city");
    coun_col = columns.findIndex(x => x.data ==="country");
    order_asc="desc"
    order_col=date_col

    var buttons=[
        {
         text: 'Show filtered',
         action: function ( e, dt, node, config) {
         console.log(e)
         console.log(dt)
         console.log(node)
         console.log(config)
            ids=get_object_ids(e, dt, node, config,"filtered")

            if(ids){window.location=url_many_wps+"?wps_ids="+ids}
         }},
        {
         text: 'Show selected',
         action: function ( e, dt, node, config) {
         console.log(e)
         console.log(dt)
         console.log(node)
         console.log(config)
            ids=get_object_ids(e, dt, node, config,"selected")
            if(ids){window.location=url_many_wps+"?wps_ids="+ids}
         }},
         ]

    var table = $(table_id).DataTable( {
        "data": data,
        "columns":columns,
        paging: true,
        "order": [[ order_col, order_asc ]],
        dom: 'rtipBf',
        select: true,
        searching: true,
        info: true,
        buttons: buttons,
        initComplete: function () {
                        this.api().columns([4,5,6,7]).every( function () {
                var column = this;
                var select = $('<select><option value=""></option></select>')
                .appendTo( $(column.footer()).empty() )
                .on( 'change', function () {
                    var val = $.fn.dataTable.util.escapeRegex(
                        $(this).val()
                    );

                    column
                        .search( val ? '^'+val+'$' : '', true, false )
                        .draw();
                } );
            column.data().unique().sort().each( function ( d, j ) {
            if(d){substr_d=d.substr(0,30)}
            else{substr_d=""}
                select.append( '<option value="'+d+'">'+substr_d+'</option>' )
            } );

                    })
            }
    })

    return table
}

function create_table_photos(table_id,data,url_many_photos){
    n_photos=data.length
    var columns=[
        { "data": "id" ,
//          "render": function ( data, type, row, meta ) {
//            return '<font color='+row.color+'>'+row.id+'</font>';
//        }
        },
       { "data": "preview",
          "render": function ( data, type, row, meta ) {
          if (true){
            return '<img src="'+row.thumbnail_url_path+'" style="max-height:60px;max-width:100px;height:auto;width:auto;">'
            }else{
            return ""}
        }},
       { "data": "name",
         "render": function ( data, type, row, meta ) {
            return '<a href='+row.link+'>'+data+'</a>';
        }},
       { "data": "date",
          "render": function ( data, type, row, meta ) {
         if(data){
            return data;
            }else{
            return ""}
        }},
       { "data": "country" },
       { "data": "city" },
       { "data": "region" },
    ]

    date_col = columns.findIndex(x => x.data ==="date");
    city_col = columns.findIndex(x => x.data ==="city");
    coun_col = columns.findIndex(x => x.data ==="country");
    order_asc="desc"
    order_col=date_col

    var buttons=[
        {
         text: 'Show filtered',
         action: function ( e, dt, node, config) {
         console.log(e)
         console.log(dt)
         console.log(node)
         console.log(config)
            ids=get_object_ids(e, dt, node, config,"filtered")
            if(ids){window.location=url_many_photos+"?photo_ids="+ids}
         }},
        {
         text: 'Show selected',
         action: function ( e, dt, node, config) {
         console.log(e)
         console.log(dt)
         console.log(node)
         console.log(config)
            ids=get_object_ids(e, dt, node, config,"selected")
            if(ids){window.location=url_many_photos+"?photo_ids="+ids}
         }},
         ]

    var table = $(table_id).DataTable( {
        "data": data,
        "columns":columns,
        paging: true,
        "order": [[ order_col, order_asc ]],
        dom: 'rtipBf',
        select: true,
        searching: true,
        info: true,
        buttons: buttons,
        initComplete: function () {
                        this.api().columns([3,4,5,6]).every( function () {
                var column = this;
                var select = $('<select><option value=""></option></select>')
                .appendTo( $(column.footer()).empty() )
                .on( 'change', function () {
                    var val = $.fn.dataTable.util.escapeRegex(
                        $(this).val()
                    );

                    column
                        .search( val ? '^'+val+'$' : '', true, false )
                        .draw();
                } );
            column.data().unique().sort().each( function ( d, j ) {
            if(d){substr_d=d.substr(0,30)}
            else{substr_d=""}
                select.append( '<option value="'+d+'">'+substr_d+'</option>' )
            } );

                    })
            }
    })
    console.log("a")

    return table
}

function summarize_table(column) {
        console.log(column)
    }

function add_group_stats(document,url,url_plots,add_details=true){
    $.getJSON(url,function(data){
        console.log(data)
        final_html=""
        final_html+="<table id='stats_table'>"
        final_html+="<thead><tr>"
        final_html+="<th>Property</th><th>Best</th><th>Average</th><th>Worst</th><th>Total</th><th>Best Track</th><th>Worst Track</th>"
        final_html+="</tr></thead>"
        for (property in data){
            data_tracks=data[property]["tracks"]
            final_html+="<tr>"
            if (data_tracks[0]) final_html+="<td><b><a target='_blank' href='"+url_plots+"?color=Speed&r=Uniform&h="+data_tracks[0]["name"]+"&x=Ordinal+number&y="+property+"'>"+property+"</a></b></td>"
            else final_html+="<td><b>"+property+"</b></td>"
            //best value
            if (data_tracks[0]) final_html+="<td>"+data_tracks[0]["value"]+"</td>"
            else final_html+="<td></td>"
            //average
            final_html+="<td>"+data[property]["average"]+"</td>"
            // worst value
            if (data_tracks[data_tracks.length-1]) final_html+="<td>"+data_tracks[data_tracks.length-1]["value"]+"</td>"
            else final_html+="<td></td>"
            //total
            final_html+="<td>"
            if (data[property]["total"]) final_html+=data[property]["total"]
            final_html+="</td>"
            //best track
            if (data_tracks[0]) final_html+="<td><a href='"+data_tracks[0]["link"]+"'>"+data_tracks[0]["name"]+"</a> - "+data_tracks[0]["date"] +"</td>"
            else final_html+="<td></td>"
            //worst track
            if (data_tracks[data_tracks.length-1]) final_html+="<td><a href='"+data_tracks[data_tracks.length-1]["link"]+"'>"+data_tracks[data_tracks.length-1]["name"]+"</a> - "+data_tracks[data_tracks.length-1]["date"] +"</td>"
            else final_html+="<td></td>"
            final_html+="</tr>"
        }
        final_html+="</table>"
        if (add_details){
            final_html+=add_group_stats_advanced(data)
            for (property in data){
                table_id='table_'+ property.replace(" ","").replace(" ","")
                simple_table("#"+table_id)
            }
        }
        simple_table("#stats_table",options={"ordering":false})
        $("#group_stats").append(final_html)
    });
}

function add_group_stats_advanced(data){
        final_html=""
        //more detailed
        var i=0
        for (property in data){
            i+=1;
            data_tracks=data[property]["tracks"]
            final_html+="<div style='width:12%;float:left;overflow:hidden;' class='left_div'>"
            if (data_tracks[0]) final_html+="<h3><a target='_blank' href='"+url_plots+"?color=Speed&r=Uniform&h="+data_tracks[0]["name"]+"&x=Ordinal+number&y="+property+"'>"+property+"</a></h3>"
            else final_html+="<h3>"+property+"</h3>"
            if (data_tracks[0]) final_html+="<p><b>Best</b>:"+data_tracks[0]["value"]+"</p>"
            final_html+="<p><b>Average</b>:"+data[property]["average"]+"</p>"
            if (data_tracks[data_tracks.length-1]) final_html+="<p><b>Worst</b>:"+data_tracks[data_tracks.length-1]["value"]+"</p>"
            final_html+="</div>"
            final_html+="<div style='width:30%;float:left;overflow:hidden;padding:3%' class='right_div'>"
            table_id='table_'+ property.replace(" ","").replace(" ","")
            table_string="<table id ='"+table_id+"'>"
            table_string+="<thead><tr><td>Rank</td><td>Track</td><td>Value</td><td>Date</td></tr></thead>"
            for (i in data_tracks){
                track_dict=data_tracks[i]
                row_string="<tr>"+
                            "<td>"+track_dict["rank"]+"</td>"+
                            "<td><a href='"+track_dict["link"]+"'>"+track_dict["name"]+"</a></td>"+
                            "<td>"+track_dict["value"]+"</td>"+
                            "<td>"+track_dict["date"]+"</td>"+
                            "</tr>"
                table_string+=row_string
            }
            table_string+="</table>"
            final_html+=table_string
            final_html+="</div>"
            if (i%2==0){
               final_html+="</div style='clear:left'>"
            }
        }
        return final_html
}

function create_table_logs(table_id){

    var table = $(table_id).DataTable( {
        paging: true,
        "order": [[ 0, "desc" ]],
        dom: 'rtipBf',
        select: true,
        searching: true,
        info: true,
        buttons: [],
        initComplete: function () {
                        this.api().columns([0,1]).every( function () {
                var column = this;
                var select = $('<select><option value=""></option></select>')
                .appendTo( $(column.footer()).empty() )
                .on( 'change', function () {
                    var val = $.fn.dataTable.util.escapeRegex(
                        $(this).val()
                    );

                    column
                        .search( val ? '^'+val+'$' : '', true, false )
                        .draw();
                } );
            column.data().unique().sort().each( function ( d, j ) {
            if(d){substr_d=d.substr(0,30)}
            else{substr_d=""}
                select.append( '<option value="'+d+'">'+substr_d+'</option>' )
            } );

                    })
            }
    })

    return table
}


function seconds_to_string(seconds){
    if (seconds<86400){
        var date = new Date(0);
        date.setSeconds(Math.round(seconds)); // specify value for SECONDS here
        var timeString = date.toISOString().substr(11, 8);
    }else{
        return (seconds/86400).toFixed(0)+"days"+((seconds%86400)/3600).toFixed(0)+"h"
    }
    return timeString
}


function add_info_from_selected_data(selected_data){
    count=0
    total_duration=0
    total_length=0
    total_speed=0
    total_duration_frequency=0
    total_frequency=0
    n_freq=0
    total_duration_hr=0
    total_hr=0
    n_hr=0
    for (i=0;i<selected_data.length;i++){
        count+=1
        //duration
        duration=selected_data[i]["duration"]["duration"]
        if (duration != undefined && duration !=null){
            total_duration+=duration
        }
        //length
        length=selected_data[i]["length"]["length"]
        if (length != undefined && length !=null){
            total_length+=length
        }
        //frequency
        frequency=selected_data[i]["frequency"]["frequency"]
        if (frequency && duration){
            total_duration_frequency+=duration
            total_frequency+=frequency*duration
            n_freq+=1
        }
        //hr
        hr=selected_data[i]["total_heartrate"]
        if (hr && duration){
            total_duration_hr+=duration
            total_hr+=hr*duration
            n_hr+=1
        }


    }
    
    if (count==0){
        var html=""
    }else{
        var html="<br>"
        if (total_duration){
            html += "Total duration: <b>"+
                    seconds_to_string(total_duration*60)+"</b>, "+
                    "Average duration: <b>" + 
                    seconds_to_string(total_duration/count*60)+"</b><br>"
        }
        if (total_length){
            html +="Total length: <b>" + 
                (total_length/1000).toFixed(2)+"km</b>, "+
                "Average length: <b>" + 
                (total_length/1000/count).toFixed(2)+"km</b><br>"
        }
        if (total_length && total_duration){
            html +="Average speed: <b>" + 
                (total_length/total_duration*60/1000).toFixed(1)+"km/h</b>, "+
                "Average pace: <b>" + 
                pace_from_speed(total_length/total_duration*60/1000)+"</b><br>"
        }
        if (total_duration_frequency && total_frequency){
            html +="Average frequency: <b>" + 
                (total_frequency/total_duration_frequency).toFixed(1)+"</b> ("+parseInt(n_freq)+" tracks)<br>"
        }
        if (total_duration_hr && total_hr){
            html +="Average heartrate: <b>" + 
                (total_hr/total_duration_hr).toFixed(1)+"</b> ("+parseInt(n_hr)+" tracks)<br>"
        }

    }

    $("#id_span_infos").html(html)
}


function pace_from_speed(speed){

    if (speed){
        if (speed>=1){
            pace = 60 / speed
            var date = new Date(0);
            date.setSeconds(Math.round(pace*60)); 
            var pace_string = date.toISOString().substr(14, 5)+"min/km"
        }else{
            var pace_string = ">1h/km"
        }
    }else{
        var pace_string=""
    }

    return pace_string
}