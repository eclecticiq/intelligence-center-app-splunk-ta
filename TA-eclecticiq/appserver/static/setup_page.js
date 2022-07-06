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
    console.log("setup_page.js require(...) called");
    tokens = mvc.Components.get("default");
    var value = tokens.get("q")
    console.log(value)
    var http = new splunkjs.SplunkWebHttp();

    var service = new splunkjs.Service(
        http,
        appNamespace,
    );
    var storagePasswords = service.storagePasswords();
    var creds = [];
    let url_key = "";
    var response = storagePasswords.fetch(
        function (err, storagePasswords) {
            if (err) { console.warn(err); }
            else {
                response = storagePasswords.list();
                console.log(response)
                var my_list = [];
                for (var i = 0; i < response.length; i++) {
                    var uname = ""
                    var api_key = ""
                    if (response[i]["_acl"]["app"] == "TA-eclecticiq") {
                        uname = "eiq"
                        api_key = response[i]["_properties"]["clear_password"];
                        var temp = {};
                        temp[uname] = api_key;
                        my_list.push(temp);
                        break
                    }
                }
                localStorage.setItem("response", JSON.stringify(my_list))
            }
        });
    var creds = JSON.parse(localStorage.getItem("response"))
    localStorage.removeItem("response")
    console.log(creds)

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
    $("#setup_button").attr('disabled', 'disabled');

    // Value of password_input from setup_page_dashboard.xml
    const sighting_value = $('#sighting_value').val();
    const sighting_desc = $('#sighting_desc').val();
    const sighting_title = $('#sighting_title').val();
    const sighting_tags = $('#sighting_title').val();
    // taking value from the drop down
    var sighting_type_obj = document.getElementById("sighting_type");
    var sighting_type = sighting_type_obj.options[sighting_type_obj.selectedIndex].text;

    var confidence_level_obj = document.getElementById("confidence_level");
    var confidence_level = confidence_level_obj.options[confidence_level_obj.selectedIndex].text;

    const data = {}
    data["sighting_value"]=sighting_value
    data["sighting_desc"]=sighting_desc
    data["sighting_title"]=sighting_title
    data["sighting_tags"]=sighting_tags
    data['confidence_level']=confidence_level
    data['sighting_type']=sighting_type
    // data['creds']=JSON.parse('{"creds":creds}')
    // data['creds']=JSON.parse("[creds]");
    
    try{sighting_title 
        response =  makeRequest('/services/create_sighting', data);
        await response;
        
        }catch(e){
                console.log(e)
        }
        // if (!existingsighting) { 
        //     sighting.create(
        //         {
        //             sighting_value: sighting_valuetosave,
        //             sighting_desc: sighting_desctosave,
        //             sighting_title: sighting_titletosave,
        //             sighting_tags: sighting_tagstosave,
        //             Confidence_level:confidence_leveltosave,
        //             sighting_type: sighting_typetosave

        //         });
        //     $('#msg').html("Sighting created! View: https://ic-playground.eclecticiq.com/api/beta/sources/9a479225-37d1-4dae-9554-172eeccea193");
        //     }
    
    }
})

           