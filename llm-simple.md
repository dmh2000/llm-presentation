---
marp: true
theme: default
paginate: true
---

# How Language AI Works

A simple guide to understanding how AI generates text

---

## Tokenization: Breaking Text Into Pieces

**From words to building blocks** 

- AI doesn't understand words like we do
- It breaks text into smaller chunks called "tokens"
- Each chunk gets a unique number
- Think of it like giving every word a barcode
- Example: "The cat" might become numbers like [415, 2891]

---

## Embedddings: Creating Meaning Maps 

**Turning numbers into concepts**

- Each token number becomes a point in a multidimensional space
- Similar words get placed near each other
- Like organizing books by topic in a library
- The AI learns these connections during training
- This helps the AI understand relationships between words

---

## Embedding Vectors

**Its all about the vectors**

 - The rest of the process is about refining these vectors so that they encode the various relationship between tokens
 - The math is a bunch of linear algebra and matrix operations
 - In the end, these vectors are used to predict the next word
  
---

## Positional Encoding: Remembering Word Order

**Position matters**

- "Dog bites man" means something different than "Man bites dog"
- AI needs to know which word came first, second, third
- Special markers are added to remember position
- Like numbering pages in a book
- This helps maintain the meaning of sentences

---

## Transformr Blocks: The Thinking Layers

**Multiple levels of understanding**

- The AI has many layers stacked on top of each other
- Like floors in a building
- Each layer understands the text a bit deeper
- Bottom layers: basic grammar and word patterns
- Top layers: complex ideas and reasoning
- More layers = smarter AI
- Attention->Neural Network->Normalization

---

#### Attention: Looking at Context

**Understanding connections**

- **Each word looks at every other word** in the sentence
- The AI asks: "How does this word relate to that word?"
- Multiple "attention heads" focus on different relationships
- Example: In "The dog was tired," the AI connects "tired" back to "dog"
- This is how AI understands context

---

#### Feed Forward Neural Network: Processing Information

**Transforming understanding**

- After understanding connections, each word gets processed individually
- Think of it like a filter that enhances certain features
- Makes the understanding richer and more detailed
- Happens at every layer
- Combines with context understanding for full meaning

---

#### Normalization: Keeping Things Stable

**Maintaining consistency**

- With so many layers, things could get messy
- Special techniques keep the data organized
- Like a quality control check at each step
- Ensures the AI doesn't get confused
- Allows for very deep, complex models

---

## Projection: Preparing Predictions

**Getting ready to respond**

- The final understanding gets converted to possible next words
- Every word in the vocabulary gets a score
- Higher score = more likely to be the next word
- Like having thousands of options ranked by confidence
- This creates a list of possibilities

---

## Softmax: Calculating Probabilities

**From scores to chances**

- Scores get converted to percentages
- All percentages add up to 100%
- Shows how confident the AI is about each word
- Can be adjusted to be more creative or more predictable
- More randomness = more creative, less predictable

---

## Choosing the Next Word

**Making the decision**

**Different approaches:**
- Argmax: Pick the most likely word (safe and predictable)
- Sample: Choose randomly from top candidates (more creative)
- Balance between creativity and accuracy

**Why it matters:**
- Predictable: consistent but can be boring
- Random: interesting but sometimes makes mistakes
- Most systems use a mix

---

## Detokenization: Converting Back to Text

**From numbers to words**

- The chosen number becomes a word again
- That word gets added to the response
- The process repeats for the next word
- Continues until the response is complete
- Final result: the text you see

---

## The Autoregressive Loop

**How AI writes one word at a time**

1. Read all the text so far
2. Predict the best next word
3. Add that word to the text
4. Repeat from step 1
5. Stop when the response is complete

Like writing one word at a time, always reading what came before

---

# The Big Picture

**How it all works together:**

Your text → Broken into pieces → Understanding created → Connections found → Next word predicted → Text appears

**Key ideas:**
- AI processes text in many layers
- Each layer adds deeper understanding
- The AI predicts one word at a time
- It always considers everything that came before
