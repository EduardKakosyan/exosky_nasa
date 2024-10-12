import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { createDot, createLine } from './draw';

type Params ={
   imageSrc: string;
   scene: THREE.Scene;
   mountRef: React.RefObject<HTMLDivElement>;
   cameraPosition: THREE.Vector3;
   cameraRotation: THREE.Euler;
   pointsRef: React.MutableRefObject<THREE.Mesh[]>;
   linesRef: React.MutableRefObject<THREE.Line[]>;
   setDots: React.Dispatch<React.SetStateAction<THREE.Vector3[]>>;
   setIsLoading: React.Dispatch<React.SetStateAction<boolean>>;
   setCamera: React.Dispatch<React.SetStateAction<THREE.PerspectiveCamera | null>>;
};


export function createSky({ 
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
}: Params) 

{
   // Create the renderer, camera, and sphere
   const mount = mountRef.current!;
   const camera = new THREE.PerspectiveCamera(75, mount.clientWidth / mount.clientHeight, 0.1, 2000);
   const renderer = new THREE.WebGLRenderer({ alpha: true });
   renderer.setSize(mount.clientWidth, mount.clientHeight);
   mount.appendChild(renderer.domElement);

   // Create the sphere with the image texture will be the sky
   const geometry = new THREE.SphereGeometry(500, 64, 32);
   geometry.scale(-1, 1, 1);
   const textureLoader = new THREE.TextureLoader();
   const texture = textureLoader.load(imageSrc, () => {
      setIsLoading(false); 
   });
   const material = new THREE.MeshBasicMaterial({ map: texture, side: THREE.DoubleSide });
   const sphere = new THREE.Mesh(geometry, material);
   scene.add(sphere);

   // Set the camera based on the params
   camera.position.copy(cameraPosition);
   camera.rotation.copy(cameraRotation);

   // Create the orbit controls
   const controls = new OrbitControls(camera, renderer.domElement);
   controls.enableDamping = true;
   controls.dampingFactor = 0.5;
   controls.enableZoom = true;
   controls.zoomSpeed = 2;
   controls.minDistance = 1;
   controls.maxDistance = 400;

   controls.mouseButtons = {
      LEFT: THREE.MOUSE.LEFT,
      MIDDLE: THREE.MOUSE.MIDDLE,
      RIGHT: null
   };

   setCamera(camera);


   // Create Raycaster and mouse for right-click listener
   // Will create dots and lines to connects stars
   const raycaster = new THREE.Raycaster();
   const mouse = new THREE.Vector2();


   // Right click listener to create dots and lines
   function handleMouseDown(event: MouseEvent) {
      // Check for right-click (button 2)
      if (event.button === 2) {
         event.preventDefault(); // Prevent the context menu

         // Get the mouse position
         mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
         mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

         // Get the intersection point with the sphere
         raycaster.setFromCamera(mouse, camera!);
         raycaster.far = 1000;

         // Check for intersections
         const intersects = raycaster.intersectObject(sphere);

         // If there is an intersection, create a dot
         if (intersects.length > 0) {
            const intersectedPoint = intersects[0].point.clone();
            createDot(intersectedPoint, scene, pointsRef);

            setDots((prevDots) => {
               // If there is a previous dot, create a line between the two dots
               if (prevDots.length === 1) {
                  createLine(prevDots[0], intersectedPoint, scene, linesRef);
                  return [intersectedPoint];
               } 
               
               else {
                  return [intersectedPoint];
               }
            });
         }
      }
   };


   // Keyboard listener to clear the canvas
   function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'c' || event.key === 'C') {
         setDots([]); // Clear positions
      }
   };


   // Add event listeners
   window.addEventListener('mousedown', handleMouseDown);
   window.addEventListener('keydown', handleKeyDown);


   // Animation loop
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
}