# Perplexity Created A Live Tutorial For A PyTorch Transformer

I have been trying to understand how a simple transform LLM work, mostly by reading 'Attention is all you need' and many youtube videos. At the point I felt like I had a grasp on the basics, I wanted to implement a simple LLM encoder and decoder. The tutorials I could find were either too high level or more than I was looking for. Hmm.

I use Perplexity a lot for search and especially for examples of how to do things, but I don't use it for acutal coding because I don't like the extra step to cut and paste. For coding I use Gemini and Claude. I didn't want to just tell Gemini or Claude to build me a simple LLM. I wanted to step through the build process. It dawned on me that Perplexity might work for this.

**Spoiler: Perplexity talked me through a step by step implementation using Pytorch, and it worked**

First, I asked it **briefly, describe the steps in the training phase of an llm. keep it simple, focus on the 2017 pagper 'all you need is attention'**. From there I had a conversation with Perplexity where I worked through all the steps and then added the decoder phase. As it went along I used Jupyter notebooks to build up the functions step by setp. I have to say it worked great. By the end, it actually worked. When I say it works, it didn't crash :) and generated nonsensical output.

For a summary of how it looked, check out summary.md'. The full transcript of the conversation is in 'full-transcript.md'.

To check my work, I asked both Gemini 2.5 and Claude sonnet to review the code and both said it looked pretty reasonable. However, I had left out the training loop and the loss function, so of course it wouldn't work properly. So I asked Claude Sonnet to

## Heres a list of the files I ended up with

- Training Data
  - pg55.txt (full text of The Wonderful Wizard of Oz)
  - chapter1.txt (subset of pg55 for training data)
- Final Code in jupyter notebook and export to py
  - encoder.ipynb
  - encoder.py
  - decoder.ipynb
  - decoder.py
  - embedding.ipynb
  - embedding.py
- Encoder Output
  - encoded_vector.pth
- Logs
  - full-transcript.md
  - summary.md
  - prompt.md (for summary)
- Reviews By Claude and Gemini
  - review.md
  - review.pdf
