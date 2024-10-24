# ons_ai_data_function_call_definitions.py

ons_data_functions = [
    {
        "type": "function",
        "function": {
            "name": "getWellbeingByLocalAuthorityData",
            "description": "Retrieves wellbeing data by local authority",
            "parameters": {
                "type": "object",
                "properties": {
                    "dimensions": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "The dimensions to include in the response (e.g., 'time', 'geography', 'estimate', 'measureofwellbeing'). If not provided, all dimensions will be included."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getSexualOrientationByAgeAndSexData",
            "description": "Retrieves sexual orientation data by age and sex",
            "parameters": {
                "type": "object",
                "properties": {
                    "dimensions": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "The dimensions to include in the response (e.g., 'time', 'age', 'sex', 'sexualorientation'). If not provided, all dimensions will be included."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getRetailSalesAllBusinessesData",
            "description": "Retrieves retail sales data for all businesses",
            "parameters": {
                "type": "object",
                "properties": {
                    "dimensions": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "The dimensions to include in the response (e.g., 'time', 'geography', 'unofficialstandardindustrialclassification', 'prices', 'seasonaladjustment'). If not provided, all dimensions will be included."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getTaxBenefitsStatisticsData",
            "description": "Retrieves tax benefits statistics data",
            "parameters": {
                "type": "object",
                "properties": {
                    "dimensions": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "The dimensions to include in the response (e.g., 'time', 'geography', 'quintile', 'averagesandpercentiles', 'income', 'deflation'). If not provided, all dimensions will be included."
                    }
                },
                "required": []
            }
        }
    }
]