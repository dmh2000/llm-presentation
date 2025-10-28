@/full-transcript.md summarize full-transcript.md and write the results to summary.md.
keep all instances of python code snippets.
keep all markdown sections headers and subheaders verbatim.
create a brief summary of the content of each section.
remove all web links. the file is big, you might need to process it in pieces. maybe the best way is to process each top level markdown section '#' and its content one section at a time.
do it however works best for you.
be sure to keep the markdown headers verbatim. do not change them. summarize only the content of the sections.


@llm-simple.md @llm-simple.pptx @md_to_pptx.py  The file llm-simple.md is the basis for creating  power point presentation slides.  Review llm-simple.md and create a parallel markdown file that has a summary of each section that will be used as the slide notes in the power point slides. The summaries will be used to create text to speech, so they should be suitable for reading aloud.  Name the new file llm-simple-notes.md and place it in the same directory as llm-simple.md.

modify md_to_pptx.py so it takes one required input, the markdown file that contains the slide text, and an optional input that contains corresponding slide notes. use the slides notes file and add those to the powerpoint out as slide notes.

create a python script that embeds an mp3 file in a powerpoint pptx presention slide. the script will have 3 required arguments: 
- -s  the number of the slide to embed the mp3 in
- the name of the pptx file to modify
- the name of the mp3 file to embed
place the script in file cmd/embed_audio.py
the directory t1/ppt contains a powerpoint presentation with no media added
the directory t2/ppt contains an idential powerpoint presentation with media added
file 12.txt is a diff of the two directories
first create a plan for creating the python script. let me know if you need any more information
do not create any code at this point


@test/cmd  python program embed_audio.py is almost working but it has an error in it. when it  modifies a powerpoint by adding an mp3, the powerpoint program says it needs to repair the file. after it repairs the file, it works. can you analyze test/cmd/embed_audio.py to see if you see an error. the file a1.pptx is a file that works correctly in powerpoint. you can use context7 for the microsoft open format of powerpoint xml.