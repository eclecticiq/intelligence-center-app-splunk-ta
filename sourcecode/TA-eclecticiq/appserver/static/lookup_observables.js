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
], function ($, splunkjs, mvc) {
    tokens = mvc.Components.get("default");
    var value = tokens.get("q")
    var index = tokens.get("index")
    var host = tokens.get("host")
    var source = tokens.get("source")
    var sourcetype = tokens.get("sourcetype")
    var event_time = tokens.get("event_time")
    var field_name = tokens.get("field_name")
    $("#msg").css('color', 'blue');
    $("#loading").text("Loading...")

    var http = new splunkjs.SplunkWebHttp();

    var service = new splunkjs.Service(
        http,
        appNamespace,
    );

    data = {}
    data['value'] = value

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
        try {
            response = makeRequest('/services/lookup_observables', data);

            await response;
        } catch (e) {
            console.log(e)
        }
    }
    response.then(function (result) {
        $("#loading").text("");
        if (result.data.length>1)
        {
        $("#mytable").append(createTable(result['data']))
     }
     else { $("#msg").css('color', 'black');
     $("#loading").text("No data found!")}
    });

    function createTable(data) {
        if (data == "False" || data == "false"){            
            return "No Observable found."
        } else if (data.startsWith("It was an error")) {
            return data
        } else {
            var table_header = `<table class="table table-striped tableChart chart1Top"  style="width: 100%; color: black;  border: 1px solid #dddddd;
                                height: 30px;" id="chart1">
                                    <thead>
                                        <tr role="row" style="background-color: #42b598 !important;">
                                            <th class="sorting_asc" tabindex="0" scope="col"
                                                rowspan="1" colspan="1" aria-sort="ascending"
                                                 style="width: 10%; background-color: #42b598 !important; word-break: break-word;">
                                                Title</th>
                                            <th class="sorting_asc" tabindex="0" scope="col"
                                                rowspan="1" colspan="1" aria-sort="ascending"
                                                 style="width: 25%; background-color: #42b598 !important; word-break: break-word;">
                                                Description</th>
                                                 <th class="sorting_asc" tabindex="0" scope="col"
                                                rowspan="1" colspan="1" aria-sort="ascending"
                                                 style="width: 10%; background-color: #42b598 !important; word-break: break-word;">
                                                 
                                                 Source Name</th>
                                                 <th class="sorting_asc" tabindex="0" scope="col"
                                                rowspan="1" colspan="1" aria-sort="ascending"
                                                 style="width: 10%; background-color: #42b598 !important; word-break: break-word;">

                                                Tags</th>
                                                 <th class="sorting_asc" tabindex="0" scope="col"
                                                rowspan="1" colspan="1" aria-sort="ascending"
                                                 style="width: 10%; background-color: #42b598 !important; word-break: break-word;">

                                                 Threat Start</th>
                                                 <th class="sorting_asc" tabindex="0" scope="col"
                                                rowspan="1" colspan="1" aria-sort="ascending"
                                                 style="width: 35%; background-color: #42b598 !important; word-break: break-word;">

                                                Observables</th>
                                        </tr>
                                    </thead> <tbody>`

            var tbody = ""
            data = data.replace(/'/g, '\\"');

            var data_json = JSON.parse(data)

            for (var item in data_json) {
                if (item < data_json.length) {

                    var str_htm = "<tr>"
                    str_htm = str_htm + "<td>" + data_json[item]["entity_title"] + "</td>"
                    str_htm = str_htm + "<td style='word-break: break-word;'>" + data_json[item]["description"] + "</td>"
                    str_htm = str_htm + "<td>" + data_json[item]["source_name"] + "</td>"
                    str_htm = str_htm + "<td style='word-break: break-word;'>" + data_json[item]["tags_list"] + "</td>"
                    str_htm = str_htm + "<td>" + data_json[item]["created_at"] + "</td>"
                    start = "<td><table  class=\"table table-striped tableChart chart1Top\"  style=\"width: 100%; word-break: break-word; color: black; border: 1px solid #dddddd;height: 30px;\" id=\"chart\"><thead><th role=\"row\" style=\"background-color: #42b598;\">Kind</th><th role=\"row\" style=\"background-color: #42b598; word-break: break-word;\">Value</th><th role=\"row\" style=\"background-color: #42b598;\">Maliciousness</th></thead><tbody>"

                    for (var item1 in data_json[item]['observables_list']) {
                        if (item1 < data_json[item]['observables_list'].length) {
                            start = start + "<tr><td>" + data_json[item]['observables_list'][item1]["type"] + "</td>" + "<td>" + data_json[item]['observables_list'][item1]["value"] + "</td>" + "<td>" + data_json[item]['observables_list'][item1]["maliciousness"] + "</td></tr>"
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
    }
});