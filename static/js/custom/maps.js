//add google and mapbox variants to all providers
function enrich_basemaps(mapbox_token="",basemaps_mapbox=[]){
    //take all
    basemaps=L.TileLayer.Provider.providers
     //add google to providers from leaflet-providers.js
    basemaps["Google"] = {
            url: 'http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            options: {
                maxZoom: 20,
                subdomains:['mt0','mt1','mt2','mt3'],
                attribution: "Google"
                },
            variants: {
                GoogleSat: {},
                GoogleStreets: {
                    url:'http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
                },
                GoogleHybrid: {
                    url:'http://{s}.google.com/vt/lyrs=y,h&x={x}&y={y}&z={z}',
                },
                GoogleTerrain: {
                    url:'http://{s}.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
                },
            }
        }

    // add to MapBox some variants
    basemaps["MapBox"]["accessToken"]=mapbox_token
    basemaps["MapBox"]["url"]=basemaps["MapBox"]["url"].replace("{accessToken}",mapbox_token)
    base_url=basemaps["MapBox"]["url"];
    variants={}
    for (i in basemaps_mapbox){
        m=basemaps_mapbox[i]
        variants[m]={url:base_url.replace("{id}","mapbox."+m)}
    }
    basemaps["MapBox"]["variants"]=variants

    L.TileLayer.Provider.providers=basemaps
    return L.TileLayer.Provider.providers

}


//get all basemaps names map.variant after enriching them
function get_basemaps_names(mapbox_token="",basemaps_mapbox=[]){

    providers=enrich_basemaps(mapbox_token=mapbox_token,basemaps_mapbox=basemaps_mapbox)
    list=[]
    for (name in providers){
        p=providers[name]
        variants=p["variants"]
        if (variants){
            for (v_name in variants){
            total_name=name+"."+ v_name
            list.push(total_name)
            }
        }else{
            list.push(name)
        }
    }
    return list
}


//get objects from names as a dict map_name:object(map_name)
function get_basemaps(basemaps_names,mapbox_token,basemaps_mapbox){

    //add google and mapbox variants
    enrich_basemaps(mapbox_token=mapbox_token,basemaps_mapbox=basemaps_mapbox)
    // build all objects
    a={}
    for (i in basemaps_names){
        m=basemaps_names[i]
        a[m]=L.tileLayer.provider(m)
    }

    return a
}
