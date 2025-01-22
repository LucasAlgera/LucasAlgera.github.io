---
layout: default
title: README
---

## Introduction to the Learning Log

For this block, **we've put the Learning Log entirely inside GitHub**. The Markdown files in this folder replace the PowerPoint file on Teams that you've had in previous years. 
Because the LL is now part of your codebase, you can work on it straight from your IDE, and you can easily embed your code into your evidence.
We hope this will make evidencing more intuitive for programmers. 

> [!IMPORTANT]
> * **Keep your Learning Log up-to-date throughout the block.** We recommend to sync it with your work at least once per week.
> * Some ILOs have a hard requirement for weekly updates. Please check the details per ILO.
> * The Learning Log will be the basis for your 1-on-1s. Use it to prepare for your feedback sessions, and make sure it contains useful conversation points.
> * The Learning Log will also be the teachers' main resource for grading at the end of the block. Make sure your evidence speaks for itself, without a need to dive into your codebase unguided. 

## Add your personal info!

First of all, make sure that the template contains enough of your personal details:

1. In [index.md](index.md), fill in your student name & number and add a picture of yourself. This info will show up on the index page of the website that you'll generate from the Learning Log. (See below for instructions on how to do that.)
2. In [_config.yml](_config.yml), fill in your student name & number. This will display them in the header of each page of the generated website.

## Sections

The index page should contain your personal info, as well as your end-of-block reflection and self-assessment.

Next to this, there is a separate Markdown file per ILO. 
Each ILO file starts with the ILO's overall description, suggested evidence, and detailed rubric. Please do not remove or alter this first part of the files.

Some ILO files already contain some evidence structure that you need to follow. Please do not change this structure.
For other ILO files, the evidence section has no prescribed structure and can be filled in however you want.

## Markdown cheatsheet

For a quick overview of how to use Markdown, have a look at the small [cheatsheet](cheatsheet.md) we've prepared!

## What should you include as evidence?

Here's what you should consider incorporating as evidence in your ILO pages:

- **Multimedia**: Add videos, screenshots, diagrams wherever they add value. Visual representation can often convey more than words. Warning: videos can become large files very quickly, so use them wisely (not too long, reasonable resolution, proper compression, etc). Also, *don't put videos on YouTube*, but include them proper way (see our Markdown cheatsheet). Officially, we cannot accept videos on external websites as evidence.
- **Link to Code**: You can provide links to specific lines of your code (see cheatsheet). 
- **Code Snippets**: Uou can easily provide code snippets using Markdown (see cheatsheet).
- **GitHub Issues**: If you choose to use GitHub issues to plan out your tasks, you code create screenshots of them and embed them here as images.
- **External Documentation / AI Tools**: If your work is based on external articles, papers, codebases, or other resources, refer to them with the appropriate names and URLs. The same goes for any tools that you have used, including AI tools like ChatGPT.
- **Feedback Summaries**: Feedback, whether from peers or instructors, is a valuable part of learning. Summarize and reflect on the feedback received to show your responsive actions and learning.

## Website instructions
This GitHub repo has been set up so that it can easily generate a nice-looking website out of your Learning Log Markdown files. 
The easiest way to trigger this is to **publish a release**. You should do this at least once, at the end of the block.

1. On the main page of your repo, click "Create a new release".
![Step 1](assets/media/github-page-instructions-1.png)

2. Give it a tag and description, and click "Publish release".
![Step 2](assets/media/github-page-instructions-2.png)

3. This will trigger a GitHub action that builds and deploys the website. You can see the progress under "Actions". The top item in the list there is your most recently triggered action. Click on it to see more info.
![Step 3](assets/media/github-page-instructions-3.png)

4. If the action has suceeded, its "Summary" page should look something like this. Copy the (auto-generated) URL to your clipboard. This is the URL that you should also mention in the Brightspace comment box when you hand in your final assignment.
![Step 4](assets/media/github-page-instructions-4.png)

Before submitting your assignment, make sure to test if all your videos etc show up correctly on this website!

## Build the LL website locally

We recommend to also generate the Learning Log website locally on a regular basis.
On Windows, this can be done as follows:

1. Install Ruby
    1. Download and install **Ruby+Devkit** from [RubyInstaller for Windows](https://rubyinstaller.org/). You'll see versions like `Ruby+Devkit 2.7.X (x64)`. Choose a version based on your Windows (64-bit or 32-bit). Most modern systems will use 64-bit.

    2. During the installation:
        - Use the default options.
        - Ensure the "Add Ruby executables to your PATH" option is checked.
        - Once the installation is finished, you'll be prompted to install MSYS2 development toolchain. Go ahead and let it install as it's required for Jekyll and some Ruby gems.

2. Navigate to your repository `evidence` directory and open the terminal/command prompt 
3. Install Bundler and Jekyll
```bash
gem install jekyll bundler
```
4. Install Dependencies:
```bash
bundle install
```
5. Build and Run the Jekyll Site
```bash
bundle exec jekyll serve
```

Now, you should be able to access the site locally at [http://localhost:4000](http://localhost:4000).
