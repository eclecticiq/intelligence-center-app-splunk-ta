"use strict";

const appName = "TA-eclecticiq";
const appNamespace = {
    owner: "nobody",
    app: appName,
    sharing: "app",
};
const pwRealm = "TA-eclecticiq_realm";


// Splunk Web Framework Provided files
require([
    "jquery", "splunkjs/splunk", "splunkjs/mvc",
], function($, splunk_js_sdk, mvc) {
    console.log("lookup_observables.js require(...) called");
    tokens = mvc.Components.get("default");
    var value = tokens.get("q")
    console.log(value)

    var http = new splunk_js_sdk.SplunkWebHttp();

    var service = new splunk_js_sdk.Service(
        http,
        appNamespace,
    );
    var storagePasswords = service.storagePasswords();
    var creds = [];
    let url_key = "";
    var response = storagePasswords.fetch(
    function (err, storagePasswords) {
        if (err) 
            {console.warn(err);}
        else {
        response = storagePasswords.list();
        var my_list = [];
        for(var i=0; i< response.length; i++){
            var uname = ""
            var api_key = ""
            if(response[i]["_acl"]["app"] == "TA-eclecticiq"){
            uname  = response[i]["_properties"]["username"];
            api_key = response[i]["_properties"]["clear_password"];
            var temp = {};
            temp[uname] = api_key;
            my_list.push(temp);
            }
        }
        localStorage.setItem("response", JSON.stringify(my_list))
        }
    });
    var creds = JSON.parse(localStorage.getItem("response"))
    console.log(creds[0])

    api_key = JSON.parse(Object.values(creds[0])[0])['api_key']
    console.log(api_key)
    data = {}
    data["api_key"]=api_key
    data["sighting_value"]=value


    completeSetup(data)
    sighting_url = "create_sighting_dashboard?q=" + value

    $("#create_sighting").click(function () {window.location.replace(sighting_url);});


    async function makeRequest(url, data) {
        return new Promise((resolve, reject) => {
            const service = mvc.createService();
            service.post(url , data, (err, resp) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(resp);
                }
            })
        })
    }


    // function for "Lookup observables" 
    async function completeSetup(data) {
        console.log("lookup_observables.js completeSetup called");

        try{
            response =  makeRequest('/services/lookup_observables', data);
          
            await response;
            }catch(e){
                    console.log(e)
            }
            
            console.log("lookup_observables endpoint called.");

    
    }
    response.then(function(result) {
        console.log(result['data'])
        $("#mytable").append(createTable(result['data']))
});

function createTable(data){
    console.log("data")
    console.log(data)
    var table_header = `<table class="table table-striped tableChart chart1Top"  style="width: 100%; color: black;  border: 1px solid #dddddd;
                            height: 30px;" id="chart1">
                                <thead>
                                    <tr role="row" style="background-color: #42b598;">
                                        <th class="sorting_asc" tabindex="0" scope="col"
                                            rowspan="1" colspan="1" aria-sort="ascending"
                                             style="width: 700px;">
                                            Title</th>
                                        <th class="sorting_asc" tabindex="0" scope="col"
                                            rowspan="1" colspan="1" aria-sort="ascending"
                                             style="width: 700px;">
                                            Description</th>
                                             <th class="sorting_asc" tabindex="0" scope="col"
                                            rowspan="1" colspan="1" aria-sort="ascending"
                                             style="width: 700px;">
                                             
                                             Source Name</th>
                                             <th class="sorting_asc" tabindex="0" scope="col"
                                            rowspan="1" colspan="1" aria-sort="ascending"
                                             style="width: 700px;">

                                            Tags</th>
                                             <th class="sorting_asc" tabindex="0" scope="col"
                                            rowspan="1" colspan="1" aria-sort="ascending"
                                             style="width: 700px;">

                                             Threat Start</th>
                                             <th class="sorting_asc" tabindex="0" scope="col"
                                            rowspan="1" colspan="1" aria-sort="ascending"
                                             style="width: 700px;">


                                            Observables</th>
                                    </tr>
                                </thead> <tbody>`
                                
    var tbody = ""
    for(item in data){
        if (item< data.length)
        {
        console.log(data[item])
        console.log("title :"+data[item]["title"])
            var str_htm = "<tr>"
            str_htm = str_htm + "<td>"+data[item]["title"]+"</td>"
            str_htm = str_htm + "<td>"+data[item]["description"]+"</td>"
            str_htm = str_htm + "<td>"+data[item]["source_name"]+"</td>"
            str_htm = str_htm + "<td>"+data[item]["tags"]+"</td>"
            str_htm = str_htm + "<td>"+data[item]["threat_start_time"]+"</td>"
            start = "<td><table  class=\"table table-striped tableChart chart1Top\"  style=\"width: 100%; color: black;  border: 1px solid #dddddd;height: 30px;\" id=\"chart\"><thead><th role=\"row\" style=\"background-color: #42b598;\">Kind</th><th role=\"row\" style=\"background-color: #42b598;\">Value</th><th role=\"row\" style=\"background-color: #42b598;\">Maliciousness</th></thead><tbody>"
            
            for(var item1 in data[item]['observables']){
                if (item1< data[item]['observables'].length)
        {
                // console.log(data[item]['observables'][item1])
                start = start + "<tr><td>"+data[item]['observables'][item1]["type"]+"</td>" + "<td>"+data[item]['observables'][item1]["value"]+"</td>"+"<td>"+data[item]['observables'][item1]["classification"]+"</td></tr>"
            }
        }
            
            start = start + "</tbody></table></td>"
            str_htm = str_htm + start
            tbody = tbody+ str_htm+ "</tr>"
   
            }
            
        }
            tbody = tbody+"</tbody>"
            table_header = table_header+tbody+"</table>"
    
            
  return table_header
}

    
});








