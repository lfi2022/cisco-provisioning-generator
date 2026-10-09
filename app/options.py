# A model registry keeps the web/UI layer independent from any PBX and makes it
# possible to add another vendor or Cisco family without changing persistence.
PHONE_MODELS = {
    "CP-7841": {"label": "Cisco CP-7841 Enterprise", "button_count": 4},
}

# These fields have historically appeared directly below <device> in Enterprise
# configuration examples.  Their firmware support is deliberately not claimed.
EXPERIMENTAL_DEVICE_FIELDS = [
    "fullConfig", "allowAutoConfig", "redirectEnable", "echoMultiEnable",
    "ipAddressMode", "ipPreferenceModeControl", "ipMediaAddressFamilyPreference",
    "dadEnable",
]

OPTION_GROUPS = {
    "identity": {
        "title": "Identité / affichage",
        "fields": [
            ("phone_label", "Label du téléphone", "text", "Bureau"),
            ("device_protocol", "Protocole appareil", "select", "SIP", ["SIP"]),
            ("date_template", "Format date", "text", "D/M/YY"),
            ("time_zone", "Fuseau Cisco", "text", "Central Europe Standard/Daylight Time"),
            ("language_name", "Nom langue", "text", "French_France"),
            ("language_code", "Code langue", "text", "fr_FR"),
            ("network_locale", "Locale réseau", "text", "Belgium"),
            ("load_information", "Firmware / loadInformation", "text", ""),
        ],
    },
    "network": {
        "title": "Réseau / provisioning",
        "fields": [
            ("pbx_host", "Serveur SIP / processNodeName", "text", "10.0.210.2"),
            ("sip_port", "Port SIP", "number", "5060"),
            ("secured_sip_port", "Port SIP TLS", "number", "5061"),
            ("ethernet_phone_port", "Port SCCP/ethernetPhonePort", "number", "2000"),
            ("ntp_primary", "NTP primaire", "text", "pool.ntp.org"),
            ("ntp_secondary", "NTP secondaire", "text", ""),
            ("ntp_mode", "Mode NTP", "select", "Unicast", ["Unicast", "DirectedBroadcast"]),
            ("voice_vlan_access", "Voice VLAN Access", "select", "1", ["0", "1"]),
            ("pc_port", "Port PC", "select", "0", ["0", "1"]),
            ("span_to_pc_port", "SPAN vers port PC", "select", "1", ["0", "1"]),
            ("web_access", "Accès web (0=activé Cisco Enterprise)", "select", "0", ["0", "1"]),
            ("ssh_access", "Accès SSH", "select", "0", ["0", "1"]),
            ("ssh_user", "Utilisateur SSH", "text", "admin"),
            ("ssh_password", "Mot de passe SSH", "password", "admin"),
            ("settings_access", "Settings Access", "select", "1", ["0", "1"]),
            ("garp_enable", "GARP", "select", "1", ["0", "1"]),
            ("lldp_asset_id", "LLDP Asset ID", "text", ""),
        ],
    },
    "sip": {
        "title": "SIP global",
        "fields": [
            ("register_with_proxy", "REGISTER auprès du proxy", "select", "true", ["true", "false"]),
            ("backup_proxy", "Proxy secours", "text", ""),
            ("backup_proxy_port", "Port proxy secours", "number", "5060"),
            ("emergency_proxy", "Proxy urgence", "text", ""),
            ("emergency_proxy_port", "Port proxy urgence", "number", "5060"),
            ("outbound_proxy", "Outbound proxy", "text", ""),
            ("outbound_proxy_port", "Port outbound proxy", "number", "5060"),
            ("timer_register_expires", "Expiration REGISTER", "number", "300"),
            ("timer_invite_expires", "Expiration INVITE", "number", "180"),
            ("sip_invite_retx", "Réessais INVITE", "number", "6"),
            ("sip_retx", "Réessais SIP", "number", "10"),
            ("preferred_codec", "Codec préféré", "select", "g711alaw", ["g711alaw", "g711ulaw", "g722", "g729", "ilbc"]),
            ("dtmf_avt_payload", "Payload DTMF RFC2833", "number", "101"),
            ("dscp_for_audio", "DSCP audio", "number", "184"),
            ("dscp_for_call_control", "DSCP signalisation", "number", "96"),
            ("rfc2543_hold", "RFC2543 Hold", "select", "false", ["true", "false"]),
            ("semi_attended_transfer", "Semi-attended transfer", "select", "true", ["true", "false"]),
            ("anonymous_call_block", "Blocage appels anonymes", "select", "0", ["0", "1"]),
            ("caller_id_blocking", "Masquage Caller ID", "select", "0", ["0", "1"]),
        ],
    },
    "features": {
        "title": "Fonctions d'appel",
        "fields": [
            ("cnf_join_enabled", "Conference Join", "select", "true", ["true", "false"]),
            ("call_forward_uri", "URI renvoi", "text", "x-cisco-serviceuri-cfwdall"),
            ("call_pickup_uri", "URI pickup", "text", "x-cisco-serviceuri-pickup"),
            ("call_pickup_list_uri", "URI other pickup", "text", "x-cisco-serviceuri-opickup"),
            ("call_pickup_group_uri", "URI group pickup", "text", "x-cisco-serviceuri-gpickup"),
            ("meetme_uri", "URI MeetMe", "text", "x-cisco-serviceuri-meetme"),
            ("abbr_dial_uri", "URI abbreviated dial", "text", "x-cisco-serviceuri-abbrdial"),
            ("call_log_blf_enabled", "BLF dans journal", "select", "2", ["0", "1", "2"]),
            ("phone_password", "Mot de passe menu admin", "password", "456"),
            ("logging_display", "Logging display", "select", "1", ["0", "1"]),
            ("disable_speaker", "Désactiver haut-parleur", "select", "false", ["false", "true"]),
            ("disable_speaker_headset", "Désactiver HP + casque", "select", "false", ["false", "true"]),
        ],
    },
    "urls": {
        "title": "Services / URLs",
        "fields": [
            ("directory_url", "Directory URL", "text", ""),
            ("services_url", "Services URL", "text", ""),
            ("information_url", "Information URL", "text", ""),
            ("messages_url", "Messages URL", "text", ""),
            ("authentication_url", "Authentication URL", "text", ""),
            ("idle_url", "Idle URL", "text", ""),
            ("idle_timeout", "Idle timeout", "number", "0"),
            ("proxy_server_url", "Proxy server URL", "text", ""),
            ("dial_template", "Dial template", "text", "dialplan.xml"),
            ("softkey_file", "Softkey file", "text", ""),
            ("feature_policy_file", "Feature policy file", "text", ""),
        ],
    },
}

