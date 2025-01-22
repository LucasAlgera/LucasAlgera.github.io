---
title: "🦾 ILO 4: Technical achievement (40%)"
preview_title: "🦾 ILO 4"
layout: default
---

As a game (engine) programmer, __I can create a technically impressive production-ready tool / feature__, so that my work can help shape future projects.

# 💭 Suggested Evidence
- Videos / screenshots of the features developed
- Relevant code snippets
- Explanations of the implemented concepts

# 💯 Detailed Rubric

🔴 **Poor:** Evidence of some development work in line with the self-study plan. The student has written enough code themselves.

In ILO 1 I have constantly kept up with my self-study plan and when I had to change things I would always announce that in that weeks ILO part. And eventually my tool came out like I expected. Terrain Brushes and Terrain Sculpting in the BEE engine. 

*Week 3 milestone:* Be able to “paint” on a surface and have that be saved to a greyscale png.

*Week 5 milestone:* Upon loading in the terrain have the height of the polygons in the grid be dependent on the heightmap from the png using either just a bunch of planes or doing it the way the OpenGL article below instructs. 

*Week 7 milestone:* Optimize the brush so that real time editing of the terrain goes smoothly without lag and add a fitting UI that helps the user with the brush (brushsize, strength, etc.)

<video width="320" height="240" controls>
  <source src="../assets/media/ToolShowcase.mp4" type="video/mp4">
</video>

In this video I show that I have achieved all the milestones I had set for myself. I have the grayscale painting with different types of brushes: circle, falloff, texture brush and smoothing brush. I have the terrain rendering which is being done by offsetting vertices of a grid by sampling over a heightmap in a shader. I have added UI which the user can use to tweak brush settings, see the heightmap they are drawing on and a small manager where you can load more heightmaps from disk. 

🟠 **Insufficient:** Evidence of the project output being a usable tool/feature. Videos and code examples show the project's basic usage and capabilities.

With 1 simple line of code the user can add a landscape to the engine: 
`Engine.TerrainManager().AddTerrain("Terrain1", "assets/textures/HeightMap1.png", 255, false);`

The first paramater represents the name, second is the filepath of the heightmap you want to load, 3rd is the amount of subdivisions and last is a boolean if you want to load an empty terrain. 

In the video above I have already showcased most of the tool's features. 

🟡 **Sufficient:** Evidence of the project output having all the functionality mentioned in the self-study plan, for example by showing multiple demos. The work has been sufficiently complex.

🟢 **Good:** Evidence of the tool/feature being easy to embed into other projects, using well-designed APIs and clear examples of usage. Evidence shows good technical execution in terms of software architecture, algorithms, data structures, error handling, etc.

🔵 **Excellent:** Videos and other evidence show that the student's code is robust and well-tested. The student has significantly pushed the boundaries of the project, by investigating and solving complex domain problems on their own.

# 🔍 Evidence

...
