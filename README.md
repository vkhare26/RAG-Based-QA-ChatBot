Overview:

In this assignment, we developed a LLM-Based Retrieval-Augmented Generation (RAG) System using two AI models: Mistral AI model and Llama Model. Our goal was to enhance information retrieval and question-answering by leveraging semantic search and large language models.

Workflow:
  1. Data Collection & Scraping:
     
     i. We scraped the entire dataset, which included General Info and History of Pittsburgh/CMU, Events in Pittsburgh and CMU, Music and Culture, and Sports.
     
     ii. To extract relevant content from different sources, we used the following techniques:
          a. BeautifulSoup for parsing static HTML web pages.
          b. Selenium for handling and extracting data from dynamic web pages that require JavaScript rendering.
          c. PdfPlumber for extracting text from PDFs, ensuring comprehensive coverage of structured documents.
     
     iii. The extracted data was cleaned and stored in text files for further processing.
     
  3. Data Processing & Embedding Generation:
     i. Once the data was collected, we split it into smaller chunks to facilitate better retrieval.
     
     ii. Each chunk was converted into vector embeddings using various SentenceTransformer models, allowing efficient semantic search.
     
     iii. The following embedding models were used:
          A. all-MiniLM-L6-v2 – a lightweight model optimized for fast sentence-level embedding generation.
          B. BAAI/bge-large-en – a more advanced model designed for high-quality retrieval and ranking.
          C. mpnet-base-v2 – a transformer-based embedding model that enhances text similarity search.
     
     iv. These embeddings were stored in a vector database for quick retrieval.
     
   4. Retrieval & Inference Testing:
      i. We implemented a retrieval mechanism based on cosine similarity, where the query embedding was compared with stored embeddings, and the top-k most relevant chunks were retrieved.
      
      ii. Finally, we ran inference on the retrieved results using two large language models:
         A. Mistral-7B-Instruct-v0.3 – optimized for structured question-answering and instruction following.
         B. llama3-8b-8192 – a powerful model designed for general-purpose reasoning and text generation.
      
      iii. We evaluated the system’s performance by testing it on a set of question-answer pairs, analyzing its accuracy and relevance in retrieving correct information.
      
Conclusion:

This pipeline successfully integrated web scraping, text processing, semantic retrieval, and LLM inference to create a robust RAG-based QA system. The combination of efficient retrieval methods and advanced language models ensured accurate and contextually relevant responses.
