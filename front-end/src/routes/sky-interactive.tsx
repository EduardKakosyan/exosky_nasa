import { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { LeftMouse } from '../components/icons/left-mouse';
import { RightMouse } from '../components/icons/right-mouse';
import { useNavigate } from 'react-router-dom';
import { HomeIcon } from '../components/icons/home-icon';
import { resetCanvas } from '../functions/draw';
import { createSky } from '../functions/create-sky';

type Props = {
   imgSrc: string;
};

export function SkyInteractive({ imgSrc }: Props) {
   // React Router navigation
   const navigate = useNavigate();
   function home() {
      navigate('/');
   }

   // State and refs
   const imageSrc: string = imgSrc;
   const scene = new THREE.Scene();
   const mountRef = useRef<HTMLDivElement>(null);
   const [camera, setCamera] = useState<THREE.PerspectiveCamera | null>(null);
   const [cameraPosition, setCameraPosition] = useState<THREE.Vector3>(new THREE.Vector3(150, 0, 40));
   const [cameraRotation, setCameraRotation] = useState<THREE.Euler>(new THREE.Euler(0, 0, 0));
   const pointsRef = useRef<THREE.Mesh[]>([]);
   const linesRef = useRef<THREE.Line[]>([]);
   const setDots = useState<THREE.Vector3[]>([])[1];
   
   // Loading state when image fetching
   const [isLoading, setIsLoading] = useState(true);


   // Function to clean the palette and scene
   function cleanPalette() {
      setDots([]); 
      resetCanvas(pointsRef, linesRef, scene);
      if (camera) {
         setCameraPosition(camera.position.clone());
         setCameraRotation(camera.rotation.clone());
      }
   };


   // Create sky canvas on load
   useEffect(() => {
      const skyCanvas = createSky({
         imageSrc,
         scene,
         mountRef,
         cameraPosition,
         cameraRotation,
         pointsRef,
         linesRef,
         setDots,
         setIsLoading,
         setCamera
      });

      return skyCanvas;
   }, [cameraPosition, cameraRotation]);



   return (
      <div>

         {/* Loading image state component */}
         {isLoading && (
            <div className='absolute inset-0 flex items-center justify-center bg-black bg-opacity-70'>
               <p className='text-white text-1xl'>Loading Sky...</p>
            </div>
         )}

         {/* Clean Palette Component */}
         <button className="p-[3px] absolute top-5 left-5 z-10 bg-white  rounded-md" onClick={cleanPalette}>
            <div className="absolute inset-0 bg-gradient-to-r from-sky-500 to-blue-500 rounded-lg" />
            <div className="px-4 py-2 bg-black rounded-[6px]  relative group transition duration-200 text-white hover:bg-transparent">
               Clean Palette
            </div>
         </button>

         {/* Home Button */}
         <button onClick={home} className='absolute right-5 top-5 border border-blue-500 rounded-full p-2'>
            <HomeIcon className='w-7 h-7 text-white' />
         </button>

         {/* Instructions */}
         <div
             className='absolute bottom-5 right-10 z-10 text-white flex flex-col bg-black border border-blue-500 rounded-lg p-4 text-sm bg-opacity-70 gap-3'>
            <div className='flex flex1 flex-row gap-3 items-center'>
               <LeftMouse className='w-5 h-5'/>
               <p className='flex flex-1'>Move Camera</p>
            </div>

            <div className='flex flex1 flex-row gap-3 items-center'>
               <RightMouse className='w-5 h-5'/>
               <p className='flex flex-1'>Connect Stars</p>
            </div>

            <div className='flex flex1 flex-row gap-3 items-center'>
               <div className=' px-1 border rounded-md'>
                  <h3 className='text-lg'>C</h3>
               </div>

               <p className='flex flex-1'>Create new constellation</p>
            </div>
         </div>

         {/* Canvas */}
         <div ref={mountRef} style={{width: '100%', height: '100vh'}}/>
      </div>
   );


}