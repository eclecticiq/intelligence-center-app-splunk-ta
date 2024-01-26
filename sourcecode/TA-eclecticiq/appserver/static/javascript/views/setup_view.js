"use strict";

function promisify(f, manyArgs = false) {
  return function (...args) {
    return new Promise((resolve, reject) => {
      function callback(err, ...results) { // our custom callback for f
        if (err) {
          reject(err);
        } else {
          // resolve with all callback results if manyArgs is specified
          resolve(manyArgs ? results : results[0]);
        }
      }

      args.push(callback);

      f.call(this, ...args);
    });
  };
}

define(
    ["backbone", "jquery", "splunkjs/splunk"],
    function(Backbone, jquery, splunk_js_sdk) {
        sdk = splunk_js_sdk;
        var View = Backbone.View.extend({
            // -----------------------------------------------------------------
            // Backbon Functions, These are specific to the Backbone library
            // -----------------------------------------------------------------
            initialize: function initialize() {
                Backbone.View.prototype.initialize.apply(this, arguments);
            },

            events: {
                "click .setup_button": "trigger_setup",
            },

            render: async function() {
                this.el.innerHTML = this.get_template();

                var app_name = "TA-eclecticiq";

                var application_name_space = {
                    owner: "nobody",
                    app: app_name,
                    sharing: "app",
                };

                var splunk_js_sdk_service = this.create_splunk_js_sdk_service(
                        splunk_js_sdk,
                        application_name_space,
                    );

                var splunk_js_sdk_service_configurations = splunk_js_sdk_service.configurations(
                    {
                        // Name space information not provided
                    },
                );

                await splunk_js_sdk_service_configurations.fetch();

                var configuration_file_accessor = this.get_configuration_file(
                    splunk_js_sdk_service_configurations,
                    "ta-eclecticiq",
                );
                await configuration_file_accessor.fetch();

                var config_list = configuration_file_accessor.item("main").properties();

                $("input[name='eiq_version']").val(config_list["eiq_version"]);

                $("input[name='eiq_baseurl']").val(config_list["eiq_baseurl"].substring(8));

                if (config_list["verify-ssl"] == "1") {
                    $("input[name='verify-ssl']").prop('checked', true);}
                else {
                    $("input[name='verify-ssl']").prop('checked', false)
                }

                $("input[name='feedslist']").val(config_list["feedslist"]);

                if (config_list["es_ti_ingest"] == "1") {
                    $("input[name='es_ti_ingest']").prop('checked', true);}
                else {
                    $("input[name='es_ti_ingest']").prop('checked', false)
                }
                
                $("input[name='sourcegroupname']").val(config_list["sourcegroupname"]);
                $("input[name='proxy_ip']").val(config_list["proxy_ip"]);
                $("input[name='proxy_username']").val(config_list["proxy_username"]);
                $("input[name='log_level']").val(config_list["log_level"]);
                $("input[name='sightings_query']").val(config_list["sightings_query"]);

                if (config_list["domain"] == "1") {
                    $("input[name='domain']").prop('checked', true);}
                else {
                    $("input[name='domain']").prop('checked', false)
                }


                if (config_list["hash-md5"] == "1") {
                    $("input[name='hash-md5']").prop('checked', true);}
                else {
                    $("input[name='hash-md5']").prop('checked', false)
                }

                if (config_list["hash-sha1"] == "1") {
                    $("input[name='hash-sha1']").prop('checked', true);}
                else {
                    $("input[name='hash-sha1']").prop('checked', false)
                }

                if (config_list["hash-sha256"] == "1") {
                    $("input[name='hash-sha256']").prop('checked', true);}
                else {
                    $("input[name='hash-sha256']").prop('checked', false)
                }

                if (config_list["hash-sha512"] == "1") {
                    $("input[name='hash-sha512']").prop('checked', true);}
                else {
                    $("input[name='hash-sha512']").prop('checked', false)
                }

                if (config_list["ipv4"] == "1") {
                    $("input[name='ipv4']").prop('checked', true);}
                else {
                    $("input[name='ipv4']").prop('checked', false)
                }

                if (config_list["ipv6"] == "1") {
                    $("input[name='ipv6']").prop('checked', true);}
                else {
                    $("input[name='ipv6']").prop('checked', false)
                }

                if (config_list["uri"] == "1") {
                    $("input[name='uri']").prop('checked', true);}
                else {
                    $("input[name='uri']").prop('checked', false)
                }

                if (config_list["host"] == "1") {
                    $("input[name='host']").prop('checked', true)}
                else {
                    $("input[name='host']").prop('checked', false)
                }



                return this;

            },

            // -----------------------------------------------------------------
            // Custom Functions, These are unrelated to the Backbone functions
            // -----------------------------------------------------------------
            // ----------------------------------
            // Main Setup Logic
            // ----------------------------------
            // This performs some sanity checking and cleanup on the inputs that
            // the user has provided before kicking off main setup process
            trigger_setup: function trigger_setup() {
                // Used to hide the error output, when a setup is retried
                this.display_error_output([]);

                console.log("Triggering setup");

                var text_fields = {"eiq_baseurl":"", "eiq_version":"", "sourcegroupname":"",
                                       "feedslist":"", "proxy_ip":"", "proxy_username":"", "log_level":""};

                var bool_fields = {"verify-ssl":"", "es_ti_ingest":"", "domain":"", "email":"", "hash-md5":"", "hash-sha1":"",
                                       "hash-sha256":"", "hash-sha512":"", "ipv4":"", "ipv6":"", "uri":"", "host":""};

                var item;

                for (item in text_fields) {
                    text_fields[item]=document.getElementsByName(item)[0].value
                }

                for (item in bool_fields) {
                    if (document.getElementsByName(item)[0].checked) {
                        bool_fields[item]="1"}
                    else {
                        bool_fields[item]="0"}
                }

                var fields = {...text_fields, ...bool_fields};

                if (fields["eiq_baseurl"] !== ""){
                    fields["eiq_baseurl"] = "https://" + fields["eiq_baseurl"]
                }


                var eiq_password = jquery("input[name=eiq_password]").val();

                var proxy_password = jquery("input[name=proxy_password]").val();
                var proxy_username = jquery("input[name=proxy_username]").val();

                var sightings_query = jquery("input[name=sightings_query]").val();

                this.perform_setup(
                        splunk_js_sdk,
                        eiq_password,
                        fields,
                    proxy_password,
                    proxy_username,
                    sightings_query
                    );


            },

            // This is where the main setup process occurs
            perform_setup: async function perform_setup(splunk_js_sdk, eiq_password, fields, proxy_password, proxy_username, sightings_query) {
                var app_name = "TA-eclecticiq";

                var application_name_space = {
                    owner: "nobody",
                    app: app_name,
                    sharing: "app",
                };

                var text_properties_to_update = fields;

                var check_box = ["eiq_baseurl", "eiq_version", "sourcegroupname"];

                try {

                var i;
                for (i in check_box) {
                    if (fields[check_box[i]] == "") {
                        throw new Error("Field '"+ check_box[i] + "' was not specified");
                    }
                }


                    // Create the Splunk JS SDK Service object
                    var splunk_js_sdk_service = this.create_splunk_js_sdk_service(
                        splunk_js_sdk,
                        application_name_space,
                    );
                    // Creates the custom configuration file of this Splunk App
                    // All required information for this Splunk App is placed in
                    // there
                    await this.create_custom_configuration_file(
                        splunk_js_sdk_service,
                        text_properties_to_update,
                        "ta-eclecticiq",
                        "main"
                    );

                    // Creates the passwords.conf stanza that is the encryption
                    // of the api_key provided by the user
                    if (eiq_password !== "") {
                       await this.encrypt_api_key(splunk_js_sdk_service, eiq_password, "eiq_user");
                    }
                    else {
                        throw new Error("Field eiq_password was not specified");
                    }

                    if (proxy_password !== "" && proxy_username !== "") {
                        await this.encrypt_api_key(splunk_js_sdk_service, proxy_password, proxy_username);
                    }

                    if (sightings_query !== "") {
                        var update = {"definition": sightings_query}
                        await this.create_custom_configuration_file(
                        splunk_js_sdk_service,
                        update,
                        "macros",
                        "eiq_sightings_search")
                    }

                    // Completes the setup, by access the app.conf's [install]
                    // stanza and then setting the `is_configured` to true
                    await this.complete_setup(splunk_js_sdk_service);

                    // Reloads the splunk app so that splunk is aware of the
                    // updates made to the file system
                    await this.reload_splunk_app(splunk_js_sdk_service, app_name);

                    // Redirect to the Splunk App's home page
                    this.redirect_to_splunk_app_homepage(app_name);

                } catch (error) {
                    // Error output
                    var error_messages_to_display = [];
                    if (
                        error !== null &&
                        typeof error === "object" &&
                        error.hasOwnProperty("responseText")
                    ) {
                        var response_object = JSON.parse(error.responseText);
                        error_messages_to_display = this.extract_error_messages(
                            response_object.messages,
                        );
                    } else {
                        // Assumed to be string
                        error_messages_to_display.push(error);
                    }

                    this.display_error_output(error_messages_to_display);
                    console.log(error_messages_to_display);
                }
            },

            create_custom_configuration_file: async function create_custom_configuration_file(
                splunk_js_sdk_service,
                properties_to_update,
                custom_configuration_file_name,
                stanza_name
            ) {
                var custom_configuration_file_name = custom_configuration_file_name;
                var stanza_name = stanza_name;


                await this.update_configuration_file(
                    splunk_js_sdk_service,
                    custom_configuration_file_name,
                    stanza_name,
                    properties_to_update,
                );
            },

            encrypt_api_key: async function encrypt_api_key(
                splunk_js_sdk_service,
                api_key,
                username,
            ) {
                // /servicesNS/<NAMESPACE_USERNAME>/<SPLUNK_APP_NAME>/storage/passwords/<REALM>%3A<USERNAME>%3A
                var realm = "TA-eclecticiq";
                var username = username;

                var storage_passwords_accessor = splunk_js_sdk_service.storagePasswords(
                    {
                        // No namespace information provided
                    },
                );
                await storage_passwords_accessor.fetch();

                var does_storage_password_exist = this.does_storage_password_exist(
                    storage_passwords_accessor,
                    realm,
                    username,
                );

                if (does_storage_password_exist) {
                    await this.delete_storage_password(
                        storage_passwords_accessor,
                        realm,
                        username,
                    );
                }
                await storage_passwords_accessor.fetch();

                await this.create_storage_password_stanza(
                    storage_passwords_accessor,
                    realm,
                    username,
                    api_key,
                );
            },

            complete_setup: async function complete_setup(splunk_js_sdk_service) {
                var app_name = "TA-eclecticiq";
                var configuration_file_name = "app";
                var stanza_name = "install";
                var properties_to_update = {
                    is_configured: "true",
                };

                await this.update_configuration_file(
                    splunk_js_sdk_service,
                    configuration_file_name,
                    stanza_name,
                    properties_to_update,
                );
            },

            reload_splunk_app: async function reload_splunk_app(
                splunk_js_sdk_service,
                app_name,
            ) {
                var splunk_js_sdk_apps = splunk_js_sdk_service.apps();
                await promisify(splunk_js_sdk_apps.fetch)();

                var current_app = splunk_js_sdk_apps.item(app_name);
                await promisify(current_app.reload)();
            },

            // ----------------------------------
            // Splunk JS SDK Helpers
            // ----------------------------------
            // ---------------------
            // Process Helpers
            // ---------------------
            update_configuration_file: async function update_configuration_file(
                splunk_js_sdk_service,
                configuration_file_name,
                stanza_name,
                properties,
            ) {
                // Retrieve the accessor used to get a configuration file
                var splunk_js_sdk_service_configurations = splunk_js_sdk_service.configurations(
                    {
                        // Name space information not provided
                    },
                );
                await splunk_js_sdk_service_configurations.fetch();

                // Check for the existence of the configuration file being editect
                var does_configuration_file_exist = this.does_configuration_file_exist(
                    splunk_js_sdk_service_configurations,
                    configuration_file_name,
                );

                // If the configuration file doesn't exist, create it
                if (!does_configuration_file_exist) {
                    await this.create_configuration_file(
                        splunk_js_sdk_service_configurations,
                        configuration_file_name,
                    );
                }

                // Retrieves the configuration file accessor
                var configuration_file_accessor = this.get_configuration_file(
                    splunk_js_sdk_service_configurations,
                    configuration_file_name,
                );
                await configuration_file_accessor.fetch();

                // Checks to see if the stanza where the inputs will be
                // stored exist
                var does_stanza_exist = this.does_stanza_exist(
                    configuration_file_accessor,
                    stanza_name,
                );

                // If the configuration stanza doesn't exist, create it
                if (!does_stanza_exist) {
                    await this.create_stanza(configuration_file_accessor, stanza_name);
                }
                // Need to update the information after the creation of the stanza
                await configuration_file_accessor.fetch();

                // Retrieves the configuration stanza accessor
                var configuration_stanza_accessor = this.get_configuration_file_stanza(
                    configuration_file_accessor,
                    stanza_name,
                );
                await configuration_stanza_accessor.fetch();

                // We don't care if the stanza property does or doesn't exist
                // This is because we can use the
                // configurationStanza.update() function to create and
                // change the information of a property
                await this.update_stanza_properties(
                    configuration_stanza_accessor,
                    properties,
                );
            },

            // ---------------------
            // Existence Functions
            // ---------------------
            does_configuration_file_exist: function does_configuration_file_exist(
                configurations_accessor,
                configuration_file_name,
            ) {
                var was_configuration_file_found = false;

                var configuration_files_found = configurations_accessor.list();
                for (var index = 0; index < configuration_files_found.length; index++) {
                    var configuration_file_name_found =
                        configuration_files_found[index].name;
                    if (configuration_file_name_found === configuration_file_name) {
                        was_configuration_file_found = true;
                    }
                }

                return was_configuration_file_found;
            },

            does_stanza_exist: function does_stanza_exist(
                configuration_file_accessor,
                stanza_name,
            ) {
                var was_stanza_found = false;

                var stanzas_found = configuration_file_accessor.list();
                for (var index = 0; index < stanzas_found.length; index++) {
                    var stanza_found = stanzas_found[index].name;
                    if (stanza_found === stanza_name) {
                        was_stanza_found = true;
                    }
                }

                return was_stanza_found;
            },

            does_stanza_property_exist: function does_stanza_property_exist(
                configuration_stanza_accessor,
                property_name,
            ) {
                var was_property_found = false;

                for (const [key, value] of Object.entries(
                    configuration_stanza_accessor.properties(),
                )) {
                    if (key === property_name) {
                        was_property_found = true;
                    }
                }

                return was_property_found;
            },

            does_storage_password_exist: function does_storage_password_exist(
                storage_passwords_accessor,
                realm_name,
                username,
            ) {
                var storage_passwords = storage_passwords_accessor.list();
                var storage_passwords_found = [];

                var i;
                var check = false;

                for (i in storage_passwords) {
                    var storage_password = storage_passwords[i]["name"];
                    var compare_password = realm_name + ":" + username +":"
                    if (storage_password===compare_password) {
                        check = true
                    }
                }
                return check;
            },

            // ---------------------
            // Retrieval Functions
            // ---------------------
            get_configuration_file: function configuration_file_accessor(
                configurations_accessor,
                configuration_file_name,
            ) {
                var configuration_file_accessor = configurations_accessor.item(
                    configuration_file_name,
                    {
                        // Name space information not provided
                    },
                );

                return configuration_file_accessor;
            },

            get_configuration_file_stanza: function get_configuration_file_stanza(
                configuration_file_accessor,
                configuration_stanza_name,
            ) {
                var configuration_stanza_accessor = configuration_file_accessor.item(
                    configuration_stanza_name,
                    {
                        // Name space information not provided
                    },
                );

                return configuration_stanza_accessor;
            },

            get_configuration_file_stanza_property: function get_configuration_file_stanza_property(
                configuration_file_accessor,
                configuration_file_name,
            ) {
                return null;
            },

            // ---------------------
            // Creation Functions
            // ---------------------
            create_splunk_js_sdk_service: function create_splunk_js_sdk_service(
                splunk_js_sdk,
                application_name_space,
            ) {
                var http = new splunk_js_sdk.SplunkWebHttp();

                var splunk_js_sdk_service = new splunk_js_sdk.Service(
                    http,
                    application_name_space,
                );

                return splunk_js_sdk_service;
            },

            create_configuration_file: function create_configuration_file(
                configurations_accessor,
                configuration_file_name,
            ) {
                var parent_context = this;

                return configurations_accessor.create(configuration_file_name, function(
                    error_response,
                    created_file,
                ) {
                    // Do nothing
                });
            },

            create_stanza: function create_stanza(
                configuration_file_accessor,
                new_stanza_name,
            ) {
                var parent_context = this;

                return configuration_file_accessor.create(new_stanza_name, function(
                    error_response,
                    created_stanza,
                ) {
                    // Do nothing
                });
            },

            update_stanza_properties: function update_stanza_properties(
                configuration_stanza_accessor,
                new_stanza_properties,
            ) {
                var parent_context = this;

                return configuration_stanza_accessor.update(
                    new_stanza_properties,
                    function(error_response, entity) {
                        // Do nothing
                    },
                );
            },

            create_storage_password_stanza: function create_storage_password_stanza(
                splunk_js_sdk_service_storage_passwords,
                realm,
                username,
                value_to_encrypt,
            ) {
                var parent_context = this;

                return splunk_js_sdk_service_storage_passwords.create(
                    {
                        name: username,
                        password: value_to_encrypt,
                        realm: realm,
                    },
                    function(error_response, response) {
                        // Do nothing
                    },
                );
            },

            // ----------------------------------
            // Deletion Methods
            // ----------------------------------
            delete_storage_password: function delete_storage_password(
                storage_passwords_accessor,
                realm,
                username,
            ) {
                    return storage_passwords_accessor.del(realm + ":" + username + ":");



            },

            // ----------------------------------
            // Input Cleaning and Checking
            // ----------------------------------
            sanitize_string: function sanitize_string(string_to_sanitize) {
                let sanitized_string = string_to_sanitize.trim();

                return sanitized_string;
            },

            validate_api_url_input: function validate_api_url_input(hostname) {
                var error_messages = [];

                var is_string_empty = typeof hostname === "undefined" || hostname === "";
                var does_string_start_with_http_protocol = hostname.startsWith("http://");
                var does_string_start_with_https_protocol = hostname.startsWith(
                    "https://",
                );

                if (is_string_empty) {
                    var error_message =
                        "The `API URL` specified was empty. Please provide" + " a value.";
                    error_messages.push(error_message);
                }
                if (does_string_start_with_http_protocol) {
                    var error_message =
                        "The `API URL` specified is using `http://` at the" +
                        " beginning of it. Please remove the `http://` and" +
                        " enter the url with out it in `API URL` field.";
                    error_messages.push(error_message);
                }
                if (does_string_start_with_https_protocol) {
                    var error_message =
                        "The `API URL` specified is using `https://` at the" +
                        " beginning of it. Please remove the `https://` and" +
                        " enter the url with out it in `API URL` field.";
                    error_messages.push(error_message);
                }

                return error_messages;
            },

            validate_api_key_input: function validate_api_key_input(api_key) {
                var error_messages = [];

                var is_string_empty = typeof api_key === "undefined" || api_key === "";

                if (is_string_empty) {
                    var error_message =
                        "The `API Key` specified was empty. Please provide" + " a value.";
                    error_messages.push(error_message);
                }

                return error_messages;
            },

            validate_inputs: function validate_inputs(hostname, api_key) {
                var error_messages = [];

                var api_url_errors = this.validate_api_url_input(hostname);
                var api_key_errors = this.validate_api_key_input(api_key);

                error_messages = error_messages.concat(api_url_errors);
                error_messages = error_messages.concat(api_key_errors);

                return error_messages;
            },

            // ----------------------------------
            // GUI Helpers
            // ----------------------------------
            extract_error_messages: function extract_error_messages(error_messages) {
                // A helper function to extract error messages

                // Expects an array of messages
                // [
                //     {
                //         type: the_specific_error_type_found,
                //         text: the_specific_reason_for_the_error,
                //     },
                //     ...
                // ]

                var error_messages_to_display = [];
                for (var index = 0; index < error_messages.length; index++) {
                    var error_message = error_messages[index];
                    var error_message_to_display =
                        error_message.type + ": " + error_message.text;
                    error_messages_to_display.push(error_message_to_display);
                }

                return error_messages_to_display;
            },

            redirect_to_splunk_app_homepage: function redirect_to_splunk_app_homepage(
                app_name,
            ) {
                var redirect_url = "/app/" + app_name;

                window.location.href = redirect_url;
            },

            // ----------------------------------
            // Display Functions
            // ----------------------------------
            display_error_output: function display_error_output(error_messages) {
                // Hides the element if no messages, shows if any messages exist
                var did_error_messages_occur = error_messages.length > 0;

                var error_output_element = jquery(".setup.container .error.output");

                if (did_error_messages_occur) {
                    var new_error_output_string = "";
                    new_error_output_string += "<ul>";
                    for (var index = 0; index < error_messages.length; index++) {
                        new_error_output_string +=
                            "<li>" + error_messages[index] + "</li>";
                    }
                    new_error_output_string += "</ul>";

                    error_output_element.html(new_error_output_string);
                    error_output_element.stop();
                    error_output_element.fadeIn();
                } else {
                    error_output_element.stop();
                    error_output_element.fadeOut({
                        complete: function() {
                            error_output_element.html("");
                        },
                    });
                }
            },

            get_template: function get_template() {
                var template_string =
                    "<div class='title'>" +
                    "    <h1>EclecticIQ Intelligence Center App Configuration Page</h1>" +
                    "</div>" +
                    "<div class='setup container'>" +
                    "    <div class='left'>" +
                    "         <b>EclecticIQ Customers:</b> If you need assistance completing the form please contact \
                                 <a href='support.eclecticiq.com' target='_blank'>support.eclecticiq.com</a>" +
                    "         <br/>" +

                    "        <h2>Setup Properties</h2>" +
                    "        <div class='field api_url'>" +
                    "            <div class='title'>" +
                    "                <div>" +
                    "                    <h3>Feed Setup:</h3>" +
                    "                    EclecticIQ Intelligence Center url:" +
                    "                </div>" +
                    "            </div>" +
                    "            <div class='user_input'>" +
                    "                <div class='protocol'>" +
                    "                    https://" +
                    "                </div>" +
                    "                <div class='url_input'>" +
                    "                    <input type='text' name='eiq_baseurl' placeholder='eclecticiq-platform.com'>" +
                    "                </div>" +
                    "            </div>" +
                    "        </div>" +

                    "       <div class='title'>" +
                    "           EclecticIQ Intelligence Center API Version:" +
                    "       </div>" +
                    "           <div class='text_input'>" +
                    "               <input type='text' name='eiq_version' placeholder='v1'>" +
                    "       </div>" +

                    "       <div class='user_input'>" +
                    "           <input type='checkbox' name='verify-ssl'>  Verify the SSL Connection" +
                    "       </div>"+
                    "       <br/>" +

                    "       <div class='title'>" +
                    "           ID of feeds for collection from EclecticIQ Platform:" +
                    "       </div>" +
                    "       <div class='text_input'>" +
                    "            <input type='text' name='feedslist' placeholder='6,8'>" +
                    "       </div>" +

                    "        <div class='title'>" +
                    "            Ingest data into Splunk Enterprise Security Threat Intel Framework:" +
                    "        </div>" +
                    "       <div class='user_input'>" +
                    "           <input type='checkbox' name='es_ti_ingest'> Yes " +
                    "       </div>"+
                    "         <br/>" +
                    "       <div class='title'>" +
                    "           EclecticIQ Intelligence Center Source Group:" +
                    "       </div>" +
                    "       <div class='text_input'>" +
                    "            <input type='text' name='sourcegroupname' placeholder='Source Group'>" +
                    "       </div>" +

                    "       <div class='title'>" +
                    "            <h3>Credentials</h3>" +
                    "       </div>" +

                    "       <div class='title'>" +
                    "            EclecticIQ Intelligence Center API Token:" +
                    "       </div>" +
                    "       <div class='text_input'>" +
                    "            <input type='password' name='eiq_password'>" +
                    "       </div>" +

                    "        <div>" +
                    "            <button name='setup_button' class='setup_button'>" +
                    "                Save Settings" +
                    "            </button>" +
                    "        </div>" +
                    "        <br/>" +
                    "        <div class='error output'>" +
                    "        </div>" +
                    "    </div>" +


                    "    <div class='right'>" +
                    "      <h2>Optional Details</h2>" +
                    "        <div class='title'>" +
                    "            <h3>Proxy</h3>" +
                    "        </div>" +
                    "        If you're using proxy please provide it's IP:port, username and password below." +


                    "       <div class='title'>" +
                    "       <br/>" +
                    "           Proxy IP:" +
                    "       </div>" +
                    "       <div class='text_input'>" +
                    "            <input type='text' name='proxy_ip' '>" +
                    "       </div>" +

                    "       <div class='title'>" +
                    "           Proxy username:" +
                    "       </div>" +
                    "       <div class='text_input'>" +
                    "            <input type='text' name='proxy_username' >" +
                    "       </div>" +

                    "       <div class='title'>" +
                    "            Proxy password:" +
                    "       </div>" +
                    "       <div class='text_input'>" +
                    "            <input type='password' name='proxy_password'>" +
                    "       </div>" +


                    "        <div class='title'>" +
                    "            <h3>Indexes setup</h3>" +
                    "        </div>" +
                    "        Look for sightings with the below query, you can change this later via the \"eiq_sightings_search\" macro." +

                    "       <div class='title'>" +
                    "        <br/>" +
                    "           Sightings query:" +
                    "       </div>" +
                    "       <div class='text_input'>" +
                    "            <input type='text' name='sightings_query' placeholder='index=main' >" +
                    "       </div>" +


                    "        <div class='title'>" +
                    "            <h3>Send the following sightings types</h3>" +
                    "        </div>" +
                    "        Only by following types sightings will be created" +

                    "       <div class='user_input'>" +
                    "           <input type='checkbox' name='ipv4' checked='checked'> ipv4 " +
                    "           <input type='checkbox' name='ipv6' checked='checked'> ipv6 " +
                    "           <input type='checkbox' name='domain' checked='checked'> domains " +
                    "           <input type='checkbox' name='host' checked='checked'> host " +
                    "           <input type='checkbox' name='uri' checked='checked'> uri " +
                    "       </div>"+
                    "       <div class='user_input'>" +
                    "           <input type='checkbox' name='hash-md5' checked='checked'> hash-md5 " +
                    "           <input type='checkbox' name='hash-sha1' checked='checked'> hash-sha1 " +
                    "           <input type='checkbox' name='hash-sha256' checked='checked'> hash-sha256 " +
                    "           <input type='checkbox' name='hash-sha512' checked='checked'> hash-sha512 " +
                    "           <input type='checkbox' name='email' checked='checked'> emails " +
                    "       </div>"+

                    "        <div class='title'>" +
                    "            <h3>Set script log level</h3>" +
                    "        </div>" +
                    "        Set the log level for all the scripts in the app" +

                    "       <div class='title'>" +
                    "        <br/>" +
                    "           Scripts Log Level:" +
                    "       </div>" +
                    "       <div class='text_input'>" +
                    "            <input type='text' name='log_level' placeholder='20'>" +
                    "       </div>" +
                    "0=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL"


                    "    </div>" +
                    "</div>";


                return template_string;
            },
        }); // End of class declaration

        return View;
    }, // End of require asynchronous module definition function
); // End of require statement
