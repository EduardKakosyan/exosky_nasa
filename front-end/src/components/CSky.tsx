import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { FontLoader } from 'three/examples/jsm/loaders/FontLoader.js';
import { TextGeometry } from 'three/examples/jsm/geometries/TextGeometry.js';

export function CSky() {
   const imageSrc: string = 'sky_image.png';
   const mountRef = useRef<HTMLDivElement>(null);
   const [camera, setCamera] = useState<THREE.PerspectiveCamera | null>(null);
   const [controls, setControls] = useState<OrbitControls | null>(null);
   const [isDrawingMode, setIsDrawingMode] = useState<boolean>(false);
   const [canCreateDot, setCanCreateDot] = useState<boolean>(false);
   const [cameraPosition, setCameraPosition] = useState<THREE.Vector3>(new THREE.Vector3(150, 0, 40));
   const [cameraRotation, setCameraRotation] = useState<THREE.Euler>(new THREE.Euler(0, 0, 0));
   const scene = new THREE.Scene();
   const planetXTextMeshRef = useRef<THREE.Mesh | null>(null);
   const planetYTextMeshRef = useRef<THREE.Mesh | null>(null);
   const pointsRef = useRef<THREE.Vector3[]>([]);
   const linesRef = useRef<THREE.Line[]>([]);

   useEffect(() => {
      // Set up camera and renderer
      const mount = mountRef.current!;
      const camera = new THREE.PerspectiveCamera(75, mount.clientWidth / mount.clientHeight, 0.1, 2000);
      const renderer = new THREE.WebGLRenderer({ alpha: true });
      renderer.setSize(mount.clientWidth, mount.clientHeight);
      mount.appendChild(renderer.domElement);

      // Create sky background
      const geometry = new THREE.SphereGeometry(500, 64, 32);
      geometry.scale(-1, 1, 1);
      const texture = new THREE.TextureLoader().load(imageSrc);
      const material = new THREE.MeshBasicMaterial({ map: texture, side: THREE.DoubleSide });
      const sphere = new THREE.Mesh(geometry, material);
      scene.add(sphere);

      // Create two planets (PlanetX and PlanetY)
      const planetGeometry = new THREE.SphereGeometry(10, 10, 10);
      const planetXMaterial = new THREE.MeshBasicMaterial({ color: 'red' });
      const planetYMaterial = new THREE.MeshBasicMaterial({ color: 'blue' });

      const planetX = new THREE.Mesh(planetGeometry, planetXMaterial);
      const planetY = new THREE.Mesh(planetGeometry, planetYMaterial);

      planetX.position.set(-470, 0, -50);
      planetY.position.set(-450, 50, 150);

      scene.add(planetX);
      scene.add(planetY);

      camera.position.copy(cameraPosition);
      camera.rotation.copy(cameraRotation);

      // Set up OrbitControls
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

      // Create text mesh for PlanetX and PlanetY
      const createTextMesh = (text: string, position: THREE.Vector3, ref: React.MutableRefObject<THREE.Mesh | null>) => {
         const loader = new FontLoader();
         loader.load('/myFont.json', (font) => {
            const textGeometry = new TextGeometry(text, {
               font: font,
               size: 10,
               depth: 1,
               curveSegments: 12,
               bevelEnabled: false,
            });
            const textMaterial = new THREE.MeshBasicMaterial({ color: 'white' });
            const textMesh = new THREE.Mesh(textGeometry, textMaterial);

            textMesh.position.copy(position);
            textMesh.rotateY(20);
            scene.add(textMesh);

            textMesh.visible = false; 
            ref.current = textMesh;
         });
      };

      createTextMesh("Planet X", new THREE.Vector3(-470, 0, -60), planetXTextMeshRef);
      createTextMesh("Planet Y", new THREE.Vector3(-450, 50, 140), planetYTextMeshRef);

      const handleHover = (event: MouseEvent) => {
         mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
         mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

         raycaster.setFromCamera(mouse, camera!);
         const intersects = raycaster.intersectObjects([planetX, planetY]);

         if (intersects.length > 0) {
            const intersectedObject = intersects[0].object;

            if (intersectedObject === planetX && planetXTextMeshRef.current) {
               planetXTextMeshRef.current.visible = true;
               if (planetYTextMeshRef.current) planetYTextMeshRef.current.visible = false;
            } else if (intersectedObject === planetY && planetYTextMeshRef.current) {
               planetYTextMeshRef.current.visible = true;
               if (planetXTextMeshRef.current) planetXTextMeshRef.current.visible = false;
            }
         } else {
            if (planetXTextMeshRef.current) planetXTextMeshRef.current.visible = false;
            if (planetYTextMeshRef.current) planetYTextMeshRef.current.visible = false;
         }
      };

      const createDot = (position: THREE.Vector3) => {
         const dotGeometry = new THREE.SphereGeometry(5, 32, 32);
         const dotMaterial = new THREE.MeshBasicMaterial({ color: 'white' });
         const dot = new THREE.Mesh(dotGeometry, dotMaterial);

         dot.position.copy(position);
         scene.add(dot);
      };

      const createLine = (point1: THREE.Vector3, point2: THREE.Vector3) => {
         const material = new THREE.LineBasicMaterial({ color: 'white' });
         const points = [point1, point2];
         const geometry = new THREE.BufferGeometry().setFromPoints(points);
         const line = new THREE.Line(geometry, material);

         scene.add(line);
         linesRef.current.push(line);
      };

      const updateLine = () => {
         const points = pointsRef.current;

         if (points.length >= 2) {
            const lastPoint = points[points.length - 1];
            const secondLastPoint = points[points.length - 2];

            createLine(secondLastPoint, lastPoint);
         }
      };

      const handleClick = (event: MouseEvent) => {
         const target = event.target as HTMLElement;
         if (target.tagName.toLowerCase() === 'button') return;

         mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
         mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

         raycaster.setFromCamera(mouse, camera!);
         raycaster.far = 1000;

         const intersects = raycaster.intersectObjects([sphere], false);

         if (intersects.length > 0) {
            const intersectedPoint = intersects[0].point.clone();

            if (isDrawingMode && canCreateDot) {
               createDot(intersectedPoint);
               pointsRef.current.push(intersectedPoint);
               updateLine();
            } else {
               if (intersects[0].object === planetX) {
                  planetX.material.color.set('yellow');
               } else if (intersects[0].object === planetY) {
                  planetY.material.color.set('yellow');
               }
            }
         } else {
            console.log('No intersection');
         }
      };

      window.addEventListener('mousemove', handleHover);
      window.addEventListener('click', handleClick);

      const animate = () => {
         requestAnimationFrame(animate);
         controls.update();

         if (planetXTextMeshRef.current) {
            planetXTextMeshRef.current.lookAt(camera!.position);
         }
         if (planetYTextMeshRef.current) {
            planetYTextMeshRef.current.lookAt(camera!.position);
         }

         renderer.render(scene, camera);
      };

      animate();

      return () => {
         window.removeEventListener('mousemove', handleHover);
         window.removeEventListener('click', handleClick);
         mount.removeChild(renderer.domElement);
      };
   }, [isDrawingMode, canCreateDot, cameraPosition, cameraRotation]);

   // Function to reset the canvas
   const resetCanvas = () => {
      pointsRef.current = []; // Clear points
      linesRef.current.forEach(line => scene.remove(line)); // Remove all lines from the scene
      linesRef.current = []; // Clear lines reference
   };

   const toggleMode = () => {
      if (camera) {
         setCameraPosition(camera.position.clone());
         setCameraRotation(camera.rotation.clone());
      }

      if (isDrawingMode) {
         resetCanvas(); // Reset canvas when switching to drawing mode
      }

      setIsDrawingMode((prev) => {
         const newMode = !prev;
         setCanCreateDot(newMode);
         return newMode;
      });

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
