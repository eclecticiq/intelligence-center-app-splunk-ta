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
], function ($, splunk_js_sdk, mvc) {
    console.log("lookup_observables.js require(...) called");
    tokens = mvc.Components.get("default");
    var value = tokens.get("q")
    var index = tokens.get("index")
    var host = tokens.get("host")
    var source = tokens.get("source")
    var sourcetype = tokens.get("sourcetype")
    var event_time = tokens.get("event_time")
    var field_name = tokens.get("field_name")
    $("#loading").text("Loading...")

    var http = new splunk_js_sdk.SplunkWebHttp();

    var service = new splunkjs.Service(
        http,
        appNamespace,
    );
    var storagePasswords = service.storagePasswords();
    var creds = [];
    var response = storagePasswords.fetch(
        function (err, storagePasswords) {
            if (err) { console.warn(err); }
            else {
                response = storagePasswords.list();
                var my_list = [];
                for (var i = 0; i < response.length; i++) {
                    var uname = ""
                    var api_key = ""
                    if (response[i]["_acl"]["app"] == "TA-eclecticiq") {
                        if (response[i]["_properties"]["realm"].endsWith("settings") == true) {
                            uname = "proxy_pass"
                        }
                        else {
                            uname = "eiq"
                        }
                        api_key = response[i]["_properties"]["clear_password"];
                        if (api_key.includes("splunk_cred_sep") == true) {
                            continue;
                        }
                        var temp = {};
                        temp[uname] = api_key;
                        my_list.push(temp);
                    }
                }
                localStorage.setItem("response", JSON.stringify(my_list))
            }
        });
    var creds = JSON.parse(localStorage.getItem("response"))
    localStorage.removeItem("response")

    api_key = JSON.parse(Object.values(creds[0])[0])['api_key']
    data = {}
    data['value'] = value
    data['creds'] = ""
    for (var i = 0; i < creds.length; i++) {
        if (creds[i]["eiq"] != undefined) {
            first_cred = JSON.parse(creds[i]["eiq"])
            data['creds'] = first_cred["api_key"]
            break;
        }
    }
    data['proxy_pass'] = ""
    for (var i = 0; i < creds.length; i++) {
        if (creds[i]["proxy_pass"] != undefined) {
            first_cred = JSON.parse(creds[i]["proxy_pass"])
            data['proxy_pass'] = first_cred["proxy_password"]
            break;
        }
    }


    completeSetup(data)
    sighting_url = "create_sighting_dashboard?q=" + value
    sighting_url = sighting_url + "&index="+index+"&"
    sighting_url = sighting_url + "&host="+host+"&"
    sighting_url = sighting_url + "&source="+source+"&"
    sighting_url = sighting_url + "&sourcetype="+sourcetype+"&"
    sighting_url = sighting_url + "&event_time="+event_time+"&"
    sighting_url = sighting_url + "&field_name="+field_name

    $("#create_sighting").click(function () { window.location.replace(sighting_url); });


    async function makeRequest(url, data) {
        return new Promise((resolve, reject) => {
            const service = mvc.createService();
            service.post(url, data, (err, resp) => {
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

        try {
            response = makeRequest('/services/lookup_observables', data);

            await response;
        } catch (e) {
            console.log(e)
        }

        console.log("lookup_observables endpoint called.");


    }
    response.then(function (result) {
        $("#loading").text("")
        $("#mytable").append(createTable(result['data']))
    });

    function createTable(data) {

        var table_header = `<table class="table table-striped tableChart chart1Top"  style="width: 100%; color: black;  border: 1px solid #dddddd;
                            height: 30px;" id="chart1">
                                <thead>
                                    <tr role="row" style="background-color: #42b598 !important;">
                                        <th class="sorting_asc" tabindex="0" scope="col"
                                            rowspan="1" colspan="1" aria-sort="ascending"
                                             style="width: 700px; background-color: #42b598 !important;">
                                            Title</th>
                                        <th class="sorting_asc" tabindex="0" scope="col"
                                            rowspan="1" colspan="1" aria-sort="ascending"
                                             style="width: 700px; background-color: #42b598 !important;">
                                            Description</th>
                                             <th class="sorting_asc" tabindex="0" scope="col"
                                            rowspan="1" colspan="1" aria-sort="ascending"
                                             style="width: 700px; background-color: #42b598 !important;">
                                             
                                             Source Name</th>
                                             <th class="sorting_asc" tabindex="0" scope="col"
                                            rowspan="1" colspan="1" aria-sort="ascending"
                                             style="width: 700px; background-color: #42b598 !important;">

                                            Tags</th>
                                             <th class="sorting_asc" tabindex="0" scope="col"
                                            rowspan="1" colspan="1" aria-sort="ascending"
                                             style="width: 700px; background-color: #42b598 !important;">

                                             Threat Start</th>
                                             <th class="sorting_asc" tabindex="0" scope="col"
                                            rowspan="1" colspan="1" aria-sort="ascending"
                                             style="width: 700px; background-color: #42b598 !important;">


                                            Observables</th>
                                    </tr>
                                </thead> <tbody>`

        var tbody = ""
        for (item in data) {
            if (item < data.length - 1) {
                var str_htm = "<tr>"
                str_htm = str_htm + "<td>" + data[item]["title"] + "</td>"
                str_htm = str_htm + "<td>" + data[item]["description"] + "</td>"
                str_htm = str_htm + "<td>" + data[item]["source_name"] + "</td>"
                str_htm = str_htm + "<td>" + data[item]["tags"] + "</td>"
                str_htm = str_htm + "<td>" + data[item]["threat_start_time"] + "</td>"
                start = "<td><table  class=\"table table-striped tableChart chart1Top\"  style=\"width: 100%; color: black;  border: 1px solid #dddddd;height: 30px;\" id=\"chart\"><thead><th role=\"row\" style=\"background-color: #42b598;\">Kind</th><th role=\"row\" style=\"background-color: #42b598;\">Value</th><th role=\"row\" style=\"background-color: #42b598;\">Maliciousness</th></thead><tbody>"

                for (var item1 in data[item]['observables']) {
                    if (item1 < data[item]['observables'].length) {
                        // console.log(data[item]['observables'][item1])
                        start = start + "<tr><td>" + data[item]['observables'][item1]["type"] + "</td>" + "<td>" + data[item]['observables'][item1]["value"] + "</td>" + "<td>" + data[item]['observables'][item1]["classification"] + "</td></tr>"
                    }
                }

                start = start + "</tbody></table></td>"
                str_htm = str_htm + start
                tbody = tbody + str_htm + "</tr>"

            }

        }
        tbody = tbody + "</tbody>"
        table_header = table_header + tbody + "</table>"
        return table_header
    }


});








