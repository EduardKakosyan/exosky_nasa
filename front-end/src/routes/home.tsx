import { useState } from "react";
import { ShootingStars } from "../components/ui/shooting-stars";
import { StarsBackground } from "../components/ui/stars-background";
import { ExploreButton } from "../components/explore-button";
import { PlanetCard } from '../layout/planet-card'
import { HomeButton } from "../components/home-button";

type PlanetObject ={
   name: string;
   imgSrc: string;
   href: string;
}

const planetArray: PlanetObject[] = [
   {name: "Earth", imgSrc: "MapOfEarth.jpg", href: "earth"},
]

export function Home() {
   const [exploreMode, setExploreMode] = useState(false);

   return (
      <div className="h-screen bg-black flex flex-col items-center justify-center relative w-screen">
         {!exploreMode && (
            <>
               <h2 className="relative flex-col md:flex-row z-10 text-3xl md:text-5xl md:leading-tight max-w-5xl mx-auto text-center tracking-tight font-medium bg-clip-text text-transparent bg-gradient-to-b from-neutral-800 via-white to-white flex items-center gap-2 md:gap-8 h-full">
                  <span className="text-6xl">Exosky</span>
               </h2>

               <div className="mb-32">
                  <ExploreButton onExploreCall={() => setExploreMode(true)}/>
               </div>
            </>
         )};


         {exploreMode && (
            <div className="w-screen flex flex-col">
               <div className="absolute top-4 left-4 z-50">
                  <HomeButton onHomeCall={() => setExploreMode(false)}/>
               </div>

               {planetArray.map((item, index) => (
                  <div key={index} className="z-10">
                     <PlanetCard imgSrc={item.imgSrc} planetName={item.name} href={item.href}/>
                  </div>
               ))}
               

            </div>
         )};

         




         <ShootingStars />
         <StarsBackground />
      </div>
   );
}
