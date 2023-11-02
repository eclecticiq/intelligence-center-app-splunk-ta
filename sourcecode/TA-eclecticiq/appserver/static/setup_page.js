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
    "jquery", "splunkjs/splunk", "splunkjs/mvc"
], function ($, splunkjs, mvc) {
    console.log("setup_page.js require(...) called");
    $("#setup_button").prop('disabled', false);
    tokens = mvc.Components.get("default");
    var value = tokens.get("q")
    var index = tokens.get("index")
    var host = tokens.get("host")
    var source = tokens.get("source")
    var sourcetype = tokens.get("sourcetype")
    var time = tokens.get("event_time")
    var field = tokens.get("field_name")
    var event_hash = tokens.get("raw") 
    var http = new splunkjs.SplunkWebHttp();
    
    // console.log("sessionkey = "+splunkjs.Context)

    var service = new splunkjs.Service(
        http,
        appNamespace,
    );
    // console.log("Sessionkey: ", $.cookie("splunk_sessionkey"));
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
                        if(response[i]["_properties"]["realm"].endsWith("settings") == true){
                            uname = "proxy_pass"
                        }
                        else{
                            uname = "eiq"
                        }
                        api_key = response[i]["_properties"]["clear_password"];
                        if(api_key.includes("splunk_cred_sep")==true){
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
    $("#sighting_value").val(value)
    console.log("Sighting of : " + String(value))
    $("#sighting_title").val("Sighting of : " + String(value))

    // Register .on( "click", handler ) for "Complete Setup" button
    $("#setup_button").click(completeSetup);
    
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

    // onclick function for "Complete Setup" button from setup_page_dashboard.xml
 async function completeSetup() {
    console.log("setup_page.js completeSetup called");
    $("#msg").text("");

    $("#setup_button").prop('disabled', true);
    $("#loading").text("Loading...");

    // Value of password_input from setup_page_dashboard.xml
    const sighting_value = $('#sighting_value').val();
    const sighting_desc = $('#sighting_desc').val();
    const sighting_title = $('#sighting_title').val();
    const sighting_tags = $('#sighting_tags').val();
    // taking value from the drop down
    var sighting_type_obj = document.getElementById("sighting_type");
    var sighting_type = sighting_type_obj.options[sighting_type_obj.selectedIndex].text;

    var confidence_level_obj = document.getElementById("confidence_level");
    var confidence_level = confidence_level_obj.options[confidence_level_obj.selectedIndex].text;
    if(sighting_value == ""){
        $("#loading").text("")
        $("#msg").css('color', 'red');
        $("#msg").text("Sighting Value field is required!");
        $("#setup_button").prop('disabled', false);
        return
    }

    if(sighting_desc == ""){
        $("#loading").text("");
        $("#msg").css('color', 'red');
        $("#msg").text("Sighting Description field is required!");
        $("#setup_button").prop('disabled', false);
        return
    }

    if(sighting_title == ""){
        $("#loading").text("");
        $("#msg").css('color', 'red');
        $("#msg").text("Sighting Title field is required!");
        $("#setup_button").prop('disabled', false);
        return
    }

    if(sighting_tags == ""){
        $("#loading").text("");
        $("#msg").css('color', 'red');
        $("#msg").text("Sighting Tags field is required!");
        $("#setup_button").prop('disabled', false);
        return
    }

    const data = {};

    data["sighting_value"]=sighting_value;
    data["sighting_desc"]=sighting_desc;
    data["sighting_title"]=sighting_title;
    data["sighting_tags"]=sighting_tags;
    data['confidence_level']=confidence_level;
    data['sighting_type']=sighting_type;
    
    data["src"] = "";
    data["dest"] = "";
    data["event_hash"] = "";
    data["feed_id_eiq"] = "";
    data["meta_entity_url_eiq"] = "";

    if(index!=undefined){data["index"] = index}else{data["index"]=""}
    if(host!=undefined){data["host"] = host}else{data["host"]=""}
    if(source!=undefined){data["source"] = source}else{data["source"]=""}
    if(sourcetype!=undefined){data["sourcetype"] = sourcetype}else{data["sourcetype"]=""}
    if(time!=undefined){data["time"] = time}else{data["time"]=""}
    if(field!=undefined){data["field"] = field}else{data["field"]=""}
    if(event_hash!=undefined){data["_raw"] = event_hash}else{data["_raw"]=""}
    
    try
    { 
        let response = await makeRequest('/services/create_sighting', data);
        $("#loading").text("")
        $("#msg").css('color', 'blue');
        $("#msg").text(response["data"])
        $("#setup_button").prop('disabled', false);
        }catch(e){
                $("#loading").text("")
                console.log(e)
                $("#msg").css('color', 'red');
                $("#msg").text(e["data"])
                $("#setup_button").prop('disabled', false);
        }
    }
})
