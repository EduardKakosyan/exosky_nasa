import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export function CSky() {
   const imageSrc: string = 'sky_image.png';
   const mountRef = useRef<HTMLDivElement>(null);
   const [camera, setCamera] = useState<THREE.PerspectiveCamera | null>(null);
   const [controls, setControls] = useState<OrbitControls | null>(null);
   const [isDrawingMode, setIsDrawingMode] = useState<boolean>(false);
   const [selectedDots, setSelectedDots] = useState<THREE.Mesh[]>([]); // Track selected dots for line creation
   const [cameraPosition, setCameraPosition] = useState<THREE.Vector3>(new THREE.Vector3(150, 0, 40));
   const [cameraRotation, setCameraRotation] = useState<THREE.Euler>(new THREE.Euler(0, 0, 0));
   const scene = new THREE.Scene();
   const pointsRef = useRef<THREE.Mesh[]>([]); // Store dots as meshes
   const linesRef = useRef<THREE.Line[]>([]);

   useEffect(() => {
      const mount = mountRef.current!;
      const camera = new THREE.PerspectiveCamera(75, mount.clientWidth / mount.clientHeight, 0.1, 2000);
      const renderer = new THREE.WebGLRenderer({ alpha: true });
      renderer.setSize(mount.clientWidth, mount.clientHeight);
      mount.appendChild(renderer.domElement);

      const geometry = new THREE.SphereGeometry(500, 64, 32);
      geometry.scale(-1, 1, 1);
      const texture = new THREE.TextureLoader().load(imageSrc);
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
      controls.maxDistance = 500;

      setCamera(camera);
      setControls(controls);

      const raycaster = new THREE.Raycaster();
      const mouse = new THREE.Vector2();

      // Function to create a dot
      const createDot = (position: THREE.Vector3) => {
         const dotGeometry = new THREE.SphereGeometry(5, 32, 32);
         const dotMaterial = new THREE.MeshBasicMaterial({ color: 'white' });
         const dot = new THREE.Mesh(dotGeometry, dotMaterial);

         dot.position.copy(position);
         scene.add(dot);
         pointsRef.current.push(dot);
      };

      // Function to create a line between two dots
      const createLineBetweenDots = (dot1: THREE.Mesh, dot2: THREE.Mesh) => {
         const material = new THREE.LineBasicMaterial({ color: 'white' });
         const points = [dot1.position, dot2.position];
         const geometry = new THREE.BufferGeometry().setFromPoints(points);
         const line = new THREE.Line(geometry, material);
         scene.add(line);
         linesRef.current.push(line);
      };

      const handleMouseDown = (event: MouseEvent) => {
         // Check if we are in drawing mode
         if (!isDrawingMode) return; // If not in drawing mode, ignore the event
      
         // Check for right-click (button 2)
         if (event.button === 2) {
            event.preventDefault(); // Prevent the context menu
      
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
      
            raycaster.setFromCamera(mouse, camera!);
            raycaster.far = 1000;
      
            const intersects = raycaster.intersectObjects([...pointsRef.current, sphere]);
      
            if (intersects.length > 0) {
               const intersectedObject = intersects[0].object;
      
               // If a dot is clicked, select it for line creation
               if (pointsRef.current.includes(intersectedObject as THREE.Mesh)) {
                  const clickedDot = intersectedObject as THREE.Mesh;
      
                  setSelectedDots((prevSelectedDots) => {
                     if (prevSelectedDots.includes(clickedDot)) {
                        return prevSelectedDots; // Ignore if already selected
                     }
                     const newSelectedDots = [...prevSelectedDots, clickedDot];
                     if (newSelectedDots.length === 2) {
                        // Create a line between the two selected dots
                        createLineBetweenDots(newSelectedDots[0], newSelectedDots[1]);
                        return []; // Reset selection after creating the line
                     }
                     return newSelectedDots;
                  });
               } 
               // If the sphere is clicked (empty space), create a dot
               else if (intersectedObject === sphere) {
                  const intersectedPoint = intersects[0].point.clone();
                  createDot(intersectedPoint);
               }
            }
         }
      };
      

      window.addEventListener('mousedown', handleMouseDown);

      const animate = () => {
         requestAnimationFrame(animate);
         controls.update();
         renderer.render(scene, camera);
      };

      animate();

      return () => {
         window.removeEventListener('mousedown', handleMouseDown);
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
         <button onClick={toggleMode} style={{ position: 'absolute', top: '10px', left: '10px', zIndex: 10, backgroundColor: 'white' }}>
            {isDrawingMode ? 'Switch to Camera Mode' : 'Switch to Drawing Mode'}
         </button>
         <div ref={mountRef} style={{ width: '100%', height: '100vh' }} />
      </div>
   );
}
