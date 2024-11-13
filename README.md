This project is a modification of the source code for lesson 6 of the "LangChain Chat With Your Data" deeplearning AI course. It is basically a rag chatbot app (programmed in python with panel) that allows you to upload a set of PDF, CSV, and/or text documents and engage in a chat about those documents. You can ask the chatbot to do typical tasks such as summarization or improvement suggestions as well as more specific questions about the content in the uploaded documents.

The code was modified to work with hugging chat embeddings and endpoints, instead of OpenAi embeddings and chatGPT. The model used to create the embeddings is "all-mpnet-base-v2" and the LLM is "Mistral-7B-Instruct-v0.3". Both these models are fully free to use, unlike the OpenAi models, and do not require API keys. Also, a minimal amount of memory is required to use these. For specific information regarding the models refer to the corresponding hugging face model cards:

https://huggingface.co/sentence-transformers/all-mpnet-base-v2 https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3 

Line 60 of main.py needs to point to an existing filepath. Once the program is running, any PDF, CSV, or text file can be chosen by navigating in a browser via the "configure" tab, but the program will be expecting a document to begin with, otherwise you may get a ValueError exception when compiling the code. To start the program, type and enter "panel serve main.py --autoreload" in your project's terminal prompt.

If you are loading a very large document or set of documents your session token may expire. To change the default bokeh server session timeout use the --session-token-expiration option. Example: "panel serve main.py --autoreload --session-token-expiration 900000" (assumming units are in milliseconds this should be equivalent to 15 minutes).

The embedding and LLM models are defined in lines 18 and 35. You can enter different models here but be sure to check the models you use work with hugging face embeddings and/or endpoints.

10/3/2024: Added functionality to save the chat history to a file.

10/5/2024: Added funtionality to process CSV and text files. Application now expects .csv extension for CSV filenames, .txt extension for text filenames, and .pdf extension for PDF files.

*Note: The requirements.txt file probably contains more libraries than are used by the application. I was too lazy to setup and test a new, cleaned-up environment. Apologies if this causes any inconvenience. 
