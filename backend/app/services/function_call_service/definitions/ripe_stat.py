# open_ai_function_call_definitions.py

ripe_stats_functions = [
    {
        "type": "function",
        "function": {
            "name": "getAnnouncedPrefixes",
            "description": "Retrieves the announced prefixes for a given ASN",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The ASN for which to retrieve the announced prefixes"
                    },
                    "starttime": {
                        "type": "string",
                        "description": "The start time for the query (ISO8601 or Unix timestamp)"
                    },
                    "endtime": {
                        "type": "string",
                        "description": "The end time for the query (ISO8601 or Unix timestamp)"
                    },
                    "min_peers_seeing": {
                        "type": "integer",
                        "description": "Minimum number of RIS peers seeing the prefix for it to be included in the results"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getAbuseContacts",
            "description": "Retrieves abuse contact information for a given IP resource",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The IP prefix or range for which to retrieve abuse contact information (e.g., '193.0.0.0/21')"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getAddressSpaceUsage",
            "description": "Retrieves the address space usage for a given IP resource",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The IP prefix or range for which to retrieve the address space usage (e.g., '193.0.0.0/23')"
                    },
                    "all_level_more_specifics": {
                        "type": "boolean",
                        "description": "Indicates whether to return all levels (True) or only the first level (False) of more-specific resources"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getAllocationHistory",
            "description": "Retrieves the allocation history for a given resource",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The prefix, IP range, or ASN for which to retrieve the allocation history"
                    },
                    "starttime": {
                        "type": "string",
                        "description": "The start time for the query (ISO8601 or Unix timestamp)"
                    },
                    "endtime": {
                        "type": "string",
                        "description": "The end time for the query (ISO8601 or Unix timestamp)"
                    }
                },
                "required": ["resource", "starttime"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getAsnNeighbours",
            "description": "Retrieves the neighbours for a given ASN",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The ASN for which to retrieve the neighbours"
                    },
                    "starttime": {
                        "type": "string",
                        "description": "The start time for the query (ISO8601 or Unix timestamp)"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getAtlasProbes",
            "description": "Retrieves the Atlas probes for a given resource",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The prefix, network (ASN), or country for which to retrieve the Atlas probes"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getBgpUpdates",
            "description": "Retrieves the BGP updates for a given resource",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The prefix, IP address, AS, or a list of valid comma-separated resources for which to retrieve the BGP updates"
                    },
                    "starttime": {
                        "type": "string",
                        "description": "The start time for the query (ISO8601 or Unix timestamp)"
                    },
                    "endtime": {
                        "type": "string",
                        "description": "The end time for the query (ISO8601 or Unix timestamp)"
                    },
                    "rrcs": {
                        "type": "string",
                        "description": "The list of Route Collectors (RRCs) to get the results from (single value or comma-separated values)"
                    },
                    "unix_timestamps": {
                        "type": "boolean",
                        "description": "Indicates whether to format the timestamps in the result as Unix timestamps"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getAsnNeighboursHistory",
            "description": "Retrieves the neighbours history for a given ASN",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The ASN for which to retrieve the neighbours history"
                    },
                    "starttime": {
                        "type": "string",
                        "description": "The start time for the query (ISO8601 or Unix timestamp)"
                    },
                    "endtime": {
                        "type": "string",
                        "description": "The end time for the query (ISO8601 or Unix timestamp)"
                    },
                    "max_rows": {
                        "type": "integer",
                        "description": "The maximum number of neighbours to include in the result"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getCountryResourceStats",
            "description": "Retrieves the resource statistics for a given country",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The 2-digit ISO-3166 country code (e.g., 'at', 'de')"
                    },
                    "starttime": {
                        "type": "string",
                        "description": "The start time for the query (ISO8601 or Unix timestamp)"
                    },
                    "endtime": {
                        "type": "string",
                        "description": "The end time for the query (ISO8601 or Unix timestamp)"
                    },
                    "resolution": {
                        "type": "string",
                        "description": "The resolution for the data ('5m', '1h', '1d', '1w')"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getCountryResourceList",
            "description": "Retrieves the list of resources associated with a given country",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The 2-digit ISO-3166 country code (e.g., 'at', 'de')"
                    },
                    "time": {
                        "type": "string",
                        "description": "The time to query (ISO8601 or Unix timestamp)"
                    },
                    "v4_format": {
                        "type": "string",
                        "description": "The formatting for the output of IPv4 space ('prefix' or '')"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getDnsChain",
            "description": "Retrieves the recursive chain of DNS forward and reverse records for a given hostname or IP address",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The hostname or IP address (IPv4 or IPv6)"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getExampleResources",
            "description": "Retrieves example resources for ASN, IPv4, and IPv6",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getHistoricalWhois",
            "description": "Retrieves historical whois information for a given resource",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The resource to query (prefix, AS number, or object type and key)"
                    },
                    "version": {
                        "type": "string",
                        "description": "The version to load details for (numerical value or time-based value)"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getRoutingHistory",
            "description": "Retrieves the routing history for a given resource",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The prefix, IP address, or AS number"
                    },
                    "starttime": {
                        "type": "string",
                        "description": "The start time for the query (ISO8601 or Unix timestamp)"
                    },
                    "endtime": {
                        "type": "string",
                        "description": "The end time for the query (ISO8601 or Unix timestamp)"
                    },
                    "min_peers": {
                        "type": "integer",
                        "description": "The minimum number of full-feed RIS peers seeing the route for the segment to be included"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getRoutingStatus",
            "description": "Retrieves the current routing status for a given resource",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The prefix, IP address, or AS number"
                    },
                    "timestamp": {
                        "type": "string",
                        "description": "The time for the lookup (ISO8601 or Unix timestamp)"
                    },
                    "min_peers_seeing": {
                        "type": "integer",
                        "description": "The minimum number of peers seeing the route for it to be included"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getRrcInfo",
            "description": "Retrieves information about the collector nodes (RRCs) of the RIS network",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getRpkiValidationStatus",
            "description": "Retrieves the RPKI validation status for a combination of prefix and Autonomous System",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The ASN used to perform the RPKI validity state lookup"
                    },
                    "prefix": {
                        "type": "string",
                        "description": "The prefix or comma-separated list of prefixes to perform the RPKI validity state lookup"
                    }
                },
                "required": ["resource", "prefix"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getRpkiHistory",
            "description": "Retrieves a timeseries with the count of VRPs (Validated ROA Payload) for the requested resource",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The prefix, ASN, 2-digit ISO-3166 country code, or trust anchor to query for"
                    },
                    "family": {
                        "type": "integer",
                        "description": "The IP address family to filter for (4 or 6)"
                    },
                    "resolution": {
                        "type": "string",
                        "description": "The time bin to group the result by ('d', 'w', 'm', 'y')"
                    },
                    "delegated": {
                        "type": "boolean",
                        "description": "Indicates whether to include registration information for the resource"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getSearchcomplete",
            "description": "Retrieves example resources that are directly or indirectly related to the given input",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The term that should be tried to be matched against resources"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "The maximum number of suggestions to return per category"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getLookingGlass",
            "description": "Retrieves Looking Glass information for a given resource",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The prefix or IP range to retrieve Looking Glass information for"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getWhatsMyIp",
            "description": "Retrieves the IP address of the requestor",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getZonemasterOverview",
            "description": "Retrieves Zonemaster overview information for a given resource",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The hostname to retrieve Zonemaster overview information for"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getZonemasterDetails",
            "description": "Retrieves Zonemaster details for a given test ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The ID of the Zonemaster test to retrieve details for"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getMlabBandwidth",
            "description": "Retrieves the measured network bandwidths for a given resource",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The IPv4 prefix, IPv4 address, or 2-digit ISO-3166 country code to retrieve bandwidth measurements for"
                    },
                    "starttime": {
                        "type": "string",
                        "description": "The start time for the query (ISO8601 or Unix timestamp)"
                    },
                    "endtime": {
                        "type": "string",
                        "description": "The end time for the query (ISO8601 or Unix timestamp)"
                    }
                },
                "required": ["resource"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getMlabClients",
            "description": "Retrieves the hosts within a certain resource for which network tests occurred",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "The IPv4 prefix, IPv4 address, or 2-digit ISO-3166 country code to retrieve client information for"
                    },
                    "starttime": {
                        "type": "string",
                        "description": "The start time for the query (ISO8601 or Unix timestamp)"
                    },
                    "endtime": {
                        "type": "string",
                        "description": "The end time for the query (ISO8601 or Unix timestamp)"
                    }
                },
                "required": ["resource"]
            }
        }
    }

]

