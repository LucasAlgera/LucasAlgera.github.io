# Exploring Landscape Editors in game engines. 
_Lucas / January 22, 2025_

![banner + Logo](/assets/images/banner.png)

## Introduction

JEDI fallen order, Borderlands, Black Myth Wukong and many more games have been made using the Unreal Engine. All these games have incredible landscapes and have most likely made use of Unreal's Landscaping tool. With many games becoming more complex and environments becoming bigger and more impressive, it is almost a necessity for game engines to have a landscape sculpter of some sorts. 

With multiple other engines also having similar landscaping tools, I thought it would be an interesting project to try to recreate one in an Educational Engine supplied to me by my teachers. This assignment was part of my studies in **Creative Media and Game Technologies** at **Breda University of applied sciences**.

In this article, I will share the knowledge I have gained having worked on and having researched landscape editors. 


## The basics of a landscape editor

A landscape editor as a whole has to consist of 2 things. 
1. Deformation of the landscape using different types of brushes. 
2. Rendering of the landscape. 

The deformation part should be user-friendly and easy to use. The tool should feel responsive and you need to make good use of things like debug drawers. These can be used to outline the landscape chunks and should definitely be used for the brush. With only the cursor the user has no idea where they are drawing and what impact their input will have to the terrain. 

The rendering of the landscape needs to be dynamic. When we are working with a mesh that we are changing every frame we can't be treating this as a regular mesh. With the rendering we should make sure that this doesn't interrupt the work flow of the user. So no huge lag spikes whenever we are drawing on the terrain. 

## How do we store our data?

I have decided to make use of grayscale heightmaps to store our terrain data. This is something other engines such as Unreal do as well. This is nice for multiple reasons: 
- Instead of just doing a binary dump and storing our vertex data raw on disk (which would be a hell to debug if issues were to occur). We can also save our terrain using .png format, with that we can make use of the compression it gives us and its much easier to debug. 
- We can also make use of libraries such as STB which will take care of the loading and saving of our data by using functions such as `stbi_load()` and `stbi_write_png()`. Having to write our own loading and saving functions will be a lot more time consuming and much more error-prone. 
- Easy for users to import their own heightmaps. If you are using your own loading and saving algorithms it is impossible for users to import other terrains created outside of your program. 
- Easy to send our data to the GPU for rendering. I will talk further about this later. 

