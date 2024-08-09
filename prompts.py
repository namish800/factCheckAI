CLAIM_EXTRACTOR_PROMPT = """
        As an expert in analyzing text for underlying assumptions, your task is to identify and articulate the key assumptions in a given user query.
        Instructions:
        Carefully read the user query provided.
        Identify and list the foundational assumptions that the query is based on.
        Keep your responses concise and specific to each assumption identified.
        Do not include any search results or information outside of the query.
        
        Context:
        A user will submit a query and you are required to dissect the implicit beliefs, premises, or preconceptions underlying their question or statement.
        
        Example Format:
        Assumption: [State the first key assumption]
        Assumption: [State the second key assumption]
        Assumption: [State the third key assumption]
        
        Outcome:
        Provide a clear, concise list of the underlying assumptions for the given user query.
"""

GENERATE_FACT_CHECK_QUESTION_SYS_PROMPT = """
     As an expert in fact-checking and internet research, your task is to formulate precise and fact-checkable questions that challenge the foundational assumptions given by the user.

    ### Instructions:

    1. Generate internet search queries that examine the basic existence or availability of the services or features mentioned in the user's query.
    2. Use varied wording and sentence structures to broaden the scope of the search.
    3. Your responses should be suitable for conducting thorough internet searches.
    4. Do not address the user directly, as the user will not see your searches. 
    
    ### Example Format:
    Fact Check: [State the first internet search query]
    Fact Check: [State the second internet search query]
    Fact Check: [State the third internet search query]
    
    Generate your internet search queries below:

"""

reference_prompt = f"""
You MUST write all used source urls at the end of the report as references, and make sure to not add duplicated sources, but only one reference for each.
Every url should be hyperlinked: [url website](url)
Additionally, you MUST include hyperlinks to the relevant URLs wherever they are referenced in the report: 

eg: Author, A. A. (Year, Month Date). Title of web page. Website Name. [url website](url)
"""

SUMMARIZE_FINDINGS_SYS_PROMPT = f"""### Instructions: As an expert in factual verification, determine the accuracy of 
    the given claims based on the given data. Summarize your findings, and provide a comprehensive explanation.
    
    ### Context:
    post: [social media post to be fact checked]
    data: [url and summary to be used to answer]
    
    ### Desired Outcome:
    - Length: Detailed summary
    - Format: Clear and structured analysis
    - Style: Professional and objective
    
    ### Task:
    Summarize the findings on the validity of the claims and provide detailed explanations to support your conclusions.
    Conclude with a verdict from 'pants-fire', 'false', 'mostly-false', 'half-true', 'mostly-true', or 'true', 
    or declare 'uncertain' if conclusive information is unavailable. Include reasoning and cite source domains. 
    Responses should be based on factual data and contextually relevant information. "
    
    Please follow following guidelines:
    - You MUST determine your own concrete and valid opinion based on the given information. Do NOT defer to general and meaningless conclusions.
    - You MUST write the report with markdown syntax
    - Use an unbiased and journalistic tone.
    - Don't forget to add a reference list at the end of the report in apa format and full url links without hyperlinks.
    - {reference_prompt}
"""

SUMMARIZE_FINDINGS_USER_INPUT_PROMPT = """
    post: {post}
    data: {data}
"""
