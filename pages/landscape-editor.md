# Landscape Editor

## Introduction

JEDI fallen order, Borderlands, Black Myth Wukon and many more games have been made using the Unreal Engine. All these games have incredible landscapes and have most likely made use of Unreal's Landscaping tool. With many games becoming more complex and environments becoming bigger and more impressive it is almost a necessity for game engines to have a landscape sculpter of some sorts. With multiple other engines also having similar landscaping tools I thought it was an interesting project to try and recreate one in an Educational Engine supplied to me by my teachers. This assignment was part of my studies in **Creative Media and Game Technologies** at **Breda University of applied sciences**.

In this article I will share the knowledge I have gained having worked on and having researched landscape editors. 


## The basics of a landscape editor

A landscape editor as a whole has to consist of 2 things. 
1. Deformation of the landscape using different types of brushes. 
2. Rendering of the landscape. 

The deformation part should be user friendly and easy to use. The tool should feel responsive and you need to make good use of things like debug drawers. These can be used to outline the landscape chunks and should definitely be used for the brush. With only the cursor the user has no idea where they are drawing and what impact their input will have to the terrain. 

The rendering of the landscape needs to be dynamic. When we are working with a mesh that we are changing every frame we cant be treating this as a regular mesh. With the rendering we should make sure that this doesn't interrupt the workflow of the user. So no huge lag spikes whenever we are drawing on the terrain. 

## How do we store our data?

I have decided to make use of greyscale heightmaps to store our terrain data. This is something other engines such as Unreal do aswell. This is nice for muliple reasons: 
- Instead of just doing a binary dump and storing our vertex data raw on disk (which would be a hell to debug if issues were to occur). We can also save our terrain using .png format, with that we can make use of the compression it gives us and its much easier to debug. 
- We can also make use of libraries such as STB which will take care of the loading and saving of our data by using functions such as `stbi_load()` and `stbi_write_png()`. Having to write our own loading and saving functions will be a lot more time consuming and much more error prone. 
- Easy for users to import their own heightmaps. If you are using your own loading and saving algorithms it is impossible for users to import other terrains created outside of your program. 
- Easy to send our data to the GPU for rendering. I will talk further about this later. 



## How do we render our landscape?

## Different brushes

## Raymarching a heightmap

## Future improvements