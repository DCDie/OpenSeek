class Response:
    def __init__(
        self,
        text: str,
        chat_id: str | None = None,
        deepthink_duration: int | None = None,
        deepthink_content: str | None = None,
        search_results: list | None = None,
    ):
        """
        Response object to store the response from the DeepSeek API.

        Args:
        ----------
            text (str): The response text.
            chat_id (Optional[str], optional): The chat ID. Defaults to None.
            deepthink_duration (Optional[int], optional): The deepthink duration. Defaults to None.
            deepthink_content (Optional[str], optional): The deepthink content. Defaults to None.
            search_results (Optional[list], optional): The search results. Defaults to None.
        """
        self.text = text
        self.chat_id = chat_id
        self.deepthink_duration = deepthink_duration
        self.deepthink_content = deepthink_content
        self.search_results = search_results

    def __repr__(self):
        return self.text
