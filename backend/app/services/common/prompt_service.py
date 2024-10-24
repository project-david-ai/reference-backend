class PromptService:
    def __init__(self, name=None):
        self.builder_username = 'thanos'
        self.name = name

    def drone_prompt_sumarise_message(self, data):
        prompt = f"succinctly summarise: '{data}' with a human readable string . No introduction, give the summary in one shot."
        return prompt

    def sentinel_drone_prompt_address_error(self, error_message):
        prompt = f"Produce a succinct, easily read report for the error that you are observing for the eyes of attending Engineers of any level.\n\nError: {error_message}\n\nEndeavour to draft code to and or next steps to ameliorate as per your instructions. Note the time and date."
        return prompt