###  Board and Committee Meetings   
   
We start with the [videos recorded by the local public access cable channel](https://acmi.tv/programs/government/) for government meetings, create a transcript using [OpenAI Whisper](https://github.com/openai/whisper), ask a series of questions, one for each of the published meeting agenda items, and follow-up questions depending on the summary of each item, using LangChains text splitters and QA retrieval pipelines.  The raw transcript is further organized by agenda item and speaker in markdown format; to be automated.  The raw transcript and markdown are saved as text columns in the ```governance.meetings``` table, while the Q&A is stored as a dictionary.


This [notebook]("transcripts\ ETL.ipynb") shows the components and is intended to be used with the *polis* postgres database available.  Adapting for stand alone use should be straighforward.


#### Raw Transcript

The raw transcript using [OpenAI Whisper](https://github.com/openai/whisper) is about 25,000 words, 125,000 characters for a 3 hour meeting.  The OpenAI api calls to create the transcripts run from about 0.90 to $1.00 per meeting.

Meetings held via Zoom have poor transcription when compared to in-person meetings; where remote participants also are sometimes garbled.

The raw transcript is one long paragraph.  Our choice of text splitters in langchain's RecursiveCharacterTextSplitter module bears scrutiny.

We store the raw transcripts for further internal processing or by agents.


#### 20 Questions

We use the OpenAI chat llm and Langchain's RetrievalQA to ask questions.  We can prepare the questions from asking for a summary of the entire meeting, a summary for each agenda item and follow-up questions where appropriate.  The chat does poorly on answering questions such as "list everyone who spoke in the meeting" due to context limitations, but does very well in asking detailed questions about a topic. We ask pre-determined questions such as results of any votes expected.  

These questions can all be prepared in advance of the meeting.

Answers from the OpenAI chat gpt-4 questions cost about \$0.20 each as of summer, 2023.  


#### Attribution Markdown

Currently, the attribution is done manually, using the published meeting agenda items for the top headers and the speaker for the sub-headers, making a collapsible presentation possible.  Analytics on speakers and independent topics of a meeting become possible by using attribution, so the effort is worthwhile.  Presenting a 25,000 wall of words has value to feed other processes.  Expanding each agenda item (topic) and arranging the speakers in order with the portion of the transcript attributed to each is eaier to consume for individuals.  As well, the raw transcript is improved with text associated with speakers.