BUTTON_TYPES = [
    ("unused", "Libre"),
    ("line", "Ligne SIP"),
    ("blf", "BLF / Speed dial"),
    ("speeddial", "Speed dial simple"),
]

EXPERIMENTAL_FIELDS = [
    "fullConfig", "allowAutoConfig", "redirectEnable", "echoMultiEnable",
    "ipAddressMode", "ipPreferenceModeControl", "ipMediaAddressFamilyPreference",
    "dadEnable", "advertiseG722Codec", "kpml", "natEnabled", "natAddress",
    "enableVad", "preferredCodec", "dtmfAvtPayload", "startMediaPort",
    "stopMediaPort", "joinAcrossLines", "autoSelectLineEnable",
    "autoCallSelect", "alwaysUsePrimeLine", "alwaysUsePrimeLineVoiceMail",
    "g722CodecSupport", "headsetWidebandUIControl", "handsetWidebandUIControl",
    "speakerWidebandUIControl", "daysDisplayNotActive", "displayOnTime",
    "displayOnDuration", "displayIdleTimeout", "displayOnWhenIncomingCall",
    "webProtocol", "sshPort", "cdpEnable", "lldpEnable", "lldpPowerPriority",
    "detectCMConnectionFailure", "peerFirmwareSharing",
]
