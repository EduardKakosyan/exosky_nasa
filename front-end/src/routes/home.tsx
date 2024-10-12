import { useState } from "react";
import { ShootingStars } from "../components/ui/shooting-stars";
import { StarsBackground } from "../components/ui/stars-background";
import { ExploreButton } from "../components/explore-button";
import { PlanetCard } from '../components/planet-card'
import { HomeButton } from "../components/home-button";
import { planetArray } from "../data/data";


export function Home() {
   const [exploreMode, setExploreMode] = useState(false);

   return (
      <div className="h-screen bg-black flex flex-col items-center justify-center relative w-screen">
         {!exploreMode && (
             <>
                 <h2 className="relative flex-col md:flex-row z-10 text-3xl md:text-5xl md:leading-tight max-w-5xl mx-auto text-center tracking-tight font-medium bg-clip-text text-transparent bg-gradient-to-b from-neutral-800 via-white to-white flex items-center gap-2 md:gap-8 h-full">
                     <span className="text-6xl">Sky Painters</span>
                 </h2>

                 <h3 className="relative md:flex-row z-10 text-3xl md:text-5xl md:leading-tight max-w-5xl mx-auto text-center tracking-tight font-medium bg-clip-text text-transparent bg-gradient-to-b from-neutral-800 via-white to-white flex items-center gap-2 md:gap-8 h-full">
                     <span className="text-4xl">NASA Space Apps Challenge 2024</span>
                 </h3>

                 <div className="mb-32">
                     <ExploreButton onExploreCall={() => setExploreMode(true)}/>
                 </div>
             </>
         )};


          {exploreMode && (
              <div className="w-screen h-screen flex flex-col mt-20">
                  <div className="absolute top-4 left-4 z-50">
                      <HomeButton onHomeCall={() => setExploreMode(false)}/>
                  </div>

                  <div className="flex justify-center items-center w-full h-full">
                  <div className="grid 2xl:grid-cols-2 xl:grid-cols-2 lg:grid-cols-2  md:grid-cols-1 sm:grid-cols-1 gap-2 h-full mx-auto">
                     {planetArray.map((item, index) => (
                     <div key={index} className="z-10 mx-10">
                        <PlanetCard planetObject={item}/>
                     </div>
                  ))}
                  </div>
               </div>
               
            </div>
         )};

         




         <ShootingStars />
         <StarsBackground />
      </div>
   );
}