STB supports upto 16 bit depth when writing to png's, I however found that 8 bits are already enough for me. But if your goal is to have really high definition landscapes and 16 bits aren't enough you could consider making use of OpenEXR. OpenEXR or exr for short is mostly used in the film VFX industry because of its high bit depth which makes it so filmmakers can store more colours. Exr supports up to 16-bit half-float and 32-bit float channels which should give you more than enough precision in your terrain. You can make use of [TinyEXR](https://github.com/syoyo/tinyexr) as a replacement for the STB library.

Because the engine I worked in didn't support meshes that exceed 255x255 subdivisions I never needed to make use of a resolution higher than that but be aware that using large heightmaps can really start to dig into memory if you don't watch out. 

## How do we render our landscape?

As I've said before we need to make sure that our landscape rendering happens dynamically without having too many performance issues. This is where using a heightmap comes into place. We can send our heightmap we use to store our terrain data to our GPU and offset our vertices inside of the vertex shader. For this we will need a flat terrain (a grid). 

After this we will sample over our heightmap using the GLSL `texture()` function like this: 
`float height = texture(s_heightmap, a_texture0).r;`
We can then use this height to offset each one of our vertices: 
`vec3 new_position = vec3(a_position.x, a_position.y + height, a_position.z);`

By doing this we don't have to remake our mesh every time it changes and it's very cost efficient. 

![Vertex offsetting illustration](/assets/images/VertexShaderHeightmap.png)

And that is basically it when it comes to the terrain rendering. 

## How do we modify the data on the heightmap

When loading in our heightmap in using stbi_load() we store our data in an unsinged char*. 

```
struct Heightmap
{
    int width, height, bpp;
    unsigned char* data = nullptr;
};

void LoadHeightmap()
{
    heightmap.data = stbi_load(filepath, &heightmap.width, &heightmap.height, &heightmap.bpp, 0);
}
```

After having loaded in our heightmap data into memory we can access it like this:
```
int index = (brush.x * heightmap.width + brush.x) * heightmap.bpp;

// Change all our colour channels.
heightmap.data[index + 0] = drawingResult; // red
heightmap.data[index + 1] = drawingResult; // green
heightmap.data[index + 2] = drawingResult; // blue
heightmap.data[index + 4] = drawingResult; // alpha
```

With this we draw 1 pixel at a time but if we put this in a loop and preform a radious check we can have a circular brush!

## Different brushes

A good landscape editor should have a variety of different brushes in it's arsenal. Because I had some time constrains I added the bare necessities which in my opinion were:
- A regular circular brush. 
- A linear falloff brush. 
- A smoothing brush. 
- A texture brush. 

Maybe aside from the texture brush all of these are needed to make basic terrains. And adding a brush strength and brush size parameter will help with the usability. 

![Brushes showcase](/assets/images/BrushTypes.png)

Most of the brushes you would want to have can be created with mathematical functions. 
For example the **circular brush** is just a radius check and for the **falloff brush** we multiply the brush's distance from center to the brush strength so the further away from the center we are the lower the terrain is. 
For the **smoothing brush** we simply check all the 8 neighboring  pixels and get an average of that and set our pixel height to that. 
Finally, the **texture brush** is jut simply loaded into memory and the buffer is applied to the heightmap at the cursor's position. 

For further inspiration regarding mathematical functions you could look at [easings.net](https://easings.net/).

Unreal for example has a bunch more brushes and settings such as erosion, noise, ramps, and different mathematical functions resulting in something else than a linear falloff. 

## Raymarching a heightmap

A bit later into making this tool I stumbled upon an issue. When for the CPU the terrain is a flat grid and only for the GPU it is an actual terrain. How do we accurately calculate the mouse to terrain intersection on the CPU without our cursor going straight through the terrain? 

After some pondering I decided to try to raymarch the heightmap. 
First off we shoot a ray from the camera and calculate it's entry and exit point from the terrain. 

![Landscape Ray](/assets/images/LandscapeRay.png)

After having these points we convert the ray into heightmap space and for every pixel in that heightmap that the ray shoots over we check if the ray in worldspace is above or under the terrain + the vertexoffset of that pixel. 

![Heightmap Ray](/assets/images/HeightmapRay.gif)

```
// The EntryLocalCoordinates are the coordinates in heightmap space where the ray first enters the grid. 
glm::vec2 currentPos = EntryLocalCoordinates;
int maxSteps = heightmap.width * 2;

for (int step = 0; step < maxSteps; step++)
{
    // The ray is clamped to stay within the bounds of the heightmap.
    int rayIn2DHeightmapX = glm::clamp(int(currentPos.x), 0, heightmap.width);
    int rayIn2DHeightmapY = glm::clamp(int(currentPos.y), 0, heightmap.width);

    // Get height of the pixel from heightmap
    int index = (rayIn2DHeightmapY * heightmap.width + rayIn2DHeightmapX) * heightmap.bpp;

    // This is the height of the vertex (pixeldata together with scale which is then divided by 255 because we go back to worldspace).
    float vertexOffset = (heightmap.data[index] * transform.GetScale().y) / 255.0f + transform.GetTranslation().y;

    // We convert the ray back from "heightmap space" into world space.
    glm::vec3 rayIn3DGrid{};
    rayIn3DGrid.x = (currentPos.x * transform.GetScale().x / heightmap.width) + transform.GetTranslation().x -
                    transform.GetScale().x / 2.0f;
    rayIn3DGrid.z = (currentPos.y * transform.GetScale().x / heightmap.width) + transform.GetTranslation().z -
                    transform.GetScale().x / 2.0f;

    // Get the current height of the ray that is in world space.
    float t = (rayIn3DGrid.x - cameraPosition.x) / rayWorld.x;
    float rayHeight = cameraPosition.y + rayWorld.y * t;

    //Is the ray below the terrain? then we have a intersection.
    if (rayHeight <= vertexOffset)
    {
        //Return the mouse position to be at the intersection point. 
        return glm::vec3(rayIn3DGrid.x, vertexOffset, rayIn3DGrid.z);
    }

    //No intersection? Shoot the ray a tad bit further
    currentPos += rayDirHeightmap;
}

```

If the ray eventually goes under the terrain then thats where we have found an intersection and that is where our new brush position will be. This will be the endresult

![Raymarching](/assets/images/RayMarching.gif)


## Level Of Detail

There are 2 different methods we could use to add LoD to our terrain. 
1. Continuous Levels of Detail (CLOD)
2. Discrete Levels of Detail (DLOD)

<h4>Continuous Levels of Detail (CLOD)</h4>
CLOD means that we split our chunk into smaller parts and the further away those parts are from our player/camera the less triangles we will use for that part. This we cannot store into memory at the start of the program if our camera can move. Thus we'd have to regenerate every close lying landscape chunks everytime our camera moves.  

<h4>Discrete Levels of Detail (DLOD)</h4>
DLOD means that we make use of chunks in our terrain and the further away the player/camera is from a chunk the lower LoD we apply to that chunk. This means that we have to either store 3 different Levels of detail per chunk into memory or generate them on the fly. 

![CLOD DLOD](/assets/images/LoD.png)

So I have a couple of things to keep in mind: 
- 🟢 CLOD: By far the smallest memory usage when comparing it to DLOD. This is because we are not storing multiple Levels of 1 chunk or not storing triangles we won't need. 
- 🟢 CLOD: By far the slowest, having to regenerate multiple chunks every time the camera moves is quite expensive. We can reduce the costs by spreading the regeneration over multiple frames but it is still not optimal. 
- 🔴 CLOD: Best looking, with regenerating in a circular area around the camera we don't see any "popping artifacts" which will occur when we regenerate each chunk seperately. 


- 🟢 DLOD: If we store 3 LoD layers into memory per chunk this is could be by far our fastest option during runtime since we won't have to regenerate our map every time the camera moves.
- 🟢 DLOD: If we don't store the layers into memory and regenerate the chunks every time we move this will be a bit slower.  
- 🔴 When comparing it to CLOD we might get some "popping artifacts" when the chunks are regenerating. 


This is what the 2 would look like in Engine:

![In Engine example](/assets/images/COLD_DOLD.png)

You can clearly see that CLOD looks visually more pleasing because there is a more gradual flow between the different levels of detail. In DLOD you can see that everything is a bit more cut-off. Also in the CLOD you can see that area's that are really far away which the user will not see are almost fully optimized away because its just a couple of triangles. 

![Far CLOD](/assets/images/Far_CLOD.png)


Performance: 

If we look at memory usage first and we spawn in 625 (25x25) chunks we actually don't see a huge difference in memory usage: 
- CLOD: 910 MB 
- DLOD: 1000 MB

This difference was kind of dissapointing to see but also made sense, a huge part of our memory goes to the largest level of detail maps stored into memory and the lower levels don't really take up that much memory, which makes the difference between storing 1 LOD and 3 smaller then expected. 

If we look at frametime we can see that CLOD really tanks in performace (this is a 15x15 chunk map):
- CLOD: 35-38 ms
- DLOD: 18-20 ms 

Seeing this I need to make a decision between looks and performance, I think for my usecase (rendering simple terrains for games) using DLOD would be more benifitial. Because with this I can still use big terrains without tanking out on performance. And I also dont think you will really notice the "popping artifacts" that much since in most games will make use of fog/mist. Also game designers can always play around with the distance for every Level of detail to show up and how much the quality goes down every level. 

## Future improvements

There is still so much to landscape editors that I haven't implemented and uncovered yet. I have for example as of now not yet touched the texuring part of terrain rendering. This could however be done by using [Tri-Planar mapping](https://bgolus.medium.com/normal-mapping-for-a-triplanar-shader-10bf39dca05a) (Article by Ben Golus, sep 17, 2017). 
Or LoD'ing and culling. Heightmaps can be massive and it would help for performance if we only render what we can see and what is further away we render at a lower resolution. 
Adding in erosion brushes/simulations or more noise based brushes which can more accurately simulate how real mountains would form. 

The list goes on and on and for the time being there is no real end in sight regarding landscape editing. 

Thanks for reading my article, if you have any feedback or questions, feel free to contact me at [lucasalgera@outlook.com](lucasalgera@outlook.com). 

### Valuable sources 
- [Unreal Engine - Landscape Brushes](https://dev.epicgames.com/documentation/en-us/unreal-engine/landscape-brushes?application_version=4.27)
- [Unreal Engine - Landscape Technical Guide](https://dev.epicgames.com/documentation/en-us/unreal-engine/landscape-technical-guide-in-unreal-engine)
- [Learn OpenGL - Rendering Using Height Maps](https://learnopengl.com/Guest-Articles/2021/Tessellation/Height-map)