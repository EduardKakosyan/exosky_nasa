import { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { LeftMouse } from './icons/left-mouse';
import { RightMouse } from './icons/right-mouse';
import { useNavigate } from 'react-router-dom';
import { HomeIcon } from './icons/home-icon';

type Props = {
   imgSrc: string;
};

export function SkyInteractive({ imgSrc }: Props) {
   const navigate = useNavigate();
   function home() {
      navigate('/');
   }

   const imageSrc: string = imgSrc;
   const mountRef = useRef<HTMLDivElement>(null);
   const [camera, setCamera] = useState<THREE.PerspectiveCamera | null>(null);
   const [controls, setControls] = useState<OrbitControls | null>(null);
   const [isDrawingMode, setIsDrawingMode] = useState<boolean>(false);
   const [_, setSelectedDots] = useState<THREE.Mesh[]>([]);
   const [cameraPosition, setCameraPosition] = useState<THREE.Vector3>(new THREE.Vector3(150, 0, 40));
   const [cameraRotation, setCameraRotation] = useState<THREE.Euler>(new THREE.Euler(0, 0, 0));
   const scene = new THREE.Scene();
   const pointsRef = useRef<THREE.Mesh[]>([]); // Store dots as meshes
   const linesRef = useRef<THREE.Line[]>([]);
   const setDots = useState<THREE.Vector3[]>([])[1];
   const [isLoading, setIsLoading] = useState(true);

   useEffect(() => {
      const mount = mountRef.current!;
      const camera = new THREE.PerspectiveCamera(75, mount.clientWidth / mount.clientHeight, 0.1, 2000);
      const renderer = new THREE.WebGLRenderer({ alpha: true });
      renderer.setSize(mount.clientWidth, mount.clientHeight);
      mount.appendChild(renderer.domElement);

      const geometry = new THREE.SphereGeometry(500, 64, 32);
      geometry.scale(-1, 1, 1);
      const textureLoader = new THREE.TextureLoader();
      const texture = textureLoader.load(imageSrc, () => {
         setIsLoading(false); 
      });
      const material = new THREE.MeshBasicMaterial({ map: texture, side: THREE.DoubleSide });
      const sphere = new THREE.Mesh(geometry, material);
      scene.add(sphere);

      camera.position.copy(cameraPosition);
      camera.rotation.copy(cameraRotation);

      const controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.5;
      controls.enableZoom = true;
      controls.zoomSpeed = 2;
      controls.minDistance = 1;
      controls.maxDistance = 450;

      setCamera(camera);
      setControls(controls);

      const raycaster = new THREE.Raycaster();
      const mouse = new THREE.Vector2();

      // Function to create a dot
      const createDot = (position: THREE.Vector3) => {
         const dotGeometry = new THREE.SphereGeometry(1, 32, 32);
         const dotMaterial = new THREE.MeshBasicMaterial({ color: 'white' });
         const dot = new THREE.Mesh(dotGeometry, dotMaterial);

         dot.position.copy(position);
         scene.add(dot);
         pointsRef.current.push(dot);
      };

      // Function to create a line between two dots
      const createLine = (start: THREE.Vector3, end: THREE.Vector3) => {
         const material = new THREE.LineBasicMaterial({ color: 'white' });
         const points = [start, end];
         const geometry = new THREE.BufferGeometry().setFromPoints(points);
         const line = new THREE.Line(geometry, material);
         scene.add(line);
         linesRef.current.push(line);
      };

      const handleMouseDown = (event: MouseEvent) => {
         // Check for right-click (button 2)
         if (event.button === 2) {
            event.preventDefault(); // Prevent the context menu

            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse, camera!);
            raycaster.far = 1000;

            const intersects = raycaster.intersectObject(sphere);

            if (intersects.length > 0) {
               const intersectedPoint = intersects[0].point.clone();
               createDot(intersectedPoint);

               setDots((prevDots) => {
                  if (prevDots.length === 1) {
                     createLine(prevDots[0], intersectedPoint);
                     return [intersectedPoint];
                  } else {
                     return [intersectedPoint];
                  }
               });
            }
         }
      };

      const handleKeyDown = (event: KeyboardEvent) => {
         if (event.key === 'c') {
            setDots([]); // Clear positions
         }
      };

      window.addEventListener('mousedown', handleMouseDown);
      window.addEventListener('keydown', handleKeyDown);

      const animate = () => {
         requestAnimationFrame(animate);
         controls.update();
         renderer.render(scene, camera);
      };

      animate();

      return () => {
         window.removeEventListener('mousedown', handleMouseDown);
         window.removeEventListener('keydown', handleKeyDown);
         mount.removeChild(renderer.domElement);
      };
   }, [isDrawingMode, cameraPosition, cameraRotation]);

   const resetCanvas = () => {
      pointsRef.current.forEach(dot => scene.remove(dot)); // Remove all dots
      pointsRef.current = []; // Clear dots reference
      linesRef.current.forEach(line => scene.remove(line)); // Remove all lines
      linesRef.current = []; // Clear lines reference
      setSelectedDots([]); // Reset selection
   };

   const toggleMode = () => {
      if (camera) {
         setCameraPosition(camera.position.clone());
         setCameraRotation(camera.rotation.clone());
      }

      if (isDrawingMode) {
         resetCanvas(); // Reset canvas when switching to drawing mode
      }

      setIsDrawingMode((prev) => !prev);

      if (controls) {
         controls.enabled = !isDrawingMode;
      }
   };

   return (
      <div>
         {isLoading && (
            <div className='absolute inset-0 flex items-center justify-center bg-black bg-opacity-70'>
               <p className='text-white text-1xl'>Loading Image...</p>
            </div>
         )}

         <button className="p-[3px] absolute top-5 left-5 z-10 bg-white  rounded-md" onClick={toggleMode}>
            <div className="absolute inset-0 bg-gradient-to-r from-sky-500 to-blue-500 rounded-lg" />
            <div className="px-4 py-2 bg-black rounded-[6px]  relative group transition duration-200 text-white hover:bg-transparent">
               Clean Palette
            </div>
         </button>

         <button onClick={home} className='absolute right-5 top-5 border border-blue-500 rounded-full p-2'>
            <HomeIcon className='w-7 h-7 text-white' />
         </button>

         <div
             className='absolute bottom-5 right-10 z-10 text-white flex flex-col bg-black border border-blue-500 rounded-lg p-4 text-sm bg-opacity-70 gap-3'>
            <div className='flex flex1 flex-row gap-3 items-center'>
               <LeftMouse className='w-5 h-5'/>
               <p className='flex flex-1'>Move Camera</p>
            </div>

            <div className='flex flex1 flex-row gap-3 items-center'>
               <RightMouse className='w-5 h-5'/>
               <p className='flex flex-1'>Create and click-back to connect</p>
            </div>

            <div className='flex flex1 flex-row gap-3 items-center'>
               <div className=' px-1 border rounded-md'>
                  <h3 className='text-lg'>C</h3>
               </div>

               <p className='flex flex-1'>Create new constellation</p>
            </div>
         </div>

         <div ref={mountRef} style={{width: '100%', height: '100vh'}}/>
      </div>
   );


}